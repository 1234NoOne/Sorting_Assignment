import time
import random
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys


def bubble_sort(arr):
    a = arr.copy()
    n = len(a)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:
            break
    return a


def selection_sort(arr):
    a = arr.copy()
    n = len(a)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if a[j] < a[min_idx]:
                min_idx = j
        a[i], a[min_idx] = a[min_idx], a[i]
    return a


def quick_sort(arr):
    a = arr.copy()
    _quick_sort_helper(a, 0, len(a) - 1)
    return a


def _quick_sort_helper(a, low, high):
    if low < high:
        pi = _partition(a, low, high)
        _quick_sort_helper(a, low, pi - 1)
        _quick_sort_helper(a, pi + 1, high)


def _partition(a, low, high):
    # Median-of-three pivot to avoid worst-case on sorted arrays
    mid = (low + high) // 2
    if a[mid] < a[low]:
        a[low], a[mid] = a[mid], a[low]
    if a[high] < a[low]:
        a[low], a[high] = a[high], a[low]
    if a[mid] < a[high]:
        a[mid], a[high] = a[high], a[mid]
    pivot = a[high]
    i = low - 1
    for j in range(low, high):
        if a[j] <= pivot:
            i += 1
            a[i], a[j] = a[j], a[i]
    a[i + 1], a[high] = a[high], a[i + 1]
    return i + 1


def merge_sort(arr):
    if len(arr) <= 1:
        return arr.copy()
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def insertion_sort(arr):
    a = arr.copy()
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


# Map IDs to (name, function)
ALGORITHMS = {
    1: ("Bubble Sort",     bubble_sort),
    2: ("Selection Sort",  selection_sort),
    3: ("Insertion Sort",  insertion_sort),
    4: ("Merge Sort",      merge_sort),
    5: ("Quick Sort",      quick_sort),
}

COLORS = {
    "Bubble Sort":    "#E63946",
    "Selection Sort": "#F4A261",
    "Insertion Sort": "#2A9D8F",
    "Merge Sort":     "#457B9D",
    "Quick Sort":     "#6A4C93",
}

# array generator
def random_array(n):
    return [random.randint(0, 10 * n) for _ in range(n)]


def nearly_sorted_array(n, noise_pct):
    arr = list(range(n))
    num_swaps = max(1, int(n * noise_pct / 100))
    for _ in range(num_swaps):
        i, j = random.randrange(n), random.randrange(n)
        arr[i], arr[j] = arr[j], arr[i]
    return arr


#timing helper
def measure_time(sort_fn, arr):
    start = time.perf_counter()
    sort_fn(arr)
    return time.perf_counter() - start


def run_experiment(algo_ids, sizes, repetitions, array_gen):
    """
    returns dict: {algo_name: {size: (mean, std)}}
    """
    results = {ALGORITHMS[a][0]: {} for a in algo_ids}

    for size in sizes:
        print(f"  Array size: {size:,}", flush=True)
        
        times = {ALGORITHMS[a][0]: [] for a in algo_ids}

        for _ in range(repetitions):
            arr = array_gen(size)

            for aid in algo_ids:
                name, fn = ALGORITHMS[aid]
                t = measure_time(fn, arr)
                times[name].append(t)

        for aid in algo_ids:
            name = ALGORITHMS[aid][0]
            results[name][size] = (np.mean(times[name]), np.std(times[name]))

    return results


