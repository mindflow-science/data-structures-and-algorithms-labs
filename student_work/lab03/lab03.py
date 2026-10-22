#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 3. Простые сортировки и QuickSort с рандомизацией — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-03 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Запуск: python lab03-simple-sorts-quicksort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import time

# ---------------------------------------------------------------------------
# 1. Простые сортировки со счётчиками (сортируют КОПИЮ входа, вход не меняют)
#    Каждая функция возвращает кортеж: (отсортированный список,
#    число сравнений ключей, число обменов/перемещений элементов).
# ---------------------------------------------------------------------------


"""ЛР 3. Задание 1. Простые сортировки со счётчиками."""

import argparse
import random
from collections import Counter
import csv
import platform
from pathlib import Path

def bubble_sort(a: list, key=lambda x: x) -> tuple[list, int, int]:
    """Пузырёк: считаются сравнения и обмены соседних элементов."""
    b = list(a)
    comparisons = swaps = 0

    for end in range(len(b) - 1, 0, -1):
        changed = False

        for j in range(end):
            comparisons += 1
            if key(b[j]) > key(b[j + 1]):
                b[j], b[j + 1] = b[j + 1], b[j]
                swaps += 1
                changed = True

        if not changed:
            break

    return b, comparisons, swaps


def insertion_sort(a: list, key=lambda x: x) -> tuple[list, int, int]:
    """Вставки: считаются сравнения и перемещения элементов. Перемещение - сдвиг элемента или запись вставляемого
    элемента на новое место. Копирование входа не учитывается.
    """
    b = list(a)
    comparisons = moves = 0

    for i in range(1, len(b)):
        value = b[i]
        value_key = key(value)
        j = i - 1

        while j >= 0:
            comparisons += 1

            if key(b[j]) <= value_key:
                break

            b[j + 1] = b[j]
            moves += 1
            j -= 1

        if j + 1 != i:
            b[j + 1] = value
            moves += 1

    return b, comparisons, moves


def selection_sort(a: list, key=lambda x: x) -> tuple[list, int, int]:
    """Выбор: считаются сравнения и фактически выполненные обмены."""
    b = list(a)
    comparisons = swaps = 0

    for i in range(len(b) - 1):
        minimum = i

        for j in range(i + 1, len(b)):
            comparisons += 1
            if key(b[j]) < key(b[minimum]):
                minimum = j

        if minimum != i:
            b[i], b[minimum] = b[minimum], b[i]
            swaps += 1

    return b, comparisons, swaps


# ---------------------------------------------------------------------------
# 2. QuickSort с рандомизированным опорным элементом
# ---------------------------------------------------------------------------


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
# 3. Демонстрация стабильности на парах (ключ, метка)
# ---------------------------------------------------------------------------


def stability_demo(seed: int = 46) -> None:
    """Проверка порядка меток при сортировке только по ключу."""
    pairs = [
        (2, "a"), (1, "b"), (2, "c"),
        (1, "d"), (2, "e"), (1, "f"),
    ]
    expected = sorted(pairs, key=lambda p: p[0])
    rng = random.Random(seed)

    sorters = [
        ("bubble_sort", bubble_sort),
        ("insertion_sort", insertion_sort),
        ("selection_sort", selection_sort),
        ("quick_sort", quick_sort),
    ]

    print("Исходный массив:", pairs)

    for name, fn in sorters:
        if name == "quick_sort":
            result = fn(pairs, rng, key=lambda p: p[0])
        else:
            result = fn(pairs, key=lambda p: p[0])[0]

        assert is_sorted([p[0] for p in result])
        assert Counter(result) == Counter(pairs)

        stable = result == expected
        if name in ("bubble_sort", "insertion_sort"):
            assert stable, f"{name}: нарушена стабильность"

        print(f"\n{name}: {result}")
        print(
            "Порядок меток сохранён:",
            "да" if stable else "нет",
        )


# ---------------------------------------------------------------------------
# 4. Классы входов (данные по варианту, детерминированно по seed)
# ---------------------------------------------------------------------------


