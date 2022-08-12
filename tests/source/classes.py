

class A:
    def __init__(self, a, b=0):
        self.a = a
        self.b = b

    def add(self):
        return self.a + self.b


class B(A):
    def __init__(self, a, b, c):
        super().__init__(a, b)
        self.c = c

    def add(self):
        return self.a + self.b * self.c


class C:
    def __init__(self,
                 d,
                 e=0):
        self.d = d
        self.e = e

    def multiply(self):
        return self.d * self.e
