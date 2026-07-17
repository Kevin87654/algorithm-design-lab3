import math
import time
import random
import sys
import matplotlib.pyplot as plt

# 全局配置：提高递归深度，避免大数据量递归报错
sys.setrecursionlimit(2000000)


# 固定随机种子（可选），保证每次运行结果一致，方便实验测试
# random.seed(100)

# -------------------------- 核心工具函数 --------------------------
def dist(p1: tuple, p2: tuple) -> float:
    """
    计算两个二维点之间的欧几里得距离
    :param p1: 点1 (x1, y1)
    :param p2: 点2 (x2, y2)
    :return: 两点间距离
    """
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


# -------------------------- 蛮力算法 O(n²) --------------------------
def brute_force(points: list) -> tuple[float, tuple]:
    """
    蛮力法求解最近点对，适用于小规模数据
    :param points: 点集列表
    :return: 最短距离, 最近点对
    """
    min_dist = float('inf')
    best_pair = None
    n = len(points)

    for i in range(n):
        for j in range(i + 1, n):
            current_dist = dist(points[i], points[j])
            if current_dist < min_dist:
                min_dist = current_dist
                best_pair = (points[i], points[j])
    return min_dist, best_pair


# -------------------------- 分治算法 O(nlogn) --------------------------
def closest_pair_recursive(px: list, py: list) -> tuple[float, tuple]:
    """
    分治法递归求解最近点对
    :param px: 按x坐标排序的点集
    :param py: 按y坐标排序的点集
    :return: 最短距离, 最近点对
    """
    n = len(px)
    # 递归终止条件：点数≤3，直接用蛮力法
    if n <= 3:
        return brute_force(px)

    # 分割点集：左右两部分
    mid = n // 2
    mid_point = px[mid]
    left_x = px[:mid]
    right_x = px[mid:]

    # 划分y坐标有序的左右子集（保持排序状态）
    left_set = set(left_x)
    left_y = [p for p in py if p in left_set]
    right_y = [p for p in py if p not in left_set]

    # 递归求解左右子区域的最近点对
    left_dist, left_pair = closest_pair_recursive(left_x, left_y)
    right_dist, right_pair = closest_pair_recursive(right_x, right_y)

    # 取左右区域的最小距离
    if left_dist < right_dist:
        current_min = left_dist
        best_pair = left_pair
    else:
        current_min = right_dist
        best_pair = right_pair

    # 筛选跨越中线的带状区域点集
    strip = [p for p in py if abs(p[0] - mid_point[0]) < current_min]
    strip_len = len(strip)

    # 几何性质：内层循环最多执行6~7次，保证线性时间
    for i in range(strip_len):
        for j in range(i + 1, min(i + 8, strip_len)):
            strip_dist = dist(strip[i], strip[j])
            if strip_dist < current_min:
                current_min = strip_dist
                best_pair = (strip[i], strip[j])

    return current_min, best_pair


def solve_closest_pair(points: list) -> tuple[float, tuple]:
    """
    分治法入口函数：预处理排序 + 调用递归
    :param points: 原始点集
    :return: 最短距离, 最近点对
    """
    # 预处理：分别按x、y坐标排序
    px_sorted = sorted(points, key=lambda p: p[0])
    py_sorted = sorted(points, key=lambda p: p[1])
    return closest_pair_recursive(px_sorted, py_sorted)


# -------------------------- 实验测试模块 --------------------------
def run_performance_test():
    """性能对比测试：分治法 VS 蛮力法"""
    print("=" * 50)
    print("          最近点对算法 性能测试")
    print("=" * 50)

    # 测试数据规模（可自行修改）
    test_sizes = [1000, 5000, 10000, 50000, 100000]

    for n in test_sizes:
        print(f"\n📊 数据量 N = {n}")
        # 随机生成二维点
        points = [(random.uniform(0, 10000), random.uniform(0, 10000)) for _ in range(n)]

        # 测试分治法
        start = time.perf_counter()
        div_dist, div_pair = solve_closest_pair(points)
        div_time = time.perf_counter() - start
        print(f"分治法  耗时：{div_time:.4f}s | 最短距离：{div_dist:.4f}")

        # 蛮力法保护：超过10000数据跳过，防止卡死
        if n <= 10000:
            start = time.perf_counter()
            bf_dist, bf_pair = brute_force(points)
            bf_time = time.perf_counter() - start
            print(f"蛮力法  耗时：{bf_time:.4f}s | 最短距离：{bf_dist:.4f}")
        else:
            print("蛮力法  数据量过大，已跳过（O(n²)复杂度耗时极长）")


def run_visualization():
    """最近点对可视化展示（实验加分项）"""
    print("\n" + "=" * 50)
    print("          最近点对 可视化展示")
    print("=" * 50)

    # 可视化用50个点（图表清晰）
    n = 50
    points = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(n)]
    min_dist, best_pair = solve_closest_pair(points)

    # 绘制所有点
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    plt.figure(figsize=(10, 7))
    plt.scatter(x, y, c='steelblue', s=30, label='所有点')

    # 高亮最近点对并连线
    p1, p2 = best_pair
    plt.plot([p1[0], p2[0]], [p1[1], p2[1]], c='crimson', linewidth=3, label=f'最近点对(距离={min_dist:.2f})')
    plt.scatter([p1[0], p2[0]], [p1[1], p2[1]], c='crimson', s=100, edgecolors='black')

    # 图表样式
    plt.title(f'分治法求解最近点对 (点数量={n})', fontsize=14)
    plt.xlabel('X 坐标', fontsize=12)
    plt.ylabel('Y 坐标', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    print("✅ 图表已生成，关闭窗口后程序结束")
    plt.show()


# -------------------------- 主程序入口 --------------------------
if __name__ == "__main__":
    # 运行性能测试
    run_performance_test()
    # 运行可视化展示
    run_visualization()