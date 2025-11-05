from network import Network, TransactionManager
import random
import transaction_gen
import copy
import csv

MAX_CAPACITY = 1_000_000_000
MAX_FEE_RATE = 0.5
MAX_BASE_FEE = 2000


def createLNetwork(num_nodes: int, edge_prob: float) -> Network:
    """
    Create a random Lightning Network topology with specified number of nodes and edge probability.

    Args:
        num_nodes (int): Number of nodes in the network.
        edge_prob (float): Probability of creating an edge between any two nodes (0 < edge_prob <= 1).

    Returns:
        Network: A Network object populated with nodes and randomly generated channels.
    """
    network = Network()

    for i in range(num_nodes):
        network.add_node(str(i))

    if edge_prob <= 0 or edge_prob > 1:
        raise ValueError("edge_prob must be in the range (0, 1]")

    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if random.random() < edge_prob:
                capacity = random.randint(1_000_000, MAX_CAPACITY)
                balance_a = random.randint(0, capacity)
                balance_b = capacity - balance_a
                base_fee = random.randint(0, MAX_BASE_FEE)

                fee_rate = round(random.betavariate(3.0, 3.0) * MAX_FEE_RATE, 6)
                network.add_channel(str(i), str(j), capacity, balance_a, balance_b, base_fee, fee_rate)

    return network


if __name__ == "__main__":
    num_nodes = 150
    iterations = 1000

    # Create network once
    network = createLNetwork(num_nodes=num_nodes, edge_prob=0.1)
    print(f"Created network: {len(network.nodes)} nodes, {len(network.channels)} channels")

    # Choose one specific channel to vary
    target_channel_id = next(iter(network.channels.keys()))  # pick the first one
    print(f"Target channel for fee modification: {target_channel_id}")

    transactions = transaction_gen.TransactionGenerator(
        max_balance=100_000, num_transactions=2000
    ).generate_transactions(list(network.nodes.keys()))

    with open('channel_fee_variation.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Iteration", "Fee Rate", "Channel Fee Earned"])

        for i in range(iterations):
            new_fee_rate = round((i / (iterations - 1)) * MAX_FEE_RATE, 6)

            # Clone the network so balances reset each iteration
            sim_network = copy.deepcopy(network)

            # Get the target channel and update its fee rate
            target_channel = sim_network.channels[target_channel_id]
            target_channel.fee_rate = new_fee_rate

            # Simulate transactions
            manager = TransactionManager(sim_network)
            for from_id, to_id, amount in transactions:
                manager.add_transaction(from_id, to_id, amount)
            manager.simulate(concurrent=False)

            # Get the total fees earned on that specific channel
            channel_fees = sim_network.channels[target_channel_id].fee_earned

            print(f"Iteration {i+1}/{iterations} | fee_rate={new_fee_rate} | fee_earned={channel_fees}")

            writer.writerow([i + 1, new_fee_rate, channel_fees])

    print("\nDone. Results saved to 'channel_fee_variation.csv'")