#plotting helper
def plot_results(results, sizes, title, filename):
    fig, ax = plt.subplots(figsize=(11, 6))
    fig.patch.set_facecolor("#0F1117")
    ax.set_facecolor("#1A1D27")

    for spine in ax.spines.values():
        spine.set_color("#2E3248")

    ax.tick_params(colors="#9AA0B8", labelsize=10)
    ax.xaxis.label.set_color("#9AA0B8")
    ax.yaxis.label.set_color("#9AA0B8")

    for name, size_data in results.items():
        xs, ys, errs = [], [], []
        for s in sizes:
            mean, std = size_data.get(s, (None, None))
            if mean is not None:
                xs.append(s)
                ys.append(mean)
                errs.append(std)

        if not xs:
            continue

        color = COLORS.get(name, "#FFFFFF")
        ax.plot(xs, ys, marker="o", label=name, color=color,
                linewidth=2.2, markersize=5, zorder=3)
        ax.fill_between(xs,
                        [y - e for y, e in zip(ys, errs)],
                        [y + e for y, e in zip(ys, errs)],
                        alpha=0.18, color=color)

    ax.set_xlabel("Array size (n)", fontsize=12, labelpad=8)
    ax.set_ylabel("Runtime (seconds)", fontsize=12, labelpad=8)
    ax.set_title(title, fontsize=14, color="#E8EAF6", pad=14, fontweight="bold")
    ax.grid(True, color="#2E3248", linestyle="--", linewidth=0.7, alpha=0.7)
    legend = ax.legend(facecolor="#1A1D27", edgecolor="#2E3248",
                       labelcolor="#E8EAF6", fontsize=10,
                       framealpha=0.9, loc="upper left")

    fig.tight_layout()
    fig.savefig(filename, dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved → {filename}")



# to read cli args
def parse_args():
    parser = argparse.ArgumentParser(
        description="Sorting Algorithm Runtime Comparison"
    )
    parser.add_argument(
        "-a", "--algorithms", nargs="+", type=int, default=[1, 2, 5],
        metavar="ID",
        help="Algorithm IDs: 1=Bubble 2=Selection 3=Insertion 4=Merge 5=Quick"
    )
    parser.add_argument(
        "-s", "--sizes", nargs="+", type=int,
        default=[100, 500, 1000, 3000, 5000, 10000],
        metavar="N",
        help="Array sizes to benchmark"
    )
    parser.add_argument(
        "-e", "--experiment", type=int, default=1,
        choices=[1, 2],
        help="Noise level: 1=5%% noise, 2=20%% noise"
    )
    parser.add_argument(
        "-r", "--repetitions", type=int, default=5,
        metavar="R",
        help="Number of repetitions per (algorithm, size) pair"
    )
    return parser.parse_args()

def print_report(results, sizes):
    algo_names = list(results.keys())
    
    print("\n" + "=" * 65)
    print("  RESULTS REPORT")
    print("=" * 65)
    
    for name in algo_names:
        print(f"\n  {name}")
        print(f"  {'Size':>10} {'Avg Time (s)':>15} {'Std Dev (s)':>15}")
        print(f"  {'-'*10} {'-'*15} {'-'*15}")
        for size in sizes:
            mean, std = results[name].get(size, (None, None))
            if mean is None:
                print(f"  {size:>10,} {'skipped (too slow)':>31}")
            else:
                print(f"  {size:>10,} {mean:>15.6f} {std:>15.6f}")
    
    print("\n" + "=" * 65)


# main function to run the experiments and generate plots
def main():
    sys.setrecursionlimit(500_000)
    args = parse_args()

    # Validate
    for aid in args.algorithms:
        if aid not in ALGORITHMS:
            print(f"Error: Unknown algorithm ID {aid}. Valid IDs: 1-5")
            sys.exit(1)

    noise_pct = 5 if args.experiment == 1 else 20
    algo_names = [ALGORITHMS[a][0] for a in args.algorithms]

    print("=" * 55)
    print("  Sorting Algorithm Benchmark")
    print("=" * 55)
    print(f"  Algorithms : {', '.join(algo_names)}")
    print(f"  Sizes      : {args.sizes}")
    print(f"  Repetitions: {args.repetitions}")
    print(f"  Noise      : {noise_pct}%")
    print("=" * 55)

    # part b: random arrays 
    print("\n[Part B] Random Arrays …")
    results_random = run_experiment(
        args.algorithms, args.sizes, args.repetitions,
        array_gen=random_array
    )
    print_report(results_random, args.sizes)
    plot_results(
        results_random, args.sizes,
        title="Runtime Comparison (Random Arrays)",
        filename="result1.png"
    )

    # part c: nearly sorted arrays with noise
    print(f"\n[Part C] Nearly Sorted Arrays (noise={noise_pct}%) …")
    results_noisy = run_experiment(
        args.algorithms, args.sizes, args.repetitions,
        array_gen=lambda n: nearly_sorted_array(n, noise_pct)
    )
    print_report(results_noisy, args.sizes)
    plot_results(
        results_noisy, args.sizes,
        title=f"Runtime Comparison (Nearly Sorted, noise={noise_pct}%)",
        filename="result2.png"
    )

    print("\nDone! Generated result1.png and result2.png")


if __name__ == "__main__":
    main()