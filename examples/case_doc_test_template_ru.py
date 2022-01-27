from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.abstract_http_driver import AbstractHttpDriver
from src.drivers.drivers_provider import DriversProvider
from src.options_providers.options_provider import OptionsProvider

# имя пакета из которого нужно извлечь набор параметров
# состоит из имен директорий относительно корня проекта разделенные точками
# например для текущей директории 'examples'
# или 'test_scenarios.creating_objects.routing_objects' пример из существующих тестов роутинга
options_path = 'examples'


# имя набора тестов
# имя файла в формате case_your_case_name.py
# имя класса YourCaseNameCase
# всегда наследуется от CustomTestCase
class DocTestTemplateCase(CustomTestCase):
    # это docstring. Инструмент документирования python
    # команда  'python print_tests_list.py' выведет в консоль список всех тестов и содержимое docstring
    """Описание набора тестов. Для чего предназначены или что делают.
    Мне кажется разумным фиксировать здесь объяснения почему должно работать именно так, а не иначе.
    Краткая документация.
    """

    @classmethod
    def set_up_class(cls):
        """
        Метод АВТОМАТИЧЕСКИ вызываемый один раз перед запуском всех тестов в данном модуле.
        Вызывается один раз вне зависимости от количества исполняющихся тестов набора.
        Декоратор @classmethod является обязательным!
        Можно не описывать если не нужен.
        """
        # Инициализация драйвера. Всегда выглядит так.
        # Драйвер нужен только если в тестах используются обертки сущностей НМС.
        # Например Controller, Vno, Shaper (все они лежат в src/nms_entities/basic_entities)
        cls.driver = DriversProvider.get_driver_instance(
            # извлечение параметров драйвера
            # по умолчанию описаны в global_options в словаре system
            OptionsProvider.get_connection()
        )
        # Инструмент работы с бекапами НМС
        backup = BackupManager()
        # apply_backup загрузит файл 'backup.txt' из директории nms_backups в НМС
        backup.apply_backup('backup.txt')
        # Так же можно сохранить текущее состояние НМС в файл 'new_backup.txt'
        backup.create_backup('new_backup.txt')

        cls.some_param = 'Можно создавать произвольные свойства'

    def set_up(self) -> None:
        """
        Данный метод вызывается АВТОМАТИЧЕСКИ ПЕРЕД каждым тестом из набора.
        Можно не описывать если не нужен.
        """
        pass

    # Пример теста
    # Имя теста всегда начинается с test_ слова разделяются _ (underscore)
    # Описывает что делает тест
    def test_my_best_test(self):
        """Этот тест служит в качестве примера.
        Описание теста объясняет ПОЧЕМУ тот или иной функционал должен работать именно таким образом
        как описывает код теста.
        Не следует здесь описыват ЧТО делает тест - это понятно из кода и названия теста.
        """
        # Пример утверждения.
        # Если утверждение ложно в результат теста выводится сообщение передаваемое параметром
        # Описание ассертов можно посмотреть здесь
        # https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertEqual
        error_message = 'Ложь стала истиной. Видимо мир рухнул!'
        self.assertTrue(True, error_message)

    # Это еще один тест
    # При запуске всего кейса порядок исполнения тестов стоит считать недетерминированным,
    # таким образом нельзя использовать результат одного теста в качестве параметров другого.
    def test_always_fail_example(self):
        """По законам этой вселенной число 42 не может быть эквивалентом строки 'BFG'"""
        self.assertEqual(42, 'BFG', 'Кадия стоит!')

    def test_driver_usage(self):
        """Пример доступа к драйверу"""
        # так так мы инициализировали драйвер в set_up_class
        # и положили его в свойство driver нашего класса
        # мы можем получить к нему доступ из любого теста
        our_driver = self.driver
        # и убедится что это именно наш драйвер в качестве примера еще одного утерждения
        self.assertIsInstance(our_driver, AbstractHttpDriver, 'Они украли нашу прелесть!')

    # из тестов можно вызывать любые функции
    def test_use_custom_function(self):
        # это пример функции описанной в текущем классе (метод)
        # если имя не начинается с test_ система обнаружения тестов его проигнорирует
        self_result = self.custom_function()
        result_message = 'Можно создавать произвольные свойства'
        msg = F'custom_function сломали. Должна всегда возвращать строку "{result_message}"'
        self.assertEqual(self_result, result_message, msg)

        # пример функции описонной в текущем файле.
        custom_result = free_function()
        self.assertIsNotNone(1, custom_result)

        # пример вызова функции импортированной из другого файла
        from examples.shared_functions import shared_function_example
        shared_result = shared_function_example()
        self.assertIsNotNone(1, shared_result)

    def custom_function(self):
        # some_param мы так же определили в set_up_class
        return self.some_param

    def tear_down(self) -> None:
        """
        Данный метод вызывается АВТОМАТИЧЕСКИ ПОСЛЕ каждого теста из набора
        Можно не описывать если не нужен.
        """
        pass

    @classmethod
    def tear_down_class(cls) -> None:
        """
        Данный метод вызывается АВТОМАТИЧЕСКИ ПОСЛЕ ПОСЛЕДНЕГО выполненного теста.
        Декоратор @classmethod является обязательным!
        Можно не описывать если не нужен.
        """
        pass


# Обратите внимание! В декларировании обычных функции отсутствует отступы как у методов.
def free_function():
    return 'Free function'
