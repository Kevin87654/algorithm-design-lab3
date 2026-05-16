import time
from collections import defaultdict


class Graph:
    def __init__(self, num_vertices):
        self.V = num_vertices
        self.adj = defaultdict(list)

    def add_edge(self, u, v):
        self.adj[u].append(v)
        self.adj[v].append(u)


def load_col_file(filepath):
    graph = None
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('c'):
                continue
            parts = line.split()
            if parts[0] == 'p':
                num_vertices = int(parts[2])
                graph = Graph(num_vertices)
            elif parts[0] == 'e':
                u = int(parts[1])
                v = int(parts[2])
                graph.add_edge(u, v)
    return graph


# ================= 新增代码 ================= #

class GraphColoringBasic:
    def __init__(self, graph, num_colors):
        self.graph = graph
        self.m = num_colors
        # 记录每个顶点的颜色，0 表示未着色。顶点编号通常从 1 到 V
        self.colors = {i: 0 for i in range(1, graph.V + 1)}

    def is_safe(self, v, c):
        """
        界限函数（约束条件）：判断给顶点 v 涂颜色 c 是否安全
        即：遍历 v 的所有邻居，看看有没有已经被涂成颜色 c 的
        """
        for neighbor in self.graph.adj[v]:
            if self.colors[neighbor] == c:
                return False
        return True

    def backtrack(self, v):
        """
        经典回溯搜索，v 表示当前正在尝试给第 v 个顶点着色
        """
        # 如果 v 大于总顶点数，说明所有顶点都安全着色完毕，找到一个解！
        if v > self.graph.V:
            return True

        # 遍历所有可能的颜色 1 到 m
        for c in range(1, self.m + 1):
            if self.is_safe(v, c):
                self.colors[v] = c  # 做出选择：记录当前顶点的颜色

                if self.backtrack(v + 1):  # 递归探索：给下一个顶点着色
                    return True

                self.colors[v] = 0  # 撤销选择：回溯

        # 所有颜色都尝试了都不行，说明走进了死胡同，返回 False
        return False


def test_small_graph():
    """
    实验要求 1：对一个小规模数据，利用四色填色测试算法的正确性
    """
    print("--- 实验要求 1：测试小规模数据的回溯法正确性 ---")

    # 构造一个小规模数据，例如一个四边形加一条对角线（共4个顶点）
    # 1 --- 2
    # | \   |
    # 4 --- 3
    # 这样的图，顶点 1 连着 2、3、4，所以至少需要 3 种颜色
    g = Graph(4)
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(3, 4)
    g.add_edge(4, 1)
    g.add_edge(1, 3)  # 添加对角线

    num_colors = 4  # 使用 4 色进行测试
    solver = GraphColoringBasic(g, num_colors)

    start_time = time.time()
    if solver.backtrack(1):  # 从顶点 1 开始填色
        print(f"找到解！颜色分配为: {solver.colors}")
    else:
        print("未找到解！")
    print(f"耗时: {time.time() - start_time:.6f} 秒\n")


import sys


