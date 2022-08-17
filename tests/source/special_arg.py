

def add(x, y):
    return x + y


def equal_inline(a, b):
    return add(x=a, y=b)


def unpack_list():
    l = list(range(5))
    a, b, c, *d = l
    return a, b, c, d


def dynamic_args(*args, **kwargs):
    return args, kwargs
