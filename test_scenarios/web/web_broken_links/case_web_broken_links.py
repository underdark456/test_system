import time
from urllib.parse import urlparse, urljoin

from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException, \
    ElementNotInteractableException, MoveTargetOutOfBoundsException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT

options_path = 'test_scenarios.web.web_broken_links'
backup_name = 'case_web_broken_links.txt'
_wait_time_out = 1


class WebBrokenLinksCase(CustomTestCase):
    """Test that all links and most buttons do not cause 404 or 400"""
    __author__ = 'dkudryashov'
    __version__ = '0.1'
    __execution_time__ = 3050
    __express__ = True

    visited_links = []
    clicked_buttons = []  # clicked buttons are saved as current url + button id + button name
    buttons = []
    paths = []
    BUTTONS_ID_TO_SKIP = [
        'logout',
        '',
        'submitFirst',
        # 'backFirst',
        'deleteFirst',
        'tree_filters',
        'save_config',
        'save_config_as',
        'load_config',
        'load_backup',
        'restart_nms',
        'shutdown',
        'reboot',
        # 'clone',
    ]
    status_code_number = 0
    getting_back = 0
    exception_in_getting_back = 0
    skip_experimental = OptionsProvider.get_system_options(options_path).get('skip_experimental', True)

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, CHROME_CONNECT), driver_id='case_web_broken_links'
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_connection(options_path)
        cls.nms_path = cls.options.get('address')
        cls.internal_urls = set()
        cls.external_urls = set()
        cls.links_with_buttons = set()
        cls.clicked_buttons = set()
        cls.next_screenshot_num = 0

    def test_logout(self):
        """Simple logout test (logout do not cause 404 or 400)"""
        web_options = OptionsProvider.get_connection(options_path, CHROME_CONNECT)
        web_driver = DriversProvider.get_driver_instance(
            web_options,
            driver_id='web_broken_links_case_test_logout',
            store_driver=False
        )
        web_driver.driver.get(self.nms_path)
        web_driver.logout()
        self._wait_load_page()
        with self.subTest('Logout link'):
            self.assertFalse(self._is_404())
        del web_driver

    def test_all_links(self):
        """Recursively test all links in NMS and make sure that they are not 404 or 400"""
        # Links from the tree are not tested.
        # Buttons with no ID and having one of the ids 'logout', 'submitFirst', 'backFirst', 'deleteFirst',
        # 'tree_filters', 'save_config', 'save_config_as', 'load_config', 'load_backup', 'restart_nms',
        # 'shutdown', and 'reboot' are not tested.

        self.crawl(self.nms_path + 'object/dashboard/nms=0', buttons=False)
        for btn_link in self.links_with_buttons:
            self._buttons(btn_link)

    def _buttons(self, btn_link, recursion_depth=0):
        if recursion_depth > 50:
            self.error(f'Button test recursion depth {recursion_depth}')
        self.driver.driver.get(btn_link)
        self._wait_load_page()
        time.sleep(1)

        for btn in self.driver.driver.find_elements_by_tag_name("button"):
            try:
                btn_id = btn.get_attribute('id')
                btn_txt = btn.text.lower()
            except StaleElementReferenceException:
                continue
            btn_test_name = f'{btn_link}.{btn_id}.{btn_txt}'
            if btn_test_name in self.clicked_buttons:
                continue
            # Some buttons are skipped and checked in another test
            if btn_id in self.BUTTONS_ID_TO_SKIP and not btn_txt == 'new':
                continue
            print(btn_test_name)
            self.clicked_buttons.add(btn_test_name)
            try:
                ActionChains(self.driver.driver).move_to_element(btn).perform()
                btn.click()
                # self.driver.screenshot(f'case_web_broken_links_{self.next_screenshot_num}.png')
                self.next_screenshot_num += 1
            except ElementClickInterceptedException as exc:
                res = self.driver.screenshot(f'case_web_broken_links_stale1.png')
                self.info(f'Screenshot {res}')
                self.info(f'Element {btn_test_name}')
                # raise exc
            except ElementNotInteractableException as exc:
                res = self.driver.screenshot(f'case_web_broken_links_not_interactable.png')
                self.info(f'Screenshot {res}')
                self.info(f'Element {btn_test_name}')
                # raise exc
            except MoveTargetOutOfBoundsException as exc:
                res = self.driver.screenshot(f'case_web_broken_links_move_target_out.png')
                self.info(f'Screenshot {res}')
                self.info(f'Element {btn_test_name}')
            self._wait_load_page()

            if self._is_404():
                with self.subTest(f'404 button id={btn_id} text={btn_txt} at {btn_link}'):
                    self.assertFalse(True)

            elif self._is_400():
                with self.subTest(f'400 button id={btn_id} text={btn_txt} at {btn_link}'):
                    self.assertFalse(True)

            else:
                # Button click leads to another page
                current_url = self.driver.get_current_url()
                if current_url != btn_link:
                    self.dbg(f'Button id={btn_id} text={btn_txt} at {btn_link} leads to {current_url}')
                    recursion_depth += 1
                    self._buttons(btn_link, recursion_depth)
                else:
                    self.dbg(f'Button id={btn_id} text={btn_txt} at {btn_link} is not a link button')
        recursion_depth -= 1

    def crawl(self, url, recursion_depth=0, buttons=False):
        if recursion_depth > 100:
            self.error(f'Recursion depth reached {recursion_depth}')
            return
        links = self.get_all_page_links(url)
        for link in links:
            recursion_depth += 1
            self.crawl(link, recursion_depth, buttons=buttons)
        recursion_depth -= 1

    def get_all_page_links(self, url):
        """
        The method gets all non-empty anchor tags in the page, determines if they are internal links or external links.
        The new unique links are added to the corresponding sets.
        If there are buttons in the page, the page is added to the corresponding set.

        :returns set urls: a set containing all new unique urls
        """
        urls = set()
        domain_name = urlparse(url).netloc
        current_url = self.driver.get_current_url()
        self.driver.driver.get(url)
        self._wait_load_page()
        time.sleep(1)

        for btn in self.driver.driver.find_elements_by_tag_name("button"):
            try:
                btn_id = btn.get_attribute('id')
                btn_txt = btn.text.lower()
            except StaleElementReferenceException:
                continue
            # Some buttons are skipped and checked in another test
            if btn_id in self.BUTTONS_ID_TO_SKIP and not btn_txt == 'new':
                continue
            self.links_with_buttons.add(url)
            break

        if self._is_404():
            with self.subTest(f'404 {url} at {current_url}'):
                self.assertFalse(True)
            return urls
        if self._is_400():
            with self.subTest(f'400 {url} at {current_url}'):
                self.assertFalse(True)
        for a_tag in self.driver.driver.find_elements_by_tag_name("a"):
            href = a_tag.get_attribute('href')
            if href is None:  #
                # print(a_tag.get_attribute('innerHTML'), a_tag.text)
                continue
            elif href == '':
                with self.subTest(url):
                    self.fail(f'Empty href at {url}')
            elif href.find('undefined=undefined') != -1:
                with self.subTest(url):
                    self.fail(f'href={href}')
            elif href.find('dbeditor') != -1:
                continue
            href = urljoin(url, href)  # joining URL if it is relative
            parsed_href = urlparse(href)
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path  # removing URL GET params
            if not self._is_valid_url(href):
                with self.subTest(url):
                    self.fail(f'Not valid href at {url}')
            if href in self.internal_urls:
                continue
            # If it is an external link
            if domain_name not in href:
                if href not in self.external_urls:
                    self.dbg(f'External link: {href} at {current_url}')
                    self.external_urls.add(href)
                continue
            self.dbg(f'Internal link: {href} at {current_url}')
            self.internal_urls.add(href)
            urls.add(href)
        return urls

    @staticmethod
    def _is_valid_url(url):
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    def _is_404(self):
        return self.driver.get_current_url().find('notfound') != -1

    def _is_400(self):
        return self.driver.get_current_url().find('badrequest') != -1

    def _wait_load_page(self):
        WebDriverWait(self.driver.driver, _wait_time_out) \
            .until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'body')))
