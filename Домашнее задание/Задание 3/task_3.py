from peco.peco import *

# Глобальный словарь для хранения значений переменных
variables = {}

# Обработка чисел, массивов, объектов (словарей) и строк
mknum = to(lambda n: float(n))
mkarr = to(lambda a: list(a))
mkobj = to(lambda o: dict(o))
mkstr = to(lambda s: str(s))

# Обработка определения константных переменных
def assign_const(n_v):
    variables[n_v[0]] = n_v[1]
    return n_v  # Возвращаем значение, чтобы оно добавилось в стек

mkAssign = to(assign_const)

# Обработка константных выражений
def constRes(name):
    # Получение значения переменной из глобального словаря
    if name not in variables:
        raise NameError(f"Variable '{name}' is not defined.")
    
    return variables[name]

mkConstRes = to(constRes)

# Обработка лишних пробелов, включая обработку комментариев
ws = many(eat(r'\s+'))

# Сканирование кода, повышающее производительность вычислений
scan = lambda f: memo(seq(ws, f))

# Пропуск того, что передано как аргумент (регулярка)
skip = lambda c: scan(eat(c))

# Кладёт распознанное в стек с помощью cite(*args)
tok = lambda c: scan(cite(eat(c)))

num = seq(tok(r'[-+]?\d+'), mknum)
name = tok(r'[a-zA-Z][a-zA-Z0-9]*')

val = lambda s: val(s)

array = seq(skip(r'\(list'), group(many(val)), skip(r'\)'), mkarr)

item = group(seq(name, skip(r'=>'), val))

const = seq(group(seq(name, skip(r'='), val)), mkAssign)

obj = seq(skip(r'{'), group(many(seq(item, skip(r',')))), skip(r'}'), mkobj)

string = seq(skip(r'@\"'), tok(r'[^"]*'), skip(r'\"'), mkstr)

constExpr = seq(skip(r'#\['), name, skip(r'\]'), mkConstRes)

val = alt(num, string, array, obj, constExpr)

main = seq(group(many(const)), ws, mkobj)

def test():
    src = '''
    a = 8
    b = (list 1 2 3 4 5)
    vm = {
        IP => (list 192 168 44 44),
        memory => 1024,
    }
    str = @"ASS"
    test = #[a]
    '''
    s = parse(src, main)
    print(s.ok)
    print(s.stack)

test()