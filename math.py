def f(x):
    if x == 1:
        return 0
    else:
        y = round(0.25 * (x - 1 + 300 * (2 ** ((x - 1) / 7))))
        y += f(x - 1)
        return y


def g(x):
    if x == 1:
        return 0
    else:
        y = round(0.25 * (x - 1 + 300 * (2 ** ((x - 1) / 7))))
        return y


exp = {}
dexp = {}
for n in range(1, 99):
    exp[n] = f(n)
    dexp[n] = g(n)