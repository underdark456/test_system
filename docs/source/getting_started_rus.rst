Начало работы
=============

Тестовая система представляет собой набор программных средств для тестирования возможностей NMS и спутниковых модемов UHP.
На данный момент использование тестовой системы ограничено локальной копией.

Содержание:
    :ref:`Локальное использование`

    :ref:`Архитектура тестовой системы`

    :ref:`Алгоритм создания простого тестового сценария`

    :ref:`Детальное описание шаблона простого тестового сценария`

    :ref:`Запуск тестового сценария`

    :ref:`Результаты тестового сценария`

Локальное использование
+++++++++++++++++++++++

.. important::
    - ОС Linux (рекомендуется) или Windows
    - Python 3.6 и выше
    - Mercurial Distributed SCM 5.3.1 и выше

Установка тест системы возможна из репозитария Mercurial:

.. code-block::

    hg clone http://10.0.0.16:5000

----------------------------------

Для корректной работы системы из консоли необходимо добавить путь к тестовой системе в переменную окружения `PYTHONPATH`:

    - OS Windows: My Computer -> Properties -> Advanced System Settings -> Environment Variables >
    - OS LINUX: добавить строку `export PYTHONPATH=<путь/до/test_system>` в `~/.bashrc` или `/etc/profile`

----------------------------------

Тест-кейсы, использующие пакет scapy (снифер, генератор пакетов), в Linux необходимо запускать или от имени суперпользователя, например

.. code-block:: bash

    sudo python3 -m unittest case_sample_test_case

или дать интерпретатору Python следующие привелегии: CAP_NET_ADMIN и CAP_NET_RAW.
Для этого необходимо выполнить следующую команду:

.. code-block:: bash

    sudo setcap cap_net_admin,cap_net_raw,cap_net_bind_service+eip $(readlink -f $(which python3))

после чего тест-кейсы можно запускать без sudo.

В Windows такие кейсы будут запрашивать разрешение на исполнение.

------------------------------------

Сконфигурировать файл глобальных локальных опций для определения адреса НМС и ряда других параметров.
Для этого создать в `test_system.global_options` файл с именем `local_options.py`. Пример конфигурации в :doc:`test_system.global_options.local_options_example`
Подробнее об опциях рассказано в соответствующем :ref:`разделе. <rst-detail-description-options>`

------------------------------------

.. note::

    Для разработки новых тест-кейсов рекомендуется использовать IDE PyCharm.

Описание работы с IDE PyCharm приводится в соответствующем :ref:`разделе. <rst-detail-description-pycharm>`

В случае использования других IDE, автоматически не предлагающих установку зависимостей проектов Python,
произвести установку всех зависимостей тест системы из файла requirements.txt:

.. code-block:: bash

    python3 -m pip install -r requirements.txt

Архитектура тестовой системы
++++++++++++++++++++++++++++

Тестовая система использует встроенную библиотеку Python Unittest для загрузки и запуска тестов.
Критерием прохождения теста является результат проверки так называемых утверждений библиотеки Unittest.
Методы утверждений можно видеть https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertEqual

.. note::

    Стандартные методы библиотек Unittest такие как setUpClass, tearDownClass, setUp и tearDown переопределены и соответствуют PEP 8:
    set_up_class, tear_down_class, set_up и tear_down соответственно. Их описание приводится в соответствующем :ref:`разделе. <rst-detail-description-case-snippet>`

1. NMS сущности представлены в :doc:`test_system.src.nms_entities.basic_entities`
2. Менеджер бэкапов находится в :doc:`test_system.src.backup_manager`
3. Драйвер взаимодействия с НМС инициализируется через :py:mod:`test_system.src.drivers.drivers_provider`
4. Драйвер взаимодействия с UHP инициализируется через :py:mod:`test_system.src.drivers.uhp.uhp_requests_driver`
5. Ридер конфигурационных файлов :py:mod:`test_system.src.options_providers.options_provider`
6. Тестовые сценарии находятся в :doc:`test_system.test_scenarios`

Алгоритм создания простого тестового сценария
+++++++++++++++++++++++++++++++++++++++++++++

- Создать в директории `test_scenarios` новую директорию с кратким именем, описывающим сценарий.

- Создать в новой директории файл __init__.py и скопировать в него содержимое `test_system.examples.init_copy_paste.py`

.. literalinclude:: ../../examples/init_copy_paste.py
    :language: python

- Создать в этой директории файл с именем `case_имя_сценария.py` и скопировать в него шаблон простого тестового сценария из `test_system.examples.full_copy_paste_template.py`

.. literalinclude:: ../../examples/full_copy_paste_template.py
    :language: python

.. _rst-detail-description-case-snippet:

Детальное описание шаблона простого тестового сценария
++++++++++++++++++++++++++++++++++++++++++++++++++++++

Детальное описание шаблона простого тестового сценария находится в :py:mod:`test_system.examples.case_doc_test_template_ru`

.. literalinclude:: ../../examples/case_doc_test_template_ru.py
    :language: python

Запуск тестового сценария
+++++++++++++++++++++++++

Возможен запуск сценариев как из консоли так и из среды разработки PyCharm.

Запуск из консоли:

.. code-block:: bash

    python3 -m unittest case_имя_сценария

Результаты тестового сценария
+++++++++++++++++++++++++++++

В консоль выводятся исключения, возникающие при выполнении сценариев, например, `assertEqual` при несовпадении ожидаемого и тестируемого параметра выводит:

.. code-block:: bash

    ======================================================================
    FAIL: test_traffic_protection (case_hubless_controller_confirmation.HublessControllerCase) [] (field_name='ctl_key', value='37')
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/dkudryashov/test_system/test_scenarios/form_confirmation/abstract_case.py", line 185, in _test_traffic_protection
        self.assertEqual(value.lower(), uhp_values.get(key, None))
    AssertionError: '37' != '38'
    - 37
    + 38

После всех тестов выводятся общие данные о количестве проведённых тестов,
а также данные по количеству ошибок при попытке запустить тест (errors) и по количеству проваленных тестов (failures).

.. note::

    - errors возникают при исключениях не связанных с группой методов assert библиотеки unittest, например, ValueError
    - failures возникают при исключениях связанных с группой методов assert библиотеки unittest

Пример вывода результата всех тестов:

.. code-block:: bash

    ----------------------------------------------------------------------
    Ran 23 tests in 15.859s

    FAILED (failures=9, errors=1)

Результаты сценария также выводятся в лог файл. Логи хранятся в директории `logs`.
Имя лог файла соответствует следующему шаблону:

`<имя_класса_тестового_сценария>_<ГГГГ>-<ММ>-<ДД>_<ЧЧ>_<ММ>_<СС>.log`

В лог файле присутствуют записи уровня INFO о всех тестах, а также записи уровня CRITICAL для errors и failures

.. note::

    Уровень логирования можно переопределить в опциях в словаре `'system'` по ключу `'logging'`.
    Пример файла `local_options.py` в директории тестового сценария для переопределения уровня логирования:

    .. code-block:: python

        import logging


        system = {
            'logging' : logging.CRITICAL
        }

    При использовании данных опций, в лог файл будут записываться только события уровня CRITICAL









