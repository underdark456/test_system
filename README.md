вызвать в корне проекта `pip install` - для установки зависимостей
 
- NMS сущности живут в `src.nms_entities.basic_entities`
- В `srs.enum_types_constants` enum подобные наборы значений параметров (представленные выпадающими списками в ГУИ)
- В `src.values_presenters` полезные обертки для range() и типовые итерируемые наборы данных
- В `examples` шаблоны для копипасты и описаниями работы

Доступ к системе конфигурационных файлов осуществляется через `src.options_providers.options_provider`,
документация там же.


`python print_tests_list.py` - выдаст список всех имеющихся тестов с их docstring
`python -m pydoc -b` - show documentation in web browser