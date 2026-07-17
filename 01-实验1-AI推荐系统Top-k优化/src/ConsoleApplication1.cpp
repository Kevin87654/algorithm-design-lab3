#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <queue>
#include <chrono>
#include <random>
#include <iomanip>

using namespace std;
using namespace std::chrono;

// 1. 数据生成
vector<vector<double>> generate_data(int n, int d) {
    vector<vector<double>> data(n, vector<double>(d));
    mt19937 gen(12345);
    uniform_real_distribution<double> dis(0.0, 1.0);
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < d; ++j) {
            data[i][j] = dis(gen);
        }
    }
    return data;
}

// 2. 余弦相似度计算
vector<double> calculate_similarities(const vector<double>& target, const vector<vector<double>>& all_users) {
    int n = all_users.size();
    int d = target.size();
    vector<double> similarities(n, 0.0);
    double target_norm = 0.0;
    for (int i = 0; i < d; ++i) target_norm += target[i] * target[i];
    target_norm = sqrt(target_norm);

    for (int i = 0; i < n; ++i) {
        double dot_product = 0.0;
        double current_norm = 0.0;
        for (int j = 0; j < d; ++j) {
            dot_product += target[j] * all_users[i][j];
            current_norm += all_users[i][j] * all_users[i][j];
        }
        current_norm = sqrt(current_norm);
        similarities[i] = dot_product / (target_norm * current_norm + 1e-10);
    }
    return similarities;
}

// 3. 排序算法
void quick_sort_top_k(vector<double> sims, int k) { sort(sims.begin(), sims.end(), greater<double>()); }
void merge_sort_top_k(vector<double> sims, int k) { stable_sort(sims.begin(), sims.end(), greater<double>()); }
void selection_sort_top_k(vector<double> sims, int k) {
    for (int step = 0; step < k; ++step) {
        auto max_it = max_element(sims.begin(), sims.end());
        *max_it = -1.0;
    }
}
void heap_top_k(const vector<double>& sims, int k) {
    priority_queue<double, vector<double>, greater<double>> min_heap;
    for (double sim : sims) {
        if (min_heap.size() < k) min_heap.push(sim);
        else if (sim > min_heap.top()) { min_heap.pop(); min_heap.push(sim); }
    }
}

// 4. 核心实验与理论值计算
void run_experiment_for_k(int k_value) {
    vector<double> n_values = { 1000, 3000, 5000, 7000, 10000 };
    int d = 50;
    int samples = 20;

    vector<double> t_quick, t_merge, t_sel, t_heap;

    cout << "正在运行 k = " << k_value << " 的压测，请稍候..." << endl;

    for (double n : n_values) {
        auto all_users = generate_data(n, d);
        auto target_user = all_users[0];
        vector<vector<double>> sims_list(samples);
        for (int i = 0; i < samples; ++i) sims_list[i] = calculate_similarities(target_user, generate_data(n, d));

        auto start = high_resolution_clock::now();
        for (int i = 0; i < samples; ++i) quick_sort_top_k(sims_list[i], k_value);
        t_quick.push_back(duration_cast<microseconds>(high_resolution_clock::now() - start).count() / (double)samples / 1000.0);

        start = high_resolution_clock::now();
        for (int i = 0; i < samples; ++i) merge_sort_top_k(sims_list[i], k_value);
        t_merge.push_back(duration_cast<microseconds>(high_resolution_clock::now() - start).count() / (double)samples / 1000.0);

        start = high_resolution_clock::now();
        for (int i = 0; i < samples; ++i) selection_sort_top_k(sims_list[i], k_value);
        t_sel.push_back(duration_cast<microseconds>(high_resolution_clock::now() - start).count() / (double)samples / 1000.0);

        start = high_resolution_clock::now();
        for (int i = 0; i < samples; ++i) heap_top_k(sims_list[i], k_value);
        t_heap.push_back(duration_cast<microseconds>(high_resolution_clock::now() - start).count() / (double)samples / 1000.0);
    }

    // 计算理论拟合曲线的常数 C (以最大的 n=10000 为基准点)
    double n_base = n_values.back();
    double c_nlogn = t_quick.back() / (n_base * log2(n_base)); // 拟合快排 O(n log n)
    double c_nk = t_sel.back() / (n_base * k_value);           // 拟合选择排序 O(n*k)

    // 打印 Excel 格式表头 (第一列故意留空，方便 Excel 识别为横坐标)
    cout << "\n=== 以下数据可直接复制到 Excel (k=" << k_value << ") ===" << endl;
    cout << " \tQuick Sort\tMerge Sort\tSelection Sort\tMin-Heap\tTheory O(n log n)\tTheory O(n*k)" << endl;

    for (size_t i = 0; i < n_values.size(); ++i) {
        double n = n_values[i];
        double theory_nlogn = c_nlogn * (n * log2(n));
        double theory_nk = c_nk * (n * k_value);

        cout << fixed << setprecision(4)
            << (int)n << "\t"
            << t_quick[i] << "\t"
            << t_merge[i] << "\t"
            << t_sel[i] << "\t"
            << t_heap[i] << "\t"
            << theory_nlogn << "\t"
            << theory_nk << endl;
    }
    cout << "========================================================\n" << endl;
}

int main() {
    run_experiment_for_k(10); // 生成 k=10 的数据
    run_experiment_for_k(50); // 生成 k=50 的数据
    return 0;
}