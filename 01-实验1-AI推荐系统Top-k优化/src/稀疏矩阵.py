import time
import random
import matplotlib.pyplot as plt


# --- 1. 稀疏数据的存储与生成 ---
# 稀疏表示如何存储？答：使用字典（哈希表）存储，只记录非零特征的索引和权重。
def generate_sparse_users(n, total_d, s):
    """
    生成稀疏用户数据。
    参数:
      n: 用户总数
      total_d: 总的兴趣维度（例如可能有上万个不同的兴趣标签）
      s: 每个用户实际拥有的非零兴趣个数
    返回:
      包含 n 个字典的列表，每个字典代表一个用户
    """
    users = []
    for _ in range(n):
        # 从总维度中随机挑选 s 个作为该用户的非零兴趣
        active_features = random.sample(range(total_d), s)
        # 为这些非零兴趣随机赋予 0 到 1 之间的权重，使用字典存储
        user_profile = {feature: random.random() for feature in active_features}
        users.append(user_profile)
    return users


# --- 2. 稀疏向量的余弦相似度计算 ---
def sparse_cosine_similarity(user1, user2):
    """
    计算两个稀疏向量（字典）的余弦相似度
    """
    # 优化点：永远遍历长度较短的字典，利用哈希表 O(1) 的查找速度
    if len(user1) > len(user2):
        user1, user2 = user2, user1

    dot_product = 0.0
    for feature, weight1 in user1.items():
        if feature in user2:
            dot_product += weight1 * user2[feature]

    norm1 = sum(w ** 2 for w in user1.values()) ** 0.5
    norm2 = sum(w ** 2 for w in user2.values()) ** 0.5

    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return dot_product / (norm1 * norm2)


def calculate_all_sparse_sims(target_user, all_users):
    """计算目标用户与所有其他稀疏用户的相似度"""
    return [sparse_cosine_similarity(target_user, u) for u in all_users]


# --- 3. 测试不同 s 对算法效率的影响 ---
def test_sparsity_impact():
    """测试不同的非零特征数 s 对整体运行时间的影响"""
    n = 10000  # 保持用户数固定为一万
    total_d = 5000  # 假设总库里有 5000 种兴趣标签
    # 测试不同的 s 值 (非零兴趣个数)
    s_values = [5, 10, 20, 50, 100, 200]

    execution_times = []

    print(f"开始测试稀疏向量效率 (固定用户数 n={n}, 总维度={total_d})")
    print("-" * 40)

    for s in s_values:
        # 1. 生成数据
        all_users = generate_sparse_users(n, total_d, s)
        target_user = all_users[0]

        # 2. 记录计算相似度的耗时
        start_time = time.time()
        # 运行 5 次取平均值以减少误差
        for _ in range(5):
            _ = calculate_all_sparse_sims(target_user, all_users)
        avg_time = (time.time() - start_time) / 5.0

        execution_times.append(avg_time)
        print(f"非零特征数 s={s:<3} | 平均计算耗时: {avg_time:.4f} 秒")

    # 3. 绘制 s 值与运行时间的关系图
    plt.figure(figsize=(8, 5))
    plt.plot(s_values, execution_times, marker='o', color='green', linestyle='-', linewidth=2)
    plt.title('Impact of Non-zero Features (s) on Execution Time')
    plt.xlabel('Number of Non-zero Features (s)')
    plt.ylabel('Average Execution Time (seconds)')
    plt.grid(True, linestyle='--', alpha=0.7)

    # 在图表上添加文本注释解释复杂度变化
    plt.text(50, max(execution_times) * 0.8,
             'Complexity drops from O(d) to O(s)',
             fontsize=12, bbox=dict(facecolor='white', alpha=0.8))

    plt.show()


if __name__ == "__main__":
    test_sparsity_impact()