#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 2. Рекурсивные функции; динамический массив, стек и дек — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-02 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Запуск: python lab02-recursion-structures-starter.py --variant N
"""
from __future__ import annotations

import argparse
import collections
import math
import random
import statistics
import time

# ---------------------------------------------------------------------------
# 1. Рекурсивные функции (счётчик вызовов — для сравнения наивной рекурсии
#    и мемоизации; результаты счётчика включаются в отчёт)
# ---------------------------------------------------------------------------

CALLS = {"fib_naive": 0, "fib_memo": 0}  # счётчики рекурсивных вызовов


def factorial(n: int) -> int:
    """Рекурсивный факториал: O(n) вызовов и O(n) памяти стека."""
    if n < 0:
        raise ValueError("n должно быть неотрицательным")
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def fib_naive(n: int) -> int:
    """Фибоначчи наивной рекурсией: экспоненциальное число вызовов."""
    if n < 0:
        raise ValueError("n должно быть неотрицательным")
    CALLS["fib_naive"] += 1
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


def fib_memo(n: int, memo: dict[int, int] | None = None) -> int:
    """Фибоначчи с мемоизацией: O(n) вызовов при пустом кэше."""
    if n < 0:
        raise ValueError("n должно быть неотрицательным")
    CALLS["fib_memo"] += 1
    if n <= 1:
        return n
    if memo is None:
        memo = {}
    if n not in memo:
        memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]


def hanoi(n: int, src: str = "A", dst: str = "C", aux: str = "B") -> int:
    """Вернуть число перемещений; O(2**n) вызовов, O(n) глубина стека."""
    if n < 0:
        raise ValueError("n должно быть неотрицательным")
    if n == 0:
        return 0
    return hanoi(n - 1, src, aux, dst) + 1 + hanoi(n - 1, aux, dst, src)


# ---------------------------------------------------------------------------
# 2. Динамический массив с ручным управлением ёмкостью (рост x2)
# ---------------------------------------------------------------------------


class DynamicArray:
    """Динамический массив с удвоением ёмкости."""

    INITIAL_CAPACITY = 4

    def __init__(self) -> None:
        self._size = 0
        self._capacity = self.INITIAL_CAPACITY
        self._buffer: list = [None] * self._capacity

    def __len__(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        return self._capacity

    def _grow(self) -> None:
        new_capacity = self._capacity * 2
        new_buffer = [None] * new_capacity
        for i in range(self._size):
            new_buffer[i] = self._buffer[i]
        self._buffer = new_buffer
        self._capacity = new_capacity

    def append(self, value) -> None:
        if self._size == self._capacity:
            self._grow()
        self._buffer[self._size] = value
        self._size += 1

    def get(self, index: int):
        if index < 0 or index >= self._size:
            raise IndexError("Индекс вне границ массива")
        return self._buffer[index]

    def set(self, index: int, value) -> None:
        if index < 0 or index >= self._size:
            raise IndexError("Индекс вне границ массива")
        self._buffer[index] = value


# ---------------------------------------------------------------------------
# 3. Стек и дек на базе собственных структур
# ---------------------------------------------------------------------------


class Stack:
    """Стек (LIFO) на базе DynamicArray."""

    def __init__(self) -> None:
        self._data = DynamicArray()

    def __len__(self) -> int:
        return len(self._data)

    def push(self, value) -> None:
        """Положить элемент на вершину. Амортизированная сложность: TODO."""
        # TODO: делегировать DynamicArray.append
        raise NotImplementedError

    def pop(self):
        """Снять элемент с вершины; для пустого стека — IndexError."""
        # TODO: прочитать последний элемент, уменьшить размер
        raise NotImplementedError

    def peek(self):
        """Вернуть вершину без удаления; для пустого стека — IndexError."""
        # TODO
        raise NotImplementedError


class _Node:
    """Узел двусвязного списка для Deque."""

    __slots__ = ("value", "prev", "next")

    def __init__(self, value, prev=None, next=None) -> None:  # noqa: A002
        self.value = value
        self.prev = prev
        self.next = next


class Deque:
    """Дек (двусторонняя очередь) на базе двусвязного списка.

    Все четыре операции концов должны стоить O(1) — без амортизации,
    в отличие от вставки в начало динамического массива (см. отчёт).
    """

    def __init__(self) -> None:
        self._head: _Node | None = None
        self._tail: _Node | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def push_front(self, value) -> None:
        """Добавить элемент в начало. Сложность: TODO."""
        # TODO: создать узел, перевязать ссылки head (учесть пустой дек)
        raise NotImplementedError

    def push_back(self, value) -> None:
        """Добавить элемент в конец. Сложность: TODO."""
        # TODO: симметрично push_front для tail
        raise NotImplementedError

    def pop_front(self):
        """Извлечь элемент из начала; для пустого дека — IndexError."""
        # TODO: учесть переход к пустому деку (tail тоже обнуляется)
        raise NotImplementedError

    def pop_back(self):
        """Извлечь элемент из конца; для пустого дека — IndexError."""
        # TODO
        raise NotImplementedError


# ---------------------------------------------------------------------------
# 4. Репрезентативные тесты и инварианты (шаги 1–3 методики верификации)
# ---------------------------------------------------------------------------


def self_check() -> None:
    """Граничные и типовые случаи + сверка с эталонами стандартной библиотеки."""
    # --- рекурсия: сверка с math.factorial и формулой Ханойских башен ---
    assert factorial(0) == 1
    for n in range(0, 12):
        assert factorial(n) == math.factorial(n)
    CALLS["fib_naive"] = CALLS["fib_memo"] = 0
    assert fib_naive(10) == 55
    assert fib_memo(10) == 55
    assert CALLS["fib_memo"] < CALLS["fib_naive"]  # мемоизация экономит вызовы
    for n in (0, 1, 3, 8):
        assert hanoi(n) == 2 ** n - 1

    # --- DynamicArray: инвариант size <= capacity, сверка с list ---
    arr, ref = DynamicArray(), []
    for i in range(100):  # проходим несколько границ роста ёмкости
        arr.append(i * i)
        ref.append(i * i)
        assert len(arr) == len(ref) <= arr.capacity
    assert [arr.get(i) for i in range(len(arr))] == ref
    arr.set(0, -1)
    assert arr.get(0) == -1
    try:
        arr.get(len(arr))
        assert False, "ожидался IndexError"
    except IndexError:
        pass

    # --- Stack: порядок LIFO, сверка с list ---
    st, ref = Stack(), []
    for x in [1, 2, 3]:
        st.push(x)
        ref.append(x)
    assert st.peek() == ref[-1]
    while ref:
        assert st.pop() == ref.pop()
    assert len(st) == 0

    # --- Deque: порядок FIFO и работа с обоих концов, сверка с collections.deque ---
    dq, ref = Deque(), collections.deque()
    dq.push_back(1), ref.append(1)
    dq.push_front(0), ref.appendleft(0)
    dq.push_back(2), ref.append(2)
    assert dq.pop_front() == ref.popleft() == 0
    assert dq.pop_back() == ref.pop() == 2
    assert dq.pop_front() == ref.popleft() == 1
    assert len(dq) == len(ref) == 0
    try:
        dq.pop_front()
        assert False, "ожидался IndexError"
    except IndexError:
        pass
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 5. Замеры (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5


def bench(fn, *args) -> float:
    """Медиана времени выполнения fn(*args) по REPEATS запускам, с прогревом."""
    fn(*args)  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        fn(*args)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def appends_dynamic_array(n: int) -> None:
    """n последовательных append в свой DynamicArray."""
    arr = DynamicArray()
    for i in range(n):
        arr.append(i)


def inserts_front_list(n: int) -> None:
    """n вставок в начало встроенного list — ожидаемо O(n) на операцию."""
    a: list[int] = []
    for i in range(n):
        a.insert(0, i)


def inserts_front_deque(n: int) -> None:
    """n вставок в начало collections.deque — ожидаемо O(1) на операцию."""
    d: collections.deque = collections.deque()
    for i in range(n):
        d.appendleft(i)


def run_benchmarks(seed: int) -> None:
    """Средняя стоимость append и сравнение вставки в начало list/deque."""
    rng = random.Random(seed)
    _ = rng.random()  # данные варианта фиксируются seed (см. reproducibility.md)
    print("\nСредняя стоимость append (DynamicArray), демонстрация амортизированной O(1):")
    for n in SIZES:
        t = bench(appends_dynamic_array, n)
        print(f"  n={n:>7}  всего t={t:.6f} c  на операцию t/n={t / n:.3e} c")
    print("\nВставка в начало: list.insert(0, x) против deque.appendleft:")
    for n in SIZES:
        if n > 30_000:
            continue  # вставка в начало list квадратична по суммарному времени
        t_list = bench(inserts_front_list, n)
        t_deque = bench(inserts_front_deque, n)
        print(f"  n={n:>7}  list={t_list:.6f} c  deque={t_deque:.6f} c")
    # TODO: снять аналогичные замеры для push_front своего Deque;
    # TODO: построить график t/n от n для append и включить его в отчёт;
    # TODO: провести амортизированный анализ push_back методом учёта (в отчёте).

def benchmark_append(seed: int) -> None:
    """Измерить время append и сохранить результаты и график."""
    import csv
    import json
    import platform
    from pathlib import Path

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sizes = [1_000, 3_000, 10_000, 30_000, 100_000, 300_000]
    repeats = 5

    rng = random.Random(seed)
    data = [rng.randint(-1_000_000, 1_000_000) for _ in range(max(sizes))]

    cpu = "Не определён"
    for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
        if line.startswith("model name"):
            cpu = line.split(":", 1)[1].strip()
            break

    print(f"\nCPU: {cpu}")
    print(f"Python: {platform.python_version()}")
    print(f"Seed: {seed}; прогрев: 1; повторов: {repeats}; обработка: медиана")
    print("\n       n | Ёмкость | Медиана серии, с | Среднее на append, мкс")

    rows = []
    costs_us = []

    for n in sizes:
        values = data[:n]

        arr = DynamicArray()
        for value in values:
            arr.append(value)

        times = []

        for _ in range(repeats):
            arr = DynamicArray()

            t0 = time.perf_counter()
            for value in values:
                arr.append(value)
            elapsed = time.perf_counter() - t0

            times.append(elapsed)

        median_s = statistics.median(times)
        mean_us = median_s / n * 1_000_000

        rows.append([n, arr.capacity, *times, median_s, mean_us])
        costs_us.append(mean_us)

        print(f"{n:>8} | {arr.capacity:>7} | {median_s:>16.6f} | {mean_us:>21.6f}")

    output_dir = Path(__file__).resolve().parent

    csv_path = output_dir / "append_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "n", "capacity",
            *[f"repeat_{i}_s" for i in range(1, repeats + 1)],
            "median_total_s", "mean_append_us",
        ])
        writer.writerows(rows)

    metadata = {
        "cpu": cpu,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "seed": seed,
        "sizes": sizes,
        "warmups_per_size": 1,
        "repeats_per_size": repeats,
        "timer": "time.perf_counter",
        "processing": "median_total_s / n * 1e6",
        "fresh_array_each_run": True,
        "data_generated_before_timing": True,
        "total_time_unit": "seconds",
        "append_time_unit": "microseconds",
    }

    metadata_path = output_dir / "append_environment.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Строим график с логарифмическими осями.
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.loglog(sizes, costs_us, "o-", label="Медиана времени серии / n")
    ax.set_xlabel("Количество добавлений n (логарифмическая шкала)")
    ax.set_ylabel("Среднее время append, мкс (логарифмическая шкала)")
    ax.set_title(f"Средняя стоимость append, seed = {seed}")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()

    graph_path = output_dir / "append_benchmark.png"
    fig.savefig(graph_path, dpi=200)
    plt.close(fig)

    print("\nСохранены файлы:")
    for path in (csv_path, metadata_path, graph_path):
        print(path)

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
