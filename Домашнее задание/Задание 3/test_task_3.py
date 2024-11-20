import pytest
import yaml
from peco.peco import parse
from task_3 import main, NoAliasDumper

# Функция для парсинга строк напрямую
def parse_config(src):
    s = parse(src, main)
    if s.ok:
        result_dict = dict(s.stack[0]) if isinstance(s.stack, tuple) else s.stack  # Преобразование стека (результат работы парсера) к типу "dict" (словарь)
        return yaml.dump(result_dict, default_flow_style=False, allow_unicode=True, default_style=None, Dumper=NoAliasDumper)  # Преобразование преобразованного стека в YAML-код
    else:
        raise Exception("Парсинг не удался.")

# === Тесты для чисел ===
def test_valid_num():
    src = "Num = 42"
    expected_output = "Num: 42.0\n"
    assert yaml.safe_load(parse_config(src)) == yaml.safe_load(expected_output)

def test_invalid_num():
    src = "Num = invalid_number"
    with pytest.raises(Exception):
        parse_config(src)

# === Тесты для массивов ===
def test_valid_list():
    src = "List = (list 1 2 3 4 5)"
    expected_output = "List:\n- 1.0\n- 2.0\n- 3.0\n- 4.0\n- 5.0\n"
    assert yaml.safe_load(parse_config(src)) == yaml.safe_load(expected_output)

def test_invalid_list():
    src = "List = (list 1 2 three 4 5)"
    with pytest.raises(Exception):
        parse_config(src)

def test_empty_list():
    src = "EmptyList = (list)"
    expected_output = "EmptyList: []\n"
    assert yaml.safe_load(parse_config(src)) == yaml.safe_load(expected_output)

# === Тесты для объектов (словарей) ===
def test_valid_obj():
    src = """
    Vm = {
        Ip => (list 192 168 1 1),
        Memory => 2048,
    }
    """
    expected_output = (
        "Vm:\n"
        "  Ip:\n"
        "  - 192.0\n"
        "  - 168.0\n"
        "  - 1.0\n"
        "  - 1.0\n"
        "  Memory: 2048.0\n"
    )
    assert yaml.safe_load(parse_config(src)) == yaml.safe_load(expected_output)

def test_invalid_obj():
    src = """
    Vm = {
        Ip => (list 192 168 1 one),
        Memory => 2048,
    }
    """
    with pytest.raises(Exception):
        parse_config(src)

def test_empty_dict():
    src = "EmptyDict = {}"
    expected_output = "EmptyDict: {}\n"
    assert yaml.safe_load(parse_config(src)) == yaml.safe_load(expected_output)

# === Тесты для константных выражений ===
def test_valid_const_expr():
    src = """
    Num = 10
    ConstExpr = #[Num]
    """
    expected_output = "Num: 10.0\nConstExpr: 10.0\n"
    assert yaml.safe_load(parse_config(src)) == yaml.safe_load(expected_output)

def test_invalid_const_expr():
    src = """
    Num = 10
    ConstExpr = #[NotDefinedVar]
    """
    with pytest.raises(Exception):
        parse_config(src)

# === Тесты для вложенных структур ===
def test_valid_nested_obj():
    src = """
    Vm = {
        Ip => (list 192 168 1 1),
        Config => {
            CPU => 4,
            RAM => 4096,
        },
    }
    """
    expected_output = (
        "Vm:\n"
        "  Ip:\n"
        "  - 192.0\n"
        "  - 168.0\n"
        "  - 1.0\n"
        "  - 1.0\n"
        "  Config:\n"
        "    CPU: 4.0\n"
        "    RAM: 4096.0\n"
    )
    assert yaml.safe_load(parse_config(src)) == yaml.safe_load(expected_output)

def test_invalid_nested_obj():
    src = """
    Vm = {
        Ip => (list 192 168 1 1),
        Config => {
            CPU => four,
            RAM => 4096,
        },
    }
    """
    with pytest.raises(Exception):
        parse_config(src)

# === Тесты на синтаксические ошибки ===
def test_incorrect_syntax_structure():
    src = """
    Num = 10
    #[Num
    """
    with pytest.raises(Exception):
        parse_config(src)

def test_unclosed_list():
    src = "List = (list 1 2 3"
    with pytest.raises(Exception):
        parse_config(src)

# === Тесты на пробелы и отступы ===
def test_spaces_and_indentation():
    src = "   Num   =   42   "
    expected_output = "Num: 42.0\n"
    assert yaml.safe_load(parse_config(src)) == yaml.safe_load(expected_output)
