import argparse
import sys
import yaml
from peco.peco import *

# Глобальный словарь для хранения значений переменных
variables = {}

# Обработка чисел, массивов, объектов (словарей) и строк
mknum = to(lambda n: float(n))
mkarr = to(lambda a: list(a))
mkobj = to(lambda o: dict(o))
mkstr = to(lambda s: str(s))

# [1, 2, 3] -- изменяемый массив
# (1, 2, 3) -- НЕизменяемый массив

# Обработка определения константных переменных
def assign_const(n_v):
    variables[n_v[0]] = n_v[1]
    return n_v  # Возвращаем значение, чтобы оно добавилось в стек

mkAssign = to(assign_const)

# Обработка константных выражений
def constRes(name):
    # Проверка на существование переменной в глобальном словаре
    if name not in variables:
        raise NameError(f"Variable '{name}' is not defined.")
    
    # Получение значения переменной из глобального словаря
    return variables[name]

mkConstRes = to(constRes)

# Обработка лишних пробелов
ws = many(eat(r'\s+'))

# Сканирование кода, повышающее производительность вычислений
scan = lambda f: memo(seq(ws, f))

# Пропуск того, что передано как аргумент (регулярка)
skip = lambda c: scan(eat(c))

# Кладёт распознанное в стек с помощью cite(*args)
tok = lambda c: scan(cite(eat(c)))

# Обработка чисел и имён соответственно
num = seq(tok(r'[-+]?\d+'), mknum)
name = tok(r'[a-zA-Z][a-zA-Z0-9]*')

# Рекурсивная пересылка (заглушки)
val = lambda s: val(s)

# Правило для массивов
array = seq(skip(r'\(list'), group(many(val)), skip(r'\)'), mkarr)

# Правило для элементов словаря
item = group(seq(name, skip(r'=>'), val))

# Правило для определения константных переменных
const = seq(group(seq(name, skip(r'='), val)), mkAssign)

# Правило для объектов (словарей)
obj = seq(skip(r'{'), group(many(seq(item, skip(r',')))), skip(r'}'), mkobj)

# Правило обработки строк
string = seq(skip(r'@\"'), tok(r'[^"]*'), skip(r'\"'), mkstr)

# Правило обработки константных выражений
constExpr = seq(skip(r'#\['), name, skip(r'\]'), mkConstRes)

# Правило обработки значений (варианты типов констант)
val = alt(num, string, array, obj, constExpr)

# Точка входа в программу обработки
main = seq(group(many(const)), ws, mkobj)

# Кастомный Dumper, чтобы отключить оптимизацию с использованием якорей (ссылок (наподобие &id001)) и явно повторять данные в YAML-коде
class NoAliasDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True

# Функция для загрузки и парсинга конфигурационного файла
def parse_file(file_path):
    try:
        src = sys.stdin.read()  # Стандартный ввод с консоли
        s = parse(src, main)  # Стек
        output = ""  # Переменная с выходными данными
        if s.ok:
            result_dict = dict(s.stack[0]) if isinstance(s.stack, tuple) else s.stack  # Преобразование стека (результат работы парсера) к типу "dict" (словарь)
            yaml_output = yaml.dump(result_dict, default_flow_style=False, allow_unicode=True, default_style=None, Dumper=NoAliasDumper)  # Преобразование преобразованного стека в YAML-код
            output = "\n" + yaml_output + "\n"
        else:
            output = "Парсинг не удался."
            print(output)
        with open(file_path, 'w', encoding='utf-8') as f:  # Запись результата парсинга и преобразований в выходной файл
            f.write(output)
    except FileNotFoundError:  # Если пути к файлу не существует
        print(f"Ошибка: Файла '{file_path}' не существует.")
    except Exception as e:  # Отлов остальных ошибок
        print(f"В процессе парсинга возникла ошибка: {e}")

# Точка входа в скрипт
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Программа парсинга конфигурационного языка.")
    parser.add_argument("outputFilePath", help="Путь к файлу-результату парсинга конфигурационного языка.")
    args = parser.parse_args()
    
    # Запуск парсинга файла (ф-ии для загрузки и парсинга конфигурационного файла)
    parse_file(args.outputFilePath)