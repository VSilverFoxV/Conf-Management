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

# Временная фун-я для теста
def test():
    # Строка для тестирования
    src = '''
    a = 8
    b = (list 1 #[a] 3 4 5)
    vm = {
        IP => (list 192 168 #[b] 44),
        memory => 1024,
    }
    str = @"Цветочки"
    test = #[str]
    '''
    s = parse(src, main) # результат парсинга через `peco`
    print(s.ok) # Всё ли окей
    print(s.stack) # Вывод стека того, что было обработано

test()