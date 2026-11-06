#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 6. Линейный, бинарный и интерполяционный поиск — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-06 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Каждая функция поиска работает с отсортированным по неубыванию массивом
и возвращает пару (индекс найденного элемента или -1, число сравнений ключей).

Запуск: python lab06-search-starter.py --variant N
"""
from __future__ import annotations

import argparse
import bisect
import csv
import math
import platform
import random
import statistics
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Алгоритмы поиска (реализуются вручную, без in/index/bisect в основной части)
# ---------------------------------------------------------------------------


def linear_search(a: list[int], key: int) -> tuple[int, int]:
    """Линейный поиск первого вхождения key.

    Возвращает (индекс первого вхождения или -1, число сравнений).
    Время O(n), дополнительная память O(1).
    """
    comparisons = 0

    for index, value in enumerate(a):
        comparisons += 1
        if value == key:
            return index, comparisons

    return -1, comparisons


def binary_search(a: list[int], key: int) -> tuple[int, int]:
    """Бинарный поиск key в отсортированном массиве.

    Возвращает (индекс любого вхождения или -1, число сравнений).
    Время O(log n), дополнительная память O(1).
    """
    lo = 0
    hi = len(a) - 1
    comparisons = 0

    while lo <= hi:
        mid = (lo + hi) // 2

        comparisons += 1
        if a[mid] == key:
            return mid, comparisons

        comparisons += 1
        if a[mid] < key:
            lo = mid + 1
        else:
            hi = mid - 1

    return -1, comparisons


def interpolation_search(a: list[int], key: int) -> tuple[int, int]:
    """Интерполяционный поиск key в отсортированном массиве.

    Возвращает (индекс любого вхождения или -1, число сравнений).
    Среднее время на равномерных данных O(log log n), худшее O(n).
    Дополнительная память O(1).
    """
    lo = 0
    hi = len(a) - 1
    comparisons = 0

    while lo <= hi:
        comparisons += 1
        if a[lo] == a[hi]:
            comparisons += 1
            if a[lo] == key:
                return lo, comparisons
            return -1, comparisons

        comparisons += 1
        if key < a[lo]:
            return -1, comparisons

        comparisons += 1
        if key > a[hi]:
            return -1, comparisons

        mid = lo + (key - a[lo]) * (hi - lo) // (a[hi] - a[lo])

        comparisons += 1
        if a[mid] == key:
            return mid, comparisons

        comparisons += 1
        if a[mid] < key:
            lo = mid + 1
        else:
            hi = mid - 1

    return -1, comparisons


# ---------------------------------------------------------------------------
# 2. Данные по варианту: два распределения, присутствующие/отсутствующие ключи
# ---------------------------------------------------------------------------


def make_dataset(n: int, distribution: str, rng: random.Random) -> list[int]:
    """Отсортированный массив n ключей: 'uniform' — равномерное распределение,
    'exponential' — неравномерное (экспоненциальное, значения сгущаются у нуля)."""
    if distribution == "uniform":
        return sorted(rng.randint(0, 10 * n) for _ in range(n))
    if distribution == "exponential":
        return sorted(int(rng.expovariate(1.0 / 1000.0)) for _ in range(n))
    raise ValueError(f"неизвестное распределение: {distribution!r}")


def pick_keys(a: list[int], rng: random.Random, count: int,
              present: bool) -> list[int]:
    """count ключей для серии поисков: присутствующие берутся из массива,
    отсутствующие подбираются вне множества его значений."""
    if present:
        return [a[rng.randrange(len(a))] for _ in range(count)]
    have = set(a)
    hi = (a[-1] if a else 0) + 2
    keys: list[int] = []
    while len(keys) < count:
        k = rng.randint(-hi, hi)
        if k not in have:
            keys.append(k)
    return keys


# ---------------------------------------------------------------------------
# 3. Репрезентативные тесты и инварианты (шаги 1–3 методики верификации)
# ---------------------------------------------------------------------------

ALGORITHMS = [
    ("linear", linear_search),
    ("binary", binary_search),
    ("interpolation", interpolation_search),
]


def self_check() -> None:
    """Граничные случаи + сверка с эталоном (оператор in, list.index, bisect)."""
    for name, fn in ALGORITHMS:
        # Пустой массив: элемент не найден, сравнений нет.
        assert fn([], 1) == (-1, 0), f"{name}: пустой массив"
        # Один элемент: найден / не найден.
        assert fn([7], 7)[0] == 0, f"{name}: один элемент, ключ найден"
        assert fn([7], 3)[0] == -1, f"{name}: один элемент, ключ отсутствует"
        # Первый, последний и отсутствующие ключи (внутри и вне диапазона).
        a = [1, 3, 3, 5, 8, 13, 21]
        assert fn(a, 1)[0] == 0, f"{name}: первый элемент"
        assert fn(a, 21)[0] == len(a) - 1, f"{name}: последний элемент"
        assert fn(a, 4)[0] == -1, f"{name}: отсутствующий ключ внутри диапазона"
        assert fn(a, 100)[0] == -1, f"{name}: ключ вне диапазона"

    # Сверка с эталоном стандартной библиотеки на случайных массивах.
    rng = random.Random(0)
    for _ in range(300):
        a = sorted(rng.randint(0, 60) for _ in range(rng.randint(1, 40)))
        key = rng.randint(-5, 65)
        # Эталон присутствия ключа — bisect_left (и, эквивалентно, оператор in).
        j = bisect.bisect_left(a, key)
        present = j < len(a) and a[j] == key
        assert present == (key in a)
        for name, fn in ALGORITHMS:
            idx, cmp_count = fn(a, key)
            assert cmp_count >= 1, f"{name}: счётчик сравнений не ведётся"
            if present:
                # При дубликатах бинарный/интерполяционный могут вернуть
                # любое вхождение — проверяем значение по индексу.
                assert idx != -1 and a[idx] == key, f"{name}: ключ не найден"
            else:
                assert idx == -1, f"{name}: найден отсутствующий ключ"
        # Линейный поиск обязан возвращать первое вхождение — эталон list.index.
        if present:
            assert linear_search(a, key)[0] == a.index(key)
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 4. Бенчмарк: сравнения и время от n (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5      # число повторов серии замеров (берётся медиана)
N_KEYS = 200     # число ключей в одной серии поисков


def bench(fn, a: list[int], keys: list[int]) -> float:
    """Медиана времени одной серии поисков по REPEATS запускам, с прогревом."""
    for k in keys:  # прогрев — не учитывается
        fn(a, k)
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        for k in keys:
            fn(a, k)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def mean_comparisons(fn, a: list[int], keys: list[int]) -> float:
    """Среднее число сравнений ключей на один поиск."""
    return statistics.mean(fn(a, k)[1] for k in keys)


def plot_results(rows: list[dict], output_dir: Path) -> None:
    """Построить графики сравнений и времени для обоих распределений."""
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 12})
    styles = {
        "linear": ("Линейный", "C0"),
        "binary": ("Бинарный", "C1"),
        "interpolation": ("Интерполяционный", "C2"),
    }
    titles = {
        "uniform": "Равномерное распределение",
        "exponential": "Экспоненциальное распределение",
    }

    for distribution in titles:
        fig_c, axes_c = plt.subplots(
            1, 2, figsize=(11, 4.5), layout="constrained"
        )
        fig_t, axes_t = plt.subplots(
            2, 2, figsize=(11, 8), layout="constrained"
        )
        fig_c.suptitle(titles[distribution])
        fig_t.suptitle(titles[distribution])

        for col, present in enumerate((True, False)):
            title = "Ключ присутствует" if present else "Ключ отсутствует"

            for name, _ in ALGORITHMS:
                points = [
                    row for row in rows
                    if row["distribution"] == distribution
                    and row["present"] == present
                    and row["algorithm"] == name
                ]
                points.sort(key=lambda row: row["n"])
                sizes = [row["n"] for row in points]
                comparisons = [row["comparisons"] for row in points]
                times = [row["time_us"] for row in points]
                label, color = styles[name]

                axes_c[col].loglog(
                    sizes, comparisons, "o-", label=label, color=color
                )
                axes_t[0, col].loglog(
                    sizes, times, "o-", label=label, color=color
                )
                if name != "linear":
                    axes_t[1, col].plot(
                        [math.log2(n) for n in sizes], times,
                        "o-", label=label, color=color
                    )

            axes_c[col].set_title(title)
            axes_c[col].set_xlabel("Размер массива n")
            axes_c[col].set_ylabel("Среднее число сравнений")
            axes_t[0, col].set_title(title)
            axes_t[0, col].set_xlabel("Размер массива n")
            axes_t[1, col].set_title(title + ": время от log₂(n)")
            axes_t[1, col].set_xlabel("log₂(n)")
            for row in range(2):
                axes_t[row, col].set_ylabel("Время одного поиска, мкс")

        for ax in [*axes_c, *axes_t.flat]:
            ax.grid(True, which="both", alpha=0.3)
            ax.legend(fontsize=10)

        fig_c.savefig(output_dir / f"comparisons_{distribution}.png", dpi=180)
        fig_t.savefig(output_dir / f"time_{distribution}.png", dpi=180)
        plt.close(fig_c)
        plt.close(fig_t)


def run_benchmarks(seed: int) -> None:
    rng = random.Random(seed)
    rows = []
    output_dir = Path(__file__).resolve().parent / "results"
    output_dir.mkdir(exist_ok=True)

    cpu = platform.processor() or "не определён"
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        for line in cpuinfo.read_text(encoding="utf-8").splitlines():
            if line.startswith("model name"):
                cpu = line.split(":", 1)[1].strip()
                break

    environment = (
        f"CPU: {cpu}\nPython: {platform.python_version()}\n"
        f"Вариант: {seed - 30}\nSeed: {seed}\n"
        f"Размеры: {SIZES}\nПовторы: {REPEATS}\nКлючей в серии: {N_KEYS}\n"
        "Время: медиана времени серии / число ключей, микросекунды\n"
    )
    (output_dir / "environment.txt").write_text(environment, encoding="utf-8")
    print(environment)

    for distribution in ("uniform", "exponential"):
        print(f"Распределение: {distribution}")
        for n in SIZES:
            a = make_dataset(n, distribution, rng)
            for present in (True, False):
                keys = pick_keys(a, rng, N_KEYS, present)
                for name, fn in ALGORITHMS:
                    comparisons = mean_comparisons(fn, a, keys)
                    time_us = bench(fn, a, keys) / len(keys) * 1_000_000
                    rows.append({
                        "distribution": distribution,
                        "n": n,
                        "present": present,
                        "algorithm": name,
                        "comparisons": comparisons,
                        "time_us": time_us,
                    })
                    label = "есть" if present else "нет"
                    print(
                        f"n={n:>6} ключ {label:<4} {name:<13} "
                        f"сравнений={comparisons:>10.2f} "
                        f"время={time_us:>10.3f} мкс",
                        flush=True,
                    )

    csv_path = output_dir / "benchmark.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)

    plot_results(rows, output_dir)
    print(f"Сохранено строк: {len(rows)}")
    print(f"Таблица и графики: {output_dir}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    run_benchmarks(seed)


if __name__ == "__main__":
    main()
