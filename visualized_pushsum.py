import random
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

NUMBER_OF_AGENTS = 10

class Node:
    def __init__(self, node_id, initial_value):
        self.id = node_id
        self.s = float(initial_value)
        self.w = 1.0
        self.neighbors = []
        self.inbox_s = 0.0
        self.inbox_w = 0.0
        self.last_target_id = None

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def send_message(self):
        if not self.neighbors:
            self.last_target_id = None
            return
        self.s /= 2.0
        self.w /= 2.0
        target = random.choice(self.neighbors)
        self.last_target_id = target.id
        target.receive_message(self.s, self.w)

    def receive_message(self, received_s, received_w):
        self.inbox_s += received_s
        self.inbox_w += received_w

    def update_state(self):
        self.s += self.inbox_s
        self.w += self.inbox_w
        self.inbox_s = 0.0
        self.inbox_w = 0.0

    def get_estimate(self):
        return self.s / self.w if self.w != 0 else 0


def run_animated_push_sum(num_agents=10, max_rounds=100):
    G = nx.erdos_renyi_graph(num_agents, p=0.25)
    while not nx.is_connected(G):
        G = nx.erdos_renyi_graph(num_agents, p=0.25)

    pos = nx.spring_layout(G, seed=42)
    initial_values = [random.randint(1, 100) for _ in range(num_agents)]
    true_avg = sum(initial_values) / num_agents
    agents = [Node(i, val) for i, val in enumerate(initial_values)]

    for u, v in G.edges():
        agents[u].add_neighbor(agents[v])
        agents[v].add_neighbor(agents[u])

    fig, ax = plt.subplots(figsize=(10, 7))

    def update(frame):
        ax.clear()

        message_edges = []
        for a in agents:
            a.send_message()
            if a.last_target_id is not None:
                message_edges.append((a.id, a.last_target_id))
        for a in agents:
            a.update_state()

        estimates = [a.get_estimate() for a in agents]

        nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.4, edge_color='gray')

        if message_edges:
            nx.draw_networkx_edges(
                G, pos, edgelist=message_edges, ax=ax,
                edge_color='red', width=2,
                arrows=True,
                arrowstyle='-|>',
                arrowsize=20,
                connectionstyle="arc3,rad=0.1",
                min_source_margin=15,
                min_target_margin=15
            )

        # 3. Draw nodes
        nx.draw_networkx_nodes(
            G, pos, ax=ax, node_color=estimates,
            cmap=plt.cm.YlGnBu, node_size=1200,
            vmin=min(initial_values), vmax=max(initial_values)
        )

        labels = {i: f"ID:{i}\n{agents[i].get_estimate():.4f}" for i in range(num_agents)}
        nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=8, font_weight='bold')

        ax.set_title(f"Push-Sum Protocol Animation\nRound: {frame} | Global Avg: {true_avg:.2f}")
        ax.axis('off')

    ani = FuncAnimation(fig, update, frames=max_rounds, repeat=False, interval=100)
    plt.show()


if __name__ == "__main__":
    run_animated_push_sum(NUMBER_OF_AGENTS)