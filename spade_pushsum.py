import asyncio
import random
import json
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

# Assuming your local utils are available
# from utils import generate_random_connected_graph, cost_dictionary

# Dummy cost dictionary for standalone functionality
cost_dictionary = {"mem": 1, "op": 1, "msg": 1}


class PushSumAgent(Agent):
    def __init__(self, jid, password, initial_value, neighbor_jids):
        super().__init__(jid, password)
        self.s = float(initial_value)
        self.w = 1.0
        self.neighbor_jids = neighbor_jids
        self.node_id = jid.split("@")[0]

    class PushBehaviour(CyclicBehaviour):
        async def run(self):
            if self.agent.neighbor_jids:
                # Local state update (Push)
                self.agent.s /= 2.0
                self.agent.w /= 2.0

                target_jid = random.choice(self.agent.neighbor_jids)

                msg = Message(to=target_jid)
                msg.set_metadata("performative", "inform")
                msg.body = json.dumps({"s": self.agent.s, "w": self.agent.w})

                await self.send(msg)
            await asyncio.sleep(1)  # Frequency of pushes

    class SumBehaviour(CyclicBehaviour):
        async def run(self):
            # Receive with a short timeout to keep the loop responsive
            msg = await self.receive(timeout=1)
            if msg:
                data = json.loads(msg.body)
                self.agent.s += data["s"]
                self.agent.w += data["w"]

                estimate = self.agent.s / self.agent.w
                print(f"[{self.agent.node_id}] Current Estimate: {estimate:.4f}")

    async def setup(self):
        self.add_behavior(self.PushBehaviour())
        self.add_behavior(self.SumBehaviour())


async def main():
    num_agents = 3
    # Use 'localhost' if running Prosody/Openfire locally
    domain = "localhost"
    agents = []

    # Example: Simple Ring Topology for testing
    for i in range(num_agents):
        jid = f"agent{i}@{domain}"
        # Connect 0->1, 1->2, 2->0
        neighbors = [f"agent{(i + 1) % num_agents}@{domain}"]

        a = PushSumAgent(jid, "password", random.randint(1, 100), neighbors)
        agents.append(a)

    print("Starting agents...")
    for a in agents:
        # The 'address' error usually comes from start() or connect()
        # Use hostname instead of address if you need to specify IP
        await a.start(auto_register=True)

    print("Agents are running. Observing estimates for 10 seconds...")
    await asyncio.sleep(10)

    for a in agents:
        await a.stop()
    print("Simulation finished.")


if __name__ == "__main__":
    asyncio.run(main())