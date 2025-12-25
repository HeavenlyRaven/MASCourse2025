import random
import numpy as np
from collections import defaultdict
from utils import generate_random_connected_graph, cost_dictionary

NUMBER_OF_AGENTS = 10
# Memory cost: node_id and value
AGENT_MEMORY_COST = NUMBER_OF_AGENTS * cost_dictionary["mem"] * 2
AGENT_OPERATIONS_COST = 0
AGENT_COMMUNICATIONS_COST = 0


class LocalVotingNode:
    def __init__(self, node_id, initial_value, step_size=0.05):
        self.id = node_id
        self.val = float(initial_value)
        self.step_size = step_size
        self.neighbors = []

        # Obstacle: Message Delay Buffer (Arrival Round -> List of Values)
        self.mailbox = defaultdict(list)
        # Obstacle: Disconnection counter
        self.disconnected_rounds = 0

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def send_messages(self, current_round):
        """Sends current value to neighbors with random delays."""

        if self.disconnected_rounds > 0:
            return

        for neighbor in self.neighbors:
            # Obstacle 3: Message Delay (1 to 2 iterations)
            delay = random.randint(1, 2)
            arrival_time = current_round + delay
            neighbor.mailbox[arrival_time].append(self.val)


    def update_state(self, current_round):
        """Local Voting Rule: x_i = x_i + alpha * sum(x_j - x_i) + noise."""
        global AGENT_OPERATIONS_COST

        if self.disconnected_rounds > 0:
            self.disconnected_rounds -= 1
            return

        incoming = self.mailbox.get(current_round, [])
        if not incoming:
            return

        # 1. Consensus Calculation
        # x_i = x_i + alpha * (sum(x_j) - count * x_i)
        diff_sum = sum(v - self.val for v in incoming)

        # 2. Obstacle 1: Noise (Zero-mean Gaussian, ~10% variability)
        noise = np.random.normal(0, 0.1)

        # 3. Apply Update
        self.val += (self.step_size * diff_sum) + noise

        AGENT_OPERATIONS_COST += cost_dictionary["op"] * (len(incoming) * 2 + 2)

        # Memory Cleanup
        if current_round in self.mailbox:
            del self.mailbox[current_round]

    def check_failure(self):
        """Obstacle 2: Random Agent Disconnections."""
        if self.disconnected_rounds == 0 and random.random() < 0.1:
            self.disconnected_rounds = random.randint(1, 2)


def run_local_voting(num_agents, max_rounds):
    global AGENT_OPERATIONS_COST, AGENT_COMMUNICATIONS_COST, AGENT_MEMORY_COST

    # 1. Setup Graph
    print(f"Generating connected graph for {num_agents} agents...")
    graph_nx = generate_random_connected_graph(num_agents, p=0.25)

    # 2. Initialize Nodes
    nodes = []
    initial_values = [random.randint(1, 100) for _ in range(num_agents)]
    print(f"Agent initial values: {initial_values}")

    for i in range(num_agents):
        nodes.append(LocalVotingNode(i, initial_value=initial_values[i]))

    for u, v in graph_nx.edges():
        nodes[u].add_neighbor(nodes[v])
        nodes[v].add_neighbor(nodes[u])

    true_avg = sum(initial_values) / num_agents
    print(f"Global True Average: {true_avg:.4f}")
    print(f"Obstacles: 10% Noise, 1-2 Round Delays, Random Disconnects")
    print("-" * 80)

    # 3. Simulation Loop
    for r in range(1, max_rounds + 1):
        # A. Failure Logic
        for node in nodes:
            node.check_failure()

        # B. Send Phase
        for node in nodes:
            node.send_messages(r)
            AGENT_COMMUNICATIONS_COST += cost_dictionary["msg"]

        # C. Update Phase
        for node in nodes:
            node.update_state(r)

        # Log progress every 10 rounds
        if r % 10 == 0 or r == 1:
            vals_str = ", ".join(f"{n.val:7.4f}" for n in nodes)
            active_count = sum(1 for n in nodes if n.disconnected_rounds == 0)
            print(f"Round {r:03d} | Active: {active_count:2d}/{num_agents} | Values: {vals_str}")

    print("-" * 80)
    print("Verification:")
    print(f"Target Average: {true_avg:.4f}")

    final_vals = [n.val for n in nodes]
    final_net_avg = sum(final_vals) / num_agents
    print(f"Final Network Average: {final_net_avg:.4f} (Error: {abs(final_net_avg - true_avg):.4f})")

    print("\nAgent Estimates:")
    for i in range(num_agents):
        est = nodes[i].val
        diff = abs(est - true_avg)
        print(f"Agent {i:02d}: {est:8.4f} (Diff: {diff:8.6f})")

    algorithm_cost = AGENT_MEMORY_COST + AGENT_OPERATIONS_COST + AGENT_COMMUNICATIONS_COST
    print(f"\nTotal Algorithm Cost: {algorithm_cost:.4f}")


if __name__ == "__main__":
    run_local_voting(num_agents=NUMBER_OF_AGENTS, max_rounds=100)