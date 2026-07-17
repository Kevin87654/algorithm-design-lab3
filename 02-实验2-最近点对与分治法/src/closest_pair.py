import math
import random
import matplotlib.pyplot as plt

# ================= 动态可视化辅助设置 =================
# 全局变量，用于记录全局最小距离，方便画图时展示
global_min_d = float('inf')
global_best_pair = None


def draw_state(points, mid_x=None, d=None, current_best_pair=None, title=""):
    """
    负责刷新画面的核心渲染函数
    """
    plt.cla()  # 清空当前画布 (Clear Axis)

    # 1. 画出所有的点
    px_coords = [p[0] for p in points]
    py_coords = [p[1] for p in points]
    plt.scatter(px_coords, py_coords, color='blue', s=30)

    # 2. 如果传了中线坐标，画出中线
    if mid_x is not None:
        plt.axvline(x=mid_x, color='green', linestyle='--', linewidth=2, label='分割线 L')

    # 3. 如果传了最小距离 d，画出带状区域
    if mid_x is not None and d is not None and d != float('inf'):
        plt.axvspan(mid_x - d, mid_x + d, color='yellow', alpha=0.3, label='带状检查区域')
        plt.axvline(x=mid_x - d, color='orange', linestyle=':', linewidth=1)
        plt.axvline(x=mid_x + d, color='orange', linestyle=':', linewidth=1)

    # 4. 如果传了当前最短点对，画出红线
    if current_best_pair:
        p1, p2 = current_best_pair
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], color='red', linewidth=3, label=f'当前最短距离: {dist(p1, p2):.2f}')
        plt.scatter([p1[0], p2[0]], [p1[1], p2[1]], color='red', s=80, zorder=5)

    plt.title(title, fontsize=14)
    plt.xlim(-5, 105)
    plt.ylim(-5, 105)
    plt.legend(loc='upper right')
    plt.grid(True, linestyle='--', alpha=0.5)

    # 【核心！】暂停 0.6 秒，产生动画效果
    plt.pause(0.6)


# ================= 核心算法部分 (加入了画图钩子) =================

def dist(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def brute_force(points, all_points):
    """带画图更新的蛮力法"""
    global global_min_d, global_best_pair
    min_d = float('inf')
    best_pair = None
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            d = dist(points[i], points[j])
            if d < min_d:
                min_d = d
                best_pair = (points[i], points[j])
                # 如果打破了全局记录，更新画面
                if d < global_min_d:
                    global_min_d = d
                    global_best_pair = best_pair
                    draw_state(all_points, current_best_pair=global_best_pair, title="[蛮力法] 找到新的全局最短距离！")
    return min_d, best_pair


def closest_pair_recursive(px, py, all_points):
    global global_min_d, global_best_pair
    n = len(px)
    if n <= 3:
        return brute_force(px, all_points)

    mid = n // 2
    mid_point = px[mid]

    # 【画图钩子 1】：展示当前划分的中线
    draw_state(all_points, mid_x=mid_point[0], current_best_pair=global_best_pair,
               title=f"正在以 X={mid_point[0]:.1f} 划分左右区域...")

    lx = px[:mid]
    rx = px[mid:]
    set_lx = set(lx)
    ly = [p for p in py if p in set_lx]
    ry = [p for p in py if p not in set_lx]

    dl, pair_l = closest_pair_recursive(lx, ly, all_points)
    dr, pair_r = closest_pair_recursive(rx, ry, all_points)

    d = min(dl, dr)
    best_pair = pair_l if dl < dr else pair_r

    # 【画图钩子 2】：展示带状合并区域
    draw_state(all_points, mid_x=mid_point[0], d=d, current_best_pair=global_best_pair,
               title="准备检查跨越中线的带状区域")

    strip = [p for p in py if abs(p[0] - mid_point[0]) < d]
    strip_len = len(strip)

    for i in range(strip_len):
        for j in range(i + 1, min(i + 8, strip_len)):
            d_strip = dist(strip[i], strip[j])
            if d_strip < d:
                d = d_strip
                best_pair = (strip[i], strip[j])
                # 如果跨界合并找到了更短的，更新画面！
                if d < global_min_d:
                    global_min_d = d
                    global_best_pair = best_pair
                    draw_state(all_points, mid_x=mid_point[0], d=d, current_best_pair=global_best_pair,
                               title="[跨界合并] 发现更短的跨界点对！")

    return d, best_pair


def run_animation():
    # 开启交互模式
    plt.ion()
    plt.figure(figsize=(9, 7))

    # 生成 30 个随机点用于演示
    N = 30
    points = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(N)]
    px = sorted(points, key=lambda p: p[0])
    py = sorted(points, key=lambda p: p[1])

    # 初始状态
    draw_state(points, title="初始状态：随机生成散点")
    plt.pause(1.5)

    # 开始执行算法
    closest_pair_recursive(px, py, points)

    # 算法结束，展示最终结果
    draw_state(points, current_best_pair=global_best_pair, title="算法执行完毕！最终最短点对")

    # 关闭交互模式，使最终画面保持住，不会一闪而过
    plt.ioff()
    plt.show()


if __name__ == "__main__":
    run_animation()