
def add(arg1, arg2):
    var1 = arg1
    var2 = arg2
    return var1 + var2


def multiply(x,
             y,
             z=3):
    return x * y * z


def assign_value_to_list(x):
    l = list(range(5))
    l[0] = x
    return l


def assign_value_to_matrix(x, y):
    l = [[0, 1], [2, 3]]
    l[0][1] += (x - y) / 2
    return l


def string(x, y):
    z = x + y
    return f"print x: {x}, y: {y}, z: {z}"
