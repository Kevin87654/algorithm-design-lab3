#include <algorithm>
#include <chrono>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;
using Clock = chrono::steady_clock;

struct Edge {
    int u;
    int v;
};

struct AdjEdge {
    int to;
    int id;
};

struct Graph {
    int n = 0;
    vector<Edge> edges;
    vector<vector<AdjEdge>> adj;
};

struct DSU {
    vector<int> parent;

    explicit DSU(int n = 0) : parent(n) {
        iota(parent.begin(), parent.end(), 0);
    }

    int find(int x) {
        int root = x;
        while (parent[root] != root) {
            root = parent[root];
        }
        while (parent[x] != x) {
            int next = parent[x];
            parent[x] = root;
            x = next;
        }
        return root;
    }

    void linkRootToRoot(int childRoot, int ancestorRoot) {
        parent[childRoot] = ancestorRoot;
    }
};

void addEdge(Graph& g, int u, int v) {
    int id = static_cast<int>(g.edges.size());
    g.edges.push_back({u, v});
    g.adj[u].push_back({v, id});
    if (u != v) {
        g.adj[v].push_back({u, id});
    }
}

Graph readGraphFromFile(const string& filename) {
    ifstream in(filename);
    if (!in) {
        throw runtime_error("Cannot open file: " + filename);
    }

    Graph g;
    int m = 0;
    in >> g.n >> m;
    if (g.n < 0 || m < 0) {
        throw runtime_error("Invalid graph header in file: " + filename);
    }

    g.adj.assign(g.n, {});
    g.edges.reserve(m);

    int u, v;
    for (int i = 0; i < m; ++i) {
        if (!(in >> u >> v)) {
            throw runtime_error("Not enough edges in file: " + filename);
        }
        if (u < 0 || u >= g.n || v < 0 || v >= g.n) {
            throw runtime_error("Vertex id out of range in file: " + filename);
        }
        addEdge(g, u, v);
    }
    return g;
}

Graph buildFigure2Graph() {
    Graph g;
    g.n = 16;
    g.adj.assign(g.n, {});

    // Vertices are numbered row by row in the 4 x 4 picture.
    addEdge(g, 0, 1);
    addEdge(g, 2, 3);
    addEdge(g, 2, 6);
    addEdge(g, 6, 7);
    addEdge(g, 9, 10);
    addEdge(g, 12, 13);
    return g;
}

int countComponentsIgnoringEdge(const Graph& g, int ignoredEdgeId) {
    vector<unsigned char> visited(g.n, 0);
    vector<int> st;
    st.reserve(g.n == 0 ? 1 : min(g.n, 100000));

    int components = 0;
    for (int start = 0; start < g.n; ++start) {
        if (visited[start]) {
            continue;
        }

        ++components;
        visited[start] = 1;
        st.push_back(start);

        while (!st.empty()) {
            int u = st.back();
            st.pop_back();

            for (const AdjEdge& e : g.adj[u]) {
                if (e.id == ignoredEdgeId) {
                    continue;
                }
                int v = e.to;
                if (!visited[v]) {
                    visited[v] = 1;
                    st.push_back(v);
                }
            }
        }
    }
    return components;
}

vector<int> baselineBridges(const Graph& g) {
    int baseComponents = countComponentsIgnoringEdge(g, -1);
    vector<int> bridges;

    for (int id = 0; id < static_cast<int>(g.edges.size()); ++id) {
        int currentComponents = countComponentsIgnoringEdge(g, id);
        if (currentComponents > baseComponents) {
            bridges.push_back(id);
        }
    }
    return bridges;
}

vector<int> dsuBridges(const Graph& g) {
    int n = g.n;
    int m = static_cast<int>(g.edges.size());

    vector<unsigned char> visited(n, 0);
    vector<unsigned char> isTreeEdge(m, 0);
    vector<unsigned char> collectedNonTree(m, 0);
    vector<unsigned char> isBridge(m, 0);
    vector<int> parent(n, -1);
    vector<int> parentEdge(n, -1);
    vector<int> depth(n, 0);
    vector<int> nextIndex(n, 0);
    vector<int> nonTreeEdges;

    vector<int> st;
    st.reserve(n == 0 ? 1 : min(n, 100000));

    for (int root = 0; root < n; ++root) {
        if (visited[root]) {
            continue;
        }

        visited[root] = 1;
        st.push_back(root);

        while (!st.empty()) {
            int u = st.back();
            if (nextIndex[u] >= static_cast<int>(g.adj[u].size())) {
                st.pop_back();
                continue;
            }

            AdjEdge e = g.adj[u][nextIndex[u]++];
            int v = e.to;
            int id = e.id;

            if (id == parentEdge[u]) {
                continue;
            }

            if (!visited[v]) {
                visited[v] = 1;
                parent[v] = u;
                parentEdge[v] = id;
                depth[v] = depth[u] + 1;
                isTreeEdge[id] = 1;
                isBridge[id] = 1;
                st.push_back(v);
            } else if (!isTreeEdge[id] && !collectedNonTree[id]) {
                collectedNonTree[id] = 1;
                nonTreeEdges.push_back(id);
            }
        }
    }

    DSU dsu(n);
    for (int id : nonTreeEdges) {
        int u = dsu.find(g.edges[id].u);
        int v = dsu.find(g.edges[id].v);

        while (u != v) {
            if (depth[u] < depth[v]) {
                swap(u, v);
            }

            int pe = parentEdge[u];
            if (pe == -1) {
                break;
            }

            isBridge[pe] = 0;
            int p = dsu.find(parent[u]);
            dsu.linkRootToRoot(u, p);
            u = dsu.find(u);
        }
    }

    vector<int> bridges;
    for (int id = 0; id < m; ++id) {
        if (isBridge[id]) {
            bridges.push_back(id);
        }
    }
    return bridges;
}

string edgeToString(const Graph& g, int id) {
    return "(" + to_string(g.edges[id].u) + ", " + to_string(g.edges[id].v) + ")";
}

void printBridgeList(const Graph& g, const vector<int>& bridges) {
    for (int id : bridges) {
        cout << "  " << edgeToString(g, id) << '\n';
    }
}

template <typename Func>
pair<vector<int>, long long> timedRun(Func func) {
    auto start = Clock::now();
    vector<int> result = func();
    auto finish = Clock::now();
    long long ms = chrono::duration_cast<chrono::milliseconds>(finish - start).count();
    return {std::move(result), ms};
}

void runFigure2Test() {
    Graph g = buildFigure2Graph();

    auto baseline = timedRun([&]() { return baselineBridges(g); });
    auto efficient = timedRun([&]() { return dsuBridges(g); });

    vector<int> a = baseline.first;
    vector<int> b = efficient.first;
    sort(a.begin(), a.end());
    sort(b.begin(), b.end());

    cout << "========== Figure 2 correctness test ==========\n";
    cout << "Vertices: " << g.n << ", Edges: " << g.edges.size() << '\n';
    cout << "Expected bridge count: 6\n";
    cout << "Baseline bridge count: " << baseline.first.size()
         << ", time: " << baseline.second << " ms\n";
    cout << "DSU bridge count: " << efficient.first.size()
         << ", time: " << efficient.second << " ms\n";
    cout << "Bridge edges found by DSU algorithm:\n";
    printBridgeList(g, efficient.first);
    cout << "Result: " << ((a == b && b.size() == 6) ? "PASS" : "FAIL") << "\n\n";
}

void runDataSet(const string& filename, bool runBaseline) {
    cout << "========== Dataset: " << filename << " ==========\n";

    auto loadStart = Clock::now();
    Graph g = readGraphFromFile(filename);
    auto loadFinish = Clock::now();
    long long loadMs = chrono::duration_cast<chrono::milliseconds>(loadFinish - loadStart).count();

    cout << "Vertices: " << g.n << ", Edges: " << g.edges.size()
         << ", load time: " << loadMs << " ms\n";

    vector<int> baselineResult;
    if (runBaseline) {
        auto baseline = timedRun([&]() { return baselineBridges(g); });
        baselineResult = baseline.first;
        cout << "Baseline bridge count: " << baseline.first.size()
             << ", time: " << baseline.second << " ms\n";
    } else {
        cout << "Baseline algorithm skipped for this dataset because it is O(E*(V+E)).\n";
        cout << "To force it, run this program with argument: --run-large-baseline\n";
    }

    auto efficient = timedRun([&]() { return dsuBridges(g); });
    cout << "DSU bridge count: " << efficient.first.size()
         << ", time: " << efficient.second << " ms\n";

    if (runBaseline) {
        sort(baselineResult.begin(), baselineResult.end());
        sort(efficient.first.begin(), efficient.first.end());
        cout << "Baseline and DSU results match: "
             << (baselineResult == efficient.first ? "YES" : "NO") << '\n';
    }
    cout << '\n';
}

int main(int argc, char* argv[]) {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    bool runLargeBaseline = false;
    for (int i = 1; i < argc; ++i) {
        if (string(argv[i]) == "--run-large-baseline") {
            runLargeBaseline = true;
        }
    }

    try {
        runFigure2Test();
        runDataSet("mediumG.txt", true);
        runDataSet("largeG.txt", runLargeBaseline);
    } catch (const exception& ex) {
        cerr << "Error: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
