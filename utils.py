import networkx as nx

def generate_random_connected_graph(n, p=0.3):
    """Retries Erdos-Renyi generation until graph is connected."""
    while True:
        G = nx.erdos_renyi_graph(n, p)
        if nx.is_connected(G):
            return G

cost_dictionary = {
    "msg": 0.01,
    "op": 0.01,
    "mem": 0.1,
}