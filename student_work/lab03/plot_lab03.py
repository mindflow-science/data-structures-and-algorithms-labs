import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


folder = Path(__file__).resolve().parent

with (folder / "results.csv").open(
    encoding="utf-8-sig", newline=""
) as file:
    rows = list(csv.DictReader(file))

algorithms = {
    "bubble_sort": "Сортировка пузырьком",
    "insertion_sort": "Сортировка вставками",
    "selection_sort": "Сортировка выбором",
    "quick_sort": "Быстрая сортировка QuickSort",
}

input_types = list(dict.fromkeys(row["input"] for row in rows))

for name, title in algorithms.items():
    fig, ax = plt.subplots(figsize=(8, 5))

    for input_type in input_types:
        points = sorted(
            (int(row["n"]), float(row["seconds"]))
            for row in rows
            if row["algorithm"] == name
            and row["input"] == input_type
        )

        sizes = [n for n, seconds in points]
        times = [seconds for n, seconds in points]

        ax.plot(sizes, times, marker="o", label=input_type)

    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xticks(sizes, labels=[str(n) for n in sizes])
    ax.set_title(title)
    ax.set_xlabel("Размер массива n")
    ax.set_ylabel("Медиана времени, с")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()

    fig.tight_layout()
    path = folder / f"{name}_time.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)

    print("Сохранён график:", path.name)

print("Построено 4 графика")