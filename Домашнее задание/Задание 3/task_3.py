from peco.peco import *

# Обработка чисел
mknum = to(lambda n: float(n))
mkarr = to(lambda a: list(a))
mkobj = to(lambda o: dict(o))

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

const = group(seq(name, skip(r'='), val))

obj = seq(skip(r'\['), group(many(seq(item, skip(r',')))), skip(r'\]'), mkobj)

val = alt(num, array, obj)

main = seq(group(many(const)), ws, mkobj)

def test():
    src = '''
    a = 8
    b = (list 1 2 3 4 5)
    vm = [
        IP => (list 192 168 44 44),
        memory => 1024,
    ]
    '''
    s = parse(src, main)
    print(s.ok)
    print(s.stack)

test()