class GraphColoringOptimized:
    def __init__(self, graph, num_colors, time_limit=60):
        self.graph = graph
        self.m = num_colors
        self.colors = {i: 0 for i in range(1, graph.V + 1)}
        self.available_colors = {i: set(range(1, num_colors + 1)) for i in range(1, graph.V + 1)}
        self.uncolored = set(range(1, graph.V + 1))
        self.max_color_used = 0

        # 【偷懒/高效优化】：预先计算好每个点的静态度数，避免在递归中重复计算动态度数
        self.degrees = {i: len(graph.adj[i]) for i in range(1, graph.V + 1)}

        # 【进度与超时监控机制】
        self.start_time = time.time()
        self.time_limit = time_limit  # 默认设置为 60 秒超时
        self.nodes_visited = 0  # 记录搜索树展开的节点数
        self.timeout_flag = False  # 超时标志

    def select_unassigned_variable(self):
        """ 选点策略：MRV + 静态度数(Tie-breaker) """
        best_v = -1
        min_avail = float('inf')
        max_deg = -1

        for v in self.uncolored:
            avail = len(self.available_colors[v])
            if avail < min_avail:
                min_avail = avail
                max_deg = self.degrees[v]
                best_v = v
            elif avail == min_avail:
                # O(1) 复杂度的查表，极大地加快了 Python 的运行速度！
                if self.degrees[v] > max_deg:
                    max_deg = self.degrees[v]
                    best_v = v
        return best_v

    def forward_check(self, u, c):
        modified_neighbors = []
        for neighbor in self.graph.adj[u]:
            if self.colors[neighbor] == 0 and c in self.available_colors[neighbor]:
                self.available_colors[neighbor].remove(c)
                modified_neighbors.append(neighbor)

                if len(self.available_colors[neighbor]) == 0:
                    for modified_node in modified_neighbors:
                        self.available_colors[modified_node].add(c)
                    return None
        return modified_neighbors

    def backtrack(self):
        # 1. 监控超时
        if time.time() - self.start_time > self.time_limit:
            self.timeout_flag = True
            return False

        # 2. 进度打印：每搜索 20000 个节点打印一次状态
        self.nodes_visited += 1
        if self.nodes_visited % 20000 == 0:
            elapsed = time.time() - self.start_time
            print(f"   [监控] 已搜索节点数: {self.nodes_visited}, 已耗时: {elapsed:.1f}秒...")

        # 3. 递归出口
        if not self.uncolored:
            return True

        v = self.select_unassigned_variable()
        self.uncolored.remove(v)

        color_limit = min(self.max_color_used + 1, self.m)
        colors_to_try = [c for c in range(1, color_limit + 1) if c in self.available_colors[v]]

        for c in colors_to_try:
            modified_neighbors = self.forward_check(v, c)

            if modified_neighbors is not None:
                self.colors[v] = c
                prev_max = self.max_color_used
                if c > self.max_color_used:
                    self.max_color_used = c

                if self.backtrack():
                    return True

                # 接收到深层传递的超时标志，立刻停止回溯，层层退出
                if self.timeout_flag:
                    return False

                self.colors[v] = 0
                self.max_color_used = prev_max
                for neighbor in modified_neighbors:
                    self.available_colors[neighbor].add(c)

        self.uncolored.add(v)
        return False


def run_dataset(filename, num_colors):
    print(f"\n开始处理数据集: {filename}，尝试使用 {num_colors} 种颜色着色...")
    g = load_col_file(f"data/{filename}")
    if g is None:
        return

    solver = GraphColoringOptimized(g, num_colors, time_limit=60)  # 设置 60 秒超时
    start_time = time.time()

    if solver.backtrack():
        print(f"[{filename}] 找到解！耗时: {time.time() - start_time:.4f} 秒, 总搜索节点数: {solver.nodes_visited}")
        preview = {i: solver.colors[i] for i in range(1, 11)}
        print(f"前10个节点的颜色分配预览: {preview}")
    else:
        if solver.timeout_flag:
            print(
                f"[{filename}] 触发超时保护（>60秒）！由于 NP完全问题的指数级复杂度，当前剪枝策略在限定时间内无法穷尽搜索树。")
        else:
            print(f"[{filename}] 搜索完毕，未找到解！耗时: {time.time() - start_time:.4f} 秒")

if __name__ == '__main__':
    # 1. 运行小规模图测试
    test_small_graph()

    # 2. 运行附件中的三个大数据集
    # le450_5a 要求 5 种颜色
    run_dataset("le450_5a.col", 5)

    # le450_15b 要求 15 种颜色
    run_dataset("le450_15b.col", 15)

    # le450_25a 要求 25 种颜色
    run_dataset("le450_25a.col", 25)