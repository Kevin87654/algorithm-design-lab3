import numpy as np
import time
import heapq
import matplotlib.pyplot as plt
import random


# ================= 1. 数据生成与相似度计算 =================
def generate_dense_data(n, d=50):
    return np.random.rand(n, d)


def calculate_dense_similarities(target_user, all_users):
    dot_products = np.dot(all_users, target_user)
    norms_target = np.linalg.norm(target_user)
    norms_all = np.linalg.norm(all_users, axis=1)
    similarities = dot_products / (norms_target * norms_all + 1e-10)
    return similarities


# ================= 2. 四种排序算法实现 =================
def quick_sort_top_k(similarities, k):
    """1. 快速排序 (全量排序) O(n log n)"""
    sorted_indices = np.argsort(similarities, kind='quicksort')[::-1]
    return sorted_indices[:k]


def merge_sort_top_k(similarities, k):
    """2. 归并排序 (全量排序) O(n log n)"""
    sorted_indices = np.argsort(similarities, kind='mergesort')[::-1]
    return sorted_indices[:k]


def selection_sort_top_k(similarities, k):
    """3. 部分选择排序 (只选前k个) O(n * k)"""
    sims = similarities.copy()  # 避免修改原数组
    top_k_indices = []
    for _ in range(k):
        max_idx = np.argmax(sims)
        top_k_indices.append(max_idx)
        sims[max_idx] = -float('inf')  # 标记为已访问
    return top_k_indices


def heap_top_k(similarities, k):
    """4. 最小堆优化算法 O(n log k)"""
    top_k_heap = []
    for i, sim in enumerate(similarities):
        if len(top_k_heap) < k:
            heapq.heappush(top_k_heap, (sim, i))
        elif sim > top_k_heap[0][0]:
            heapq.heapreplace(top_k_heap, (sim, i))
    return [idx for sim, idx in sorted(top_k_heap, key=lambda x: x[0], reverse=True)]


# ================= 3. 核心实验与绘图逻辑 =================
def run_comparison_experiment(k_value):
    n_values = [1000, 3000, 5000, 7000, 10000]  # 横坐标均匀取值
    d = 50
    samples = 20  # 20个随机样本

    times_quick = []
    times_merge = []
    times_selection = []
    times_heap = []

    print(f"开始运行实验，当前 k = {k_value}...")

    for n in n_values:
        all_users = generate_dense_data(n, d)
        target_user = all_users[0]

        # 预先计算出20个样本的相似度，避免把相似度计算时间计入排序时间
        sims_list = [calculate_dense_similarities(target_user, generate_dense_data(n, d)) for _ in range(samples)]

        # 测试 Quick Sort
        start = time.time()
        for sims in sims_list: quick_sort_top_k(sims, k_value)
        times_quick.append((time.time() - start) / samples)

        # 测试 Merge Sort
        start = time.time()
        for sims in sims_list: merge_sort_top_k(sims, k_value)
        times_merge.append((time.time() - start) / samples)

        # 测试 Selection Sort
        start = time.time()
        for sims in sims_list: selection_sort_top_k(sims, k_value)
        times_selection.append((time.time() - start) / samples)

        # 测试 Min-Heap
        start = time.time()
        for sims in sims_list: heap_top_k(sims, k_value)
        times_heap.append((time.time() - start) / samples)

    # ================= 绘制实测与理论对比图 =================
    plt.figure(figsize=(12, 8))

    # 绘制实测曲线
    plt.plot(n_values, times_quick, label='Actual Quick Sort O(n log n)', marker='o', color='blue')
    plt.plot(n_values, times_merge, label='Actual Merge Sort O(n log n)', marker='v', color='purple')
    plt.plot(n_values, times_selection, label=f'Actual Selection Sort O(n*{k_value})', marker='x', color='green')
    plt.plot(n_values, times_heap, label='Actual Min-Heap O(n log k)', marker='s', color='red')

    # 绘制理论曲线 (以最大规模 n=10000 的时间为基准进行常数C缩放调整)
    base_idx = -1
    n_base = n_values[base_idx]

    # O(n log n) 理论拟合
    c_nlogn = times_quick[base_idx] / (n_base * np.log2(n_base))
    theory_nlogn = [c_nlogn * (n * np.log2(n)) for n in n_values]
    plt.plot(n_values, theory_nlogn, '--', color='blue', alpha=0.5, label='Theory O(n log n)')

    # O(n*k) 理论拟合
    c_nk = times_selection[base_idx] / (n_base * k_value)
    theory_nk = [c_nk * (n * k_value) for n in n_values]
    plt.plot(n_values, theory_nk, '--', color='green', alpha=0.5, label=f'Theory O(n*{k_value})')

    plt.xlabel('Number of Users (n)')
    plt.ylabel('Average Time (seconds)')
    plt.title(f'Algorithm Efficiency Comparison (k={k_value})')
    plt.legend()
    plt.grid(True)
    plt.show()


# ================= 4. 稀疏向量选做题部分 =================
def generate_sparse_data(n, d, s):
    return [{idx: random.random() for idx in random.sample(range(d), s)} for _ in range(n)]


def calc_sparse_sim(u1, u2):
    if len(u1) > len(u2): u1, u2 = u2, u1
    dot_product = sum(val * u2[key] for key, val in u1.items() if key in u2)
    norm1 = sum(v ** 2 for v in u1.values()) ** 0.5
    norm2 = sum(v ** 2 for v in u2.values()) ** 0.5
    return dot_product / (norm1 * norm2) if norm1 and norm2 else 0.0


if __name__ == "__main__":
    # 1. 绘制固定 k=10 的多算法对比曲线
    run_comparison_experiment(k_value=10)
    # 2. 绘制固定 k=50 的多算法对比曲线
    run_comparison_experiment(k_value=50)