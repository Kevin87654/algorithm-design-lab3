#include <iostream>
#include <vector>
#include <string>
#include <queue>
#include <algorithm>

using namespace std;

// 使用最基础的 Edmonds-Karp 算法求最大流（邻接矩阵实现，更容易理解）
bool bfs(vector<vector<int>>& graph, int s, int t, vector<int>& parent) {
    int V = graph.size();
    vector<bool> visited(V, false);
    queue<int> q;

    q.push(s);
    visited[s] = true;
    parent[s] = -1;

    while (!q.empty()) {
        int u = q.front();
        q.pop();

        for (int v = 0; v < V; v++) {
            if (!visited[v] && graph[u][v] > 0) { // 如果有残余容量
                if (v == t) {
                    parent[v] = u;
                    return true;
                }
                q.push(v);
                parent[v] = u;
                visited[v] = true;
            }
        }
    }
    return false;
}

int getMaxFlow(vector<vector<int>> graph, int s, int t) {
    int max_flow = 0;
    vector<int> parent(graph.size());

    while (bfs(graph, s, t, parent)) {
        int path_flow = 1e9; // 找这条路径上的瓶颈容量
        for (int v = t; v != s; v = parent[v]) {
            int u = parent[v];
            path_flow = min(path_flow, graph[u][v]);
        }
        // 更新残余网络
        for (int v = t; v != s; v = parent[v]) {
            int u = parent[v];
            graph[u][v] -= path_flow;
            graph[v][u] += path_flow;
        }
        max_flow += path_flow;
    }
    return max_flow;
}

void checkTeam(int x, vector<string>& teams, vector<int>& wins, vector<int>& left, vector<vector<int>>& g) {
    int n = teams.size();
    int max_possible_wins = wins[x] + left[x];

    // 1. 简单的平凡淘汰：如果全赢也比不过别人现在的胜场，直接淘汰
    for (int i = 0; i < n; ++i) {
        if (wins[i] > max_possible_wins) {
            cout << teams[x] << ": 被淘汰 (即使全赢也达不到最高分)" << endl;
            return;
        }
    }

    // 2. 构建流网络
    // 节点分配：0是源点，1到6是比赛节点(最多4支队伍C(4,2)=6场)，7到10是队伍节点，11是汇点
    int num_games = 0;
    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            if (i != x && j != x && g[i][j] > 0) num_games++;
        }
    }

    int total_nodes = 1 + num_games + n + 1;
    int source = 0;
    int sink = total_nodes - 1;
    vector<vector<int>> graph(total_nodes, vector<int>(total_nodes, 0));

    int game_node = 1;
    int total_remaining_games = 0; // 记录总的剩余比赛容量

    for (int i = 0; i < n; ++i) {
        if (i == x) continue;

        // 队伍节点连向汇点
        int team_node_i = 1 + num_games + i;
        graph[team_node_i][sink] = max_possible_wins - wins[i];

        for (int j = i + 1; j < n; ++j) {
            if (j == x || g[i][j] == 0) continue;

            // 源点连向比赛节点
            graph[source][game_node] = g[i][j];
            total_remaining_games += g[i][j];

            // 比赛节点连向对阵的两支队伍 (容量无穷大，这里用 1000 代表)
            int team_node_j = 1 + num_games + j;
            graph[game_node][team_node_i] = 1000;
            graph[game_node][team_node_j] = 1000;

            game_node++;
        }
    }

    // 3. 计算最大流并判断
    int max_flow = getMaxFlow(graph, source, sink);

    if (max_flow < total_remaining_games) {
        cout << teams[x] << ": 被淘汰 (剩余比赛无法合理分配)" << endl;
    }
    else {
        cout << teams[x] << ": 仍有机会夺冠！" << endl;
    }
}

int main() {
    // 直接录入截图表格中的数据
    vector<string> teams = { "Atlanta", "Philly", "New York", "Montreal" };
    vector<int> wins = { 83, 80, 78, 77 };
    vector<int> left = { 8, 3, 6, 3 };
    vector<vector<int>> g = {
        {0, 1, 6, 1}, // Atlanta 对阵情况
        {1, 0, 0, 2}, // Philly
        {6, 0, 0, 0}, // New York
        {1, 2, 0, 0}  // Montreal
    };

    cout << "--- 赛季最终预测 ---" << endl;
    for (int i = 0; i < 4; ++i) {
        checkTeam(i, teams, wins, left, g);
    }

    return 0;
}