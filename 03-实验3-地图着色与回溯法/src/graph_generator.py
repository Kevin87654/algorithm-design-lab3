import random
import time
import matplotlib.pyplot as plt

# 从我们刚才写的 main.py 中导入图结构和优化后的求解器
from main import Graph, GraphColoringOptimized

# 设置字体，防止画图时中文变成方块
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


def generate_random_graph(num_vertices, avg_degree=4):
    """
    生成随机图。
    为了模拟真实的"地图"（平面图性质），我们控制它的平均度数较低
    （例如每个州平均和 4 个州接壤）。
    边生成的概率 p = 平均度 / 潜在最大邻居数
    """
    g = Graph(num_vertices)
    if num_vertices <= 1:
        return g

    p = avg_degree / (num_vertices - 1)

    # 随机生成边
    for i in range(1, num_vertices + 1):
        for j in range(i + 1, num_vertices + 1):
            if random.random() < p:
                g.add_edge(i, j)
    return g


def run_experiment():
    # 图的规模 V 的测试列表 (从 50 到 500)
    vertex_sizes = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]
    execution_times = []

    # 统一尝试用 5 种颜色着色（真实地图 4 色就够，我们给 5 色保证较快出解）
    num_colors = 5

    print("--- 开始实验要求 4：图规模与算法效率的关系测试 ---\n")

    for v in vertex_sizes:
        # 生成平均度为 4 的随机图
        g = generate_random_graph(v, avg_degree=4)

        # 初始化求解器，设置一个 10 秒超时（防止随机生成的图刚好很变态卡死）
        solver = GraphColoringOptimized(g, num_colors, time_limit=10)

        start_time = time.time()
        success = solver.backtrack()
        cost_time = time.time() - start_time

        execution_times.append(cost_time)

        # 记录运行状态
        status = "找到解" if success else ("超时" if solver.timeout_flag else "无解")
        print(f"规模 V={v:3d}, 边数={sum(len(g.adj[i]) for i in range(1, v + 1)) // 2:4d} "
              f"-> 状态: {status}, 耗时: {cost_time:.4f} 秒, 搜索节点: {solver.nodes_visited}")

    # ================= 开始画折线图 ================= #
    plt.figure(figsize=(10, 6))
    plt.plot(vertex_sizes, execution_times, marker='o', linestyle='-', color='#d62728', linewidth=2, markersize=8)

    plt.title('图着色回溯算法：图规模(顶点数)与执行效率的关系', fontsize=16, pad=15)
    plt.xlabel('图的规模 (顶点数 N)', fontsize=14)
    plt.ylabel('执行时间 (秒)', fontsize=14)

    # 加上网格线让图表看起来更学术
    plt.grid(True, linestyle='--', alpha=0.6)

    # 保存图片到当前目录
    plt.savefig('scale_vs_time.png', dpi=300, bbox_inches='tight')
    print("\n测试完成！已生成折线图并保存为当前目录下的 'scale_vs_time.png'。")

    # 弹出展示窗口
    plt.show()


if __name__ == '__main__':
    run_experiment()