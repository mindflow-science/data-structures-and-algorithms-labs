#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 4. MergeSort, Counting, Radix и HeapSort: оценка производительности — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-04 и правилами использования генеративного ИИ
(docs/ai-verification.md). QuickSort перенесите из собственной ЛР 3.

Запуск: python lab04-mergesort-linear-heapsort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import sys
import time
import traceback

# ---------------------------------------------------------------------------
# 1. Сортировки (реализуются вручную; sorted() используется только как эталон)
# ---------------------------------------------------------------------------


def merge(left: list, right: list, key) -> list:
    """Стабильное слияние двух отсортированных списков."""
    result = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


def merge_sort(a: list, key=lambda x: x) -> list:
    """Стабильная сортировка слиянием: время O(n log n), память O(n)."""
    if len(a) <= 1:
        return list(a)

    middle = len(a) // 2
    left = merge_sort(a[:middle], key=key)
    right = merge_sort(a[middle:], key=key)
    return merge(left, right, key)


def counting_sort(a: list, key_max: int, key=lambda x: x) -> list:
    """Устойчивая сортировка целых ключей от 0 до key_max."""
    if not a:
        return []

    minimum = min(key(item) for item in a)
    maximum = max(key(item) for item in a)
    if minimum < 0 or maximum > key_max:
        raise ValueError("Ключ выходит за диапазон от 0 до key_max")

    counts = [0] * (maximum - minimum + 1)
    for item in a:
        counts[key(item) - minimum] += 1

    for i in range(1, len(counts)):
        counts[i] += counts[i - 1]

    result = [None] * len(a)
    for item in reversed(a):
        index = key(item) - minimum
        counts[index] -= 1
        result[counts[index]] = item

    return result


