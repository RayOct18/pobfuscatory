def add(x, y):
    return x + y


def equal_inline(a, b):
    return add(x=a, y=b)


def unpack_list():
    l = list(range(5))
    a1, b1, c1, *d1 = l
    return a1, b1, c1, d1


def dynamic_args(*args, **kwargs):
    return args, kwargs
