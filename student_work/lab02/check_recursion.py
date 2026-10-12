import math
from unittest import TestCase

from lab02 import CALLS, factorial, fib_naive, fib_memo

assert all(factorial(n) == math.factorial(n) for n in range(101))
TestCase().assertRaises(ValueError, factorial, -1)
print("factorial: OK")


cases = {
    0: 0, 1: 1, 2: 1, 5: 5, 10: 55, 15: 610, 20: 6765, 25: 75025
}

print("\n n |   F(n) | Наивная | Мемоизация")
for n, expected in cases.items():
    CALLS["fib_naive"] = CALLS["fib_memo"] = 0
    a, b = fib_naive(n), fib_memo(n)
    assert a == b == expected, f"Ошибка при n={n}"
    naive_calls = CALLS["fib_naive"]
    memo_calls = CALLS["fib_memo"]
    assert n < 5 or memo_calls < naive_calls
    print(f"{n:>2} | {a:>6} | {naive_calls:>7} | {memo_calls:>10}")

for fn in (fib_naive, fib_memo):
    TestCase().assertRaises(ValueError, fn, -1)
print("Фибоначчи: OK")