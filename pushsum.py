import random
from utils import generate_random_connected_graph, cost_dictionary

NUMBER_OF_AGENTS = 10
# node id, s and w
AGENT_MEMORY_COST = NUMBER_OF_AGENTS * cost_dictionary["mem"] * 3
# Number of assignment, taking absolute value, comparison and arithmetic operations
AGENT_OPERATIONS_COST = 0
# Number of messages sent between agents
AGENT_COMMUNICATIONS_COST = 0


class Node:
    def __init__(self, node_id, initial_value):
        self.id = node_id
        # s = sum estimate, w = weight
        self.s = float(initial_value)
        self.w = 1.0

        self.neighbors = []

        # Buffer for synchronous communication
        self.inbox_s = 0.0
        self.inbox_w = 0.0

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def send_message(self):
        """Standard Push-Sum Protocol: Send half to neighbor, keep half."""
        if not self.neighbors:
            return

        self.s /= 2.0
        self.w /= 2.0

        # Pick random neighbor
        target = random.choice(self.neighbors)
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

        if self.w == 0: return 0
        return self.s / self.w


def run_push_sum(num_agents, max_rounds):
    global AGENT_OPERATIONS_COST, AGENT_COMMUNICATIONS_COST, AGENT_MEMORY_COST
    # 1. Setup Graph
    print(f"Generating graph for {num_agents} agents...")
    graph_nx = generate_random_connected_graph(num_agents, p=0.25)

    # 2. Initialize Nodes with Random Integers
    nodes = []
    initial_values = [random.randint(1, 100) for _ in range(num_agents)]
    print("Agent initial values: ", initial_values)

    for i in range(num_agents):
        nodes.append(Node(i, initial_value=initial_values[i]))

    # Connect nodes based on graph topology
    for u, v in graph_nx.edges():
        nodes[u].add_neighbor(nodes[v])
        nodes[v].add_neighbor(nodes[u])

    # Show True Average (For User Verification Only)
    true_avg = sum(initial_values) / num_agents
    print(f"Global True Average: {true_avg:.4f} (Hidden from agents)")
    print("-" * 50)

    # 3. Simulation Loop
    for r in range(1, max_rounds + 1):
        # -- Phase A: Push (Send) --
        for node in nodes:
            node.send_message()
            AGENT_OPERATIONS_COST += cost_dictionary["op"] * 8
            AGENT_COMMUNICATIONS_COST += cost_dictionary["msg"]

        # -- Phase B: Sum (Receive & Update) --
        for node in nodes:
            node.update_state()

        # Log progress
        if r % 10 == 0 or r == 1:
            print(f"Round {r:03d}: Agents values: {", ".join(f"{n.get_estimate():.4f}" for n in nodes)}")


    print("-" * 50)
    print("Verification:")
    print(f"True Average: {true_avg:.4f}")

    # Print a sample of agents
    print("Agent Estimates:")
    for i in range(num_agents):
        est = nodes[i].get_estimate()
        diff = abs(est - true_avg)
        print(f"Agent {i}: {est:.4f} (Diff from true avg: {diff:.6f})")
    algorithm_cost = AGENT_MEMORY_COST + AGENT_OPERATIONS_COST + AGENT_COMMUNICATIONS_COST
    print(f"Overall cost: {algorithm_cost:.4f}")


if __name__ == "__main__":
    run_push_sum(num_agents=NUMBER_OF_AGENTS, max_rounds=100)