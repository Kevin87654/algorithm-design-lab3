import math
import time
import random
import sys
import numpy as np
import matplotlib.pyplot as plt

# 1. 初始化设置
# 提高递归深度限制，防止 N 达到 100 万时报错
sys.setrecursionlimit(2000000)

# 设置 matplotlib 中文字体，防止图表中的中文变成方块 (Windows 系统默认黑体)
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


# ================= 第一部分：核心算法实现 =================

def dist(p1, p2):
    """计算两点之间的欧氏距离"""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def brute_force(points):
    """蛮力法：O(N^2)"""
    min_d = float('inf')
    best_pair = None
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            d = dist(points[i], points[j])
            if d < min_d:
                min_d = d
                best_pair = (points[i], points[j])
    return min_d, best_pair


def closest_pair_recursive(px, py):
    """分治法核心递归：O(N log N)"""
    n = len(px)
    if n <= 3:
        return brute_force(px)

    mid = n // 2
    mid_point = px[mid]

    lx = px[:mid]
    rx = px[mid:]

    set_lx = set(lx)
    ly = [p for p in py if p in set_lx]
    ry = [p for p in py if p not in set_lx]

    dl, pair_l = closest_pair_recursive(lx, ly)
    dr, pair_r = closest_pair_recursive(rx, ry)

    d = dl
    best_pair = pair_l
    if dr < dl:
        d = dr
        best_pair = pair_r

    # 处理跨越中线的带状区域 (剪枝，确保线性效率)
    strip = [p for p in py if abs(p[0] - mid_point[0]) < d]
    strip_len = len(strip)
    for i in range(strip_len):
        for j in range(i + 1, min(i + 8, strip_len)):
            d_strip = dist(strip[i], strip[j])
            if d_strip < d:
                d = d_strip
                best_pair = (strip[i], strip[j])

    return d, best_pair


def solve_closest_pair(points):
    """算法入口，处理预排序"""
    px = sorted(points, key=lambda p: p[0])
    py = sorted(points, key=lambda p: p[1])
    return closest_pair_recursive(px, py)


# ================= 第二部分：自动测试与可视化绘图 =================

def run_experiment_and_plot():
    print("正在进行基准测试 (N=10000)，请稍候...")
    n_base = 10000
    points = [(random.uniform(0, 10000), random.uniform(0, 10000)) for _ in range(n_base)]

    # 测算蛮力法时间
    start_time = time.time()
    brute_force(points)
    t_bf_base = time.time() - start_time

    # 测算分治法时间
    start_time = time.time()
    solve_closest_pair(points)
    t_dc_base = time.time() - start_time

    print(f"基准测试完成！\n蛮力法耗时: {t_bf_base:.4f} 秒\n分治法耗时: {t_dc_base:.4f} 秒\n")
    print("正在生成数据量高达 1,000,000 的理论分析图表...")

    # 使用 numpy 生成从 1万 到 100万 之间的 15 个点
    N_values = np.linspace(10000, 1000000, 100)  # 用于画平滑曲线
    key_N = np.linspace(10000, 1000000, 15)  # 用于打散点

    # 根据你的电脑真实性能，推算理论时间
    T_bf_curve = t_bf_base * (N_values / n_base) ** 2
    key_T_bf = t_bf_base * (key_N / n_base) ** 2

    base_log_factor = n_base * np.log(n_base)
    T_dc_curve = t_dc_base * (N_values * np.log(N_values)) / base_log_factor
    key_T_dc = t_dc_base * (key_N * np.log(key_N)) / base_log_factor

    # 开始绘制双子图画布
    plt.figure(figsize=(14, 6))

    # 子图 1：普通线性图
    plt.subplot(1, 2, 1)
    plt.plot(N_values, T_bf_curve, color='red', label='蛮力法 O(N^2) 推算时间', linewidth=2)
    plt.plot(N_values, T_dc_curve, color='blue', label='分治法 O(N log N) 推算时间', linewidth=2)
    plt.scatter(key_N, key_T_bf, color='darkred', zorder=5)
    plt.scatter(key_N, key_T_dc, color='darkblue', zorder=5)

    plt.title('时间复杂度对比（普通坐标轴）', fontsize=14)
    plt.xlabel('数据规模 N', fontsize=12)
    plt.ylabel('耗时 (秒)', fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.ticklabel_format(style='plain', axis='x')

    # 子图 2：对数坐标图
    plt.subplot(1, 2, 2)
    plt.plot(N_values, T_bf_curve, color='red', label='蛮力法 O(N^2) 推算时间', linewidth=2)
    plt.plot(N_values, T_dc_curve, color='blue', label='分治法 O(N log N) 推算时间', linewidth=2)
    plt.scatter(key_N, key_T_bf, color='darkred', zorder=5)
    plt.scatter(key_N, key_T_dc, color='darkblue', zorder=5)

    plt.title('时间复杂度对比（Y轴对数坐标）', fontsize=14)
    plt.xlabel('数据规模 N', fontsize=12)
    plt.ylabel('耗时 (秒) - 对数刻度', fontsize=12)
    plt.yscale('log')  # 关键：对数刻度
    plt.legend(fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.6, which='both')
    plt.ticklabel_format(style='plain', axis='x')

    plt.tight_layout()
    print("图表已生成，请在弹出的窗口中查看或保存截图！")
    plt.show()


if __name__ == "__main__":
    run_experiment_and_plot()