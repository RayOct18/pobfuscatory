
def add(arg1, arg2):
    var1 = arg1
    var2 = arg2
    return var1 + var2


def multiply(x1,
             y1,
             z1=3):
    return x1 * y1 * z1


def assign_value_to_list(x2):
    l1 = list(range(5))
    l1[0] = x2
    return l1


def assign_value_to_matrix(x3, y3):
    l2 = [[0, 1], [2, 3]]
    l2[0][1] += (x3 - y3) / 2
    return l2


def string(x4, y4):
    z4 = x4 + y4
    return f"print x4: {x4}, y4: {y4}, z4: {z4}"


def multiline_string(x5):
    s = "test1, x5\n" +\
        "test2"
    s += "test3 \
          test4 x5  "
    s += str(x5)
    return s
