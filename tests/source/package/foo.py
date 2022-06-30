from source.package.bar import bar, zoo


def foo(a, b, c):
    return bar.bar(a, b) + zoo.zoo(b, c)