def make_inputs(n: int, seed: int) -> dict[str, list[int]]:
    """Три класса входов размера n: упорядоченный, случайный, обратный."""
    rng = random.Random(seed + n)  # свой поток для каждого размера
    data = [rng.randint(-1_000_000, 1_000_000) for _ in range(n)]
    return {
        "упорядоченный": sorted(data),
        "случайный": data,
        "обратный": sorted(data, reverse=True),
    }


# ---------------------------------------------------------------------------
# 5. Верификация (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------

ALGORITHMS = {
    "bubble_sort": lambda a: bubble_sort(a)[0],
    "insertion_sort": lambda a: insertion_sort(a)[0],
    "selection_sort": lambda a: selection_sort(a)[0],
    "quick_sort": lambda a: quick_sort(a, random.Random(0)),
}


def is_sorted(a: list) -> bool:
    """Инвариант 1: неубывающий порядок элементов."""
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


def self_check() -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [5, 5, 5, 5],          # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for name, fn in ALGORITHMS.items():
        for a in boundary:
            res = fn(list(a))
            assert is_sorted(res), f"{name}: нарушен порядок на {a}"
            assert sorted(res) == sorted(a), f"{name}: не перестановка входа {a}"

    # Сверка с эталоном из стандартной библиотеки на сотнях случайных входов.
    rng = random.Random(0)
    for _ in range(300):
        a = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
        expected = sorted(a)
        for name, fn in ALGORITHMS.items():
            assert fn(list(a)) == expected, f"{name}: расходится с sorted() на {a}"

    # Счётчики: у сортировки выбором ровно n*(n-1)/2 сравнений на любом входе.
    _, comparisons, _ = selection_sort([3, 1, 2, 5, 4])
    assert comparisons == 10, "selection_sort: неверный счётчик сравнений"
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 6. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES_QUADRATIC = [250, 500, 1_000, 2_000, 4_000]
SIZES_QUICK = [1_000, 2_000, 4_000, 8_000, 16_000]
REPEATS = 5


def bench(fn, data: list) -> tuple:
    """Один прогрев, затем пять повторов; результат - медиана времени."""
    fn(list(data))
    times = []

    for _ in range(REPEATS):
        arg = list(data)
        start = time.perf_counter()
        result = fn(arg)
        times.append(time.perf_counter() - start)

    return statistics.median(times), result


def run_benchmarks(seed: int) -> None:
    """Замеры на одинаковых данных и сохранение времени и операций."""
    folder = Path(__file__).resolve().parent
    sizes = sorted(set(SIZES_QUADRATIC + SIZES_QUICK))
    datasets = {n: make_inputs(n, seed) for n in sizes}
    pivot_rng = random.Random(seed)

    plans = [
        ("bubble_sort", bubble_sort, SIZES_QUADRATIC),
        ("insertion_sort", insertion_sort, SIZES_QUADRATIC),
        ("selection_sort", selection_sort, SIZES_QUADRATIC),
        ("quick_sort", lambda a: quick_sort(a, pivot_rng), SIZES_QUICK),
    ]

    print(f"Вариант: {seed - 30}; seed: {seed}")
    print(f"Python: {platform.python_version()}")
    print(f"Методика: 1 прогрев, {REPEATS} повторов, медиана")
    rows = []

    for name, fn, plan_sizes in plans:
        print(f"\n{name}:")
        for n in plan_sizes:
            for cls, data in datasets[n].items():
                seconds, result = bench(fn, data)
                comparisons = operations = ""
                label = ""
                details = ""

                if name == "quick_sort":
                    sorted_data = result
                else:
                    sorted_data, comparisons, operations = result
                    label = (
                        "перемещения" if name == "insertion_sort" else "обмены"
                    )
                    details = (
                        f"; сравнения={comparisons}; {label}={operations}"
                    )

                assert sorted_data == datasets[n]["упорядоченный"]
                print(f"n={n:>6}; {cls:<13}; t={seconds:.9f} с{details}")
                rows.append({
                    "algorithm": name, "input": cls, "n": n,
                    "seconds": seconds, "comparisons": comparisons,
                    "operations": operations, "operation_type": label,
                })

    with (folder / "results.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nСохранено {len(rows)} строк в results.csv")
    print("Замеры завершены")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    stability_demo(seed)
    run_benchmarks(seed)


if __name__ == "__main__":
    main()