def counting_sort_digit(a: list, exp: int, key=lambda x: x) -> list:
    """Устойчивый проход по одной десятичной цифре."""
    return counting_sort(a, key_max=9, key=lambda item: (key(item) // exp) % 10)


def radix_sort_lsd(a: list, key=lambda x: x) -> list:
    """RadixSort LSD: время O(d(n + 10)), память O(n + 10)."""
    if not a:
        return []
    if min(key(item) for item in a) < 0:
        raise ValueError("RadixSort принимает неотрицательные целые ключи")

    result = list(a)
    maximum = max(key(item) for item in result)
    exp = 1
    while exp <= maximum:
        result = counting_sort_digit(result, exp, key=key)
        exp *= 10
    return result


def sift_down(a: list[int], i: int, n: int) -> None:
    """Просейка вниз в max-куче: рассматриваются индексы меньше n."""
    while True:
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2

        if left < n and a[left] > a[largest]:
            largest = left
        if right < n and a[right] > a[largest]:
            largest = right
        if largest == i:
            return

        a[i], a[largest] = a[largest], a[i]
        i = largest


def build_heap(a: list[int]) -> None:
    """Построение max-кучи снизу вверх за O(n)."""
    for i in range(len(a) // 2 - 1, -1, -1):
        sift_down(a, i, len(a))


def heap_sort(a: list[int]) -> None:
    """Сортировка на месте: худшее время O(n log n), память O(1)."""
    build_heap(a)
    for end in range(len(a) - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        sift_down(a, 0, end)


def quick_sort(a: list, rng=None, key=lambda x: x) -> list:
    """QuickSort: в среднем O(n log n), в худшем O(n²)."""
    if rng is None:
        rng = random

    b = list(a)
    stack = [(0, len(b))]

    while stack:
        lo, hi = stack.pop()

        if hi - lo <= 1:
            continue

        pivot_index = rng.randrange(lo, hi)
        b[pivot_index], b[hi - 1] = b[hi - 1], b[pivot_index]
        pivot = key(b[hi - 1])

        position = lo
        for j in range(lo, hi - 1):
            if key(b[j]) < pivot:
                b[position], b[j] = b[j], b[position]
                position += 1

        b[position], b[hi - 1] = b[hi - 1], b[position]

        if position - lo > 1:
            stack.append((lo, position))

        if hi - position - 1 > 1:
            stack.append((position + 1, hi))

    return b


# ---------------------------------------------------------------------------
# 2. Верификация: инварианты + сверка с эталоном sorted()
#    (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------


class SelfCheckError(Exception):
    """Нарушен контракт или инвариант реализации."""


def expect(condition: bool, message: str) -> None:
    """Явная проверка вместо assert: assert-ы исчезают при запуске python -O."""
    if not condition:
        raise SelfCheckError(message)


def heap_sorted(a: list[int]) -> list[int]:
    """heap_sort сортирует на месте: проверяется тот список, который ему передали."""
    buf = list(a)
    heap_sort(buf)
    return buf


#Каждая функция возвращает отсортированный список.
SORTS = {
    "merge_sort": lambda a: merge_sort(a),
    "counting_sort": lambda a: counting_sort(a, key_max=999),
    "radix_sort_lsd": lambda a: radix_sort_lsd(a),
    "heap_sort": lambda a: heap_sorted(a),
    "quick_sort": lambda a: quick_sort(a),
}


def check_sort(fn, signed: bool = False) -> None:
    """Граничные случаи, порядок, сохранность элементов и сверка с sorted()."""
    cases = [
        [], [7], [0], [2, 1], [1, 2], [5, 5, 5],
        [1, 2, 3, 4, 5], [5, 4, 3, 2, 1],
    ]
    if signed:
        cases.append([-3, 0, -1, -3, 2])
    for seed in (0, 46):
        rng = random.Random(seed)
        for _ in range(200):
            cases.append([
                rng.randint(0, 999) for _ in range(rng.randint(0, 60))
            ])
    for a in cases:
        result = fn(list(a))
        expect(isinstance(result, list), "Результат должен быть списком")
        expect(all(result[i] <= result[i + 1]
                   for i in range(len(result) - 1)),
               f"Нарушен порядок на входе {a}")
        expected = sorted(a)
        expect(sorted(result) == expected, f"Изменён набор элементов на входе {a}")
        expect(result == expected, f"Расхождение с sorted() на входе {a}")


def check_stability(fn) -> None:
    """Порядок номеров при одинаковых ключах должен сохраняться."""
    rng = random.Random(46)
    pairs = [(rng.randint(0, 99), i) for i in range(200)]
    expect(fn(list(pairs)) == sorted(pairs, key=lambda p: p[0]),
           "Нарушена устойчивость на парах (ключ, порядковый номер)")


def check_merge_stability() -> None:
    """Сохраняем проверку заготовки и добавляем проверку с seed=46."""
    rng = random.Random(0)
    pairs = [(rng.randint(0, 5), i) for i in range(100)]
    expect(merge_sort(pairs, key=lambda p: p[0])
           == sorted(pairs, key=lambda p: p[0]),
           "merge_sort нарушает порядок равных ключей")
    check_stability(lambda a: merge_sort(a, key=lambda p: p[0]))


def check_radix_pass() -> None:
    """Проверка цифры и устойчивости отдельного поразрядного прохода."""
    pairs = [(21, 0), (11, 1), (22, 2), (12, 3), (21, 4), (11, 5)]
    for exp in (1, 10, 100):
        result = counting_sort_digit(pairs, exp, key=lambda p: p[0])
        expected = sorted(pairs, key=lambda p: (p[0] // exp) % 10)
        expect(result == expected, f"Неверный или неустойчивый проход exp={exp}")


def check_heap() -> None:
    """После построения кучи родитель не меньше каждого своего потомка."""
    rng = random.Random(46)
    for n in (0, 1, 2, 10, 100):
        data = [rng.randint(0, 999) for _ in range(n)]
        expected = sorted(data)
        build_heap(data)
        expect(all(data[(i - 1) // 2] >= data[i] for i in range(1, n)),
               "Нарушено свойство max-кучи")
        expect(sorted(data) == expected, "Построение кучи изменило набор элементов")


def self_check() -> None:
    """При любой ошибке проверки останавливают дальнейшие замеры."""
    signed_names = {"merge_sort", "heap_sort", "quick_sort"}
    checks = [
        (name, lambda fn=fn, signed=name in signed_names:
         check_sort(fn, signed=signed))
        for name, fn in SORTS.items()
    ]
    checks.extend([
        ("стабильность merge_sort", check_merge_stability),
        ("стабильность counting_sort", lambda: check_stability(
            lambda a: counting_sort(a, key_max=99, key=lambda p: p[0]))),
        ("стабильность radix_sort_lsd", lambda: check_stability(
            lambda a: radix_sort_lsd(a, key=lambda p: p[0]))),
        ("устойчивость поразрядного прохода", check_radix_pass),
        ("свойство max-кучи", check_heap),
    ])
    failed = 0
    print("self_check:")
    for name, check in checks:
        try:
            check()
        except NotImplementedError as err:
            where = traceback.extract_tb(err.__traceback__)[-1].name
            print(f"  {name}: не реализовано - {where}")
            failed += 1
        except SelfCheckError as err:
            print(f"  {name}: ОШИБКА - {err}")
            failed += 1
        except Exception:
            print(f"  {name}: ИСКЛЮЧЕНИЕ")
            traceback.print_exc(file=sys.stdout)
            failed += 1
        else:
            print(f"  {name}: OK")
    if failed:
        raise SystemExit(f"self_check: ошибок - {failed}; замеры остановлены")
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 3. Бенчмарк: задание 5 методички
# ---------------------------------------------------------------------------


SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5
SMALL_KEY_MAX = 100
WIDE_KEY_MAX = 10**9


def make_datasets(rng: random.Random, n: int) -> dict[str, list[int]]:
    """Пять распределений из заготовки преподавателя."""
    almost = list(range(n))
    for _ in range(max(1, n // 100)):
        i, j = rng.randrange(n), rng.randrange(n)
        almost[i], almost[j] = almost[j], almost[i]
    return {
        "random_wide": [rng.randint(0, WIDE_KEY_MAX) for _ in range(n)],
        "random_small": [rng.randint(0, SMALL_KEY_MAX) for _ in range(n)],
        "sorted": list(range(n)),
        "reversed": list(range(n, 0, -1)),
        "almost_sorted": almost,
    }


def bench(fn, data: list[int]) -> float:
    """Один прогрев, пять измеряемых повторов и медиана."""
    fn(list(data))
    times = []
    for _ in range(REPEATS):
        buf = list(data)
        start = time.perf_counter()
        fn(buf)
        times.append(time.perf_counter() - start)
    return statistics.median(times)


def plot_results(rows: list, folder, seed: int) -> None:
    """Пять log-log графиков по результатам, сохранённым в CSV."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    for distribution in dict.fromkeys(row[1] for row in rows):
        fig, ax = plt.subplots(figsize=(8, 5))
        for name in dict.fromkeys(row[2] for row in rows):
            points = [
                row for row in rows
                if row[1] == distribution and row[2] == name
                and row[3] is not None
            ]
            if points:
                ax.loglog(
                    [row[0] for row in points], [row[3] for row in points],
                    marker="o", label=name,
                )
        ax.set_title(f"{distribution}; seed={seed}")
        ax.set_xlabel("Количество элементов n")
        ax.set_ylabel("Медиана времени, с")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
        fig.tight_layout()
        path = folder / f"{distribution}_time.png"
        fig.savefig(path, dpi=160)
        plt.close(fig)
        print("Сохранён график:", path.name)


def run_benchmarks(seed: int) -> None:
    """Все сортировки получают одинаковые входные данные."""
    import csv
    from pathlib import Path

    rng = random.Random(seed)
    pivot_rng = random.Random(seed)
    algorithms = [
        ("merge_sort", merge_sort),
        ("counting_sort", lambda a: counting_sort(a, key_max=max(a, default=0))),
        ("radix_sort_lsd", radix_sort_lsd),
        ("heap_sort", heap_sort),
        ("quick_sort", lambda a: quick_sort(a, rng=pivot_rng)),
        ("sorted", sorted),
    ]
    rows = []
    for n in SIZES:
        for distribution, data in make_datasets(rng, n).items():
            print(f"\nn={n}; {distribution}", flush=True)
            for name, fn in algorithms:
                seconds = None
                if name == "counting_sort" and distribution == "random_wide":
                    print(f"  {name}: пропуск - широкий диапазон", flush=True)
                else:
                    seconds = bench(fn, data)
                    print(f"  {name}: {seconds:.8f} с", flush=True)
                rows.append((n, distribution, name, seconds))
    folder = Path(__file__).resolve().parent
    with (folder / "results.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["n", "distribution", "algorithm", "seconds"])
        writer.writerows(rows)
    print(f"\nСохранено {len(rows)} строк в results.csv")
    plot_results(rows, folder, seed)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    print(f"Вариант: {args.variant}; seed={seed}")
    print("Python:", sys.version.split()[0])
    print(f"Методика: 1 прогрев, {REPEATS} повторов, медиана")
    self_check()
    run_benchmarks(seed)


if __name__ == "__main__":
    main()
