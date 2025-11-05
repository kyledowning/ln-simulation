import random
import transaction_gen


class Node:
    """
    Represents a node in the Lightning Network simulation.
    """
    def __init__(self, node_id: str):
        """
        Initialize a Node with a unique identifier.

        Args:
            node_id (str): Unique node identifier.
        """
        self.node_id = node_id
        self.channels = {}  # Key: other_node_id, Value: Channel object

    def add_channel(self, channel_id: str, channel):
        """
        Add a channel to this node.

        Args:
            channel_id (str): Channel identifier.
            channel (Channel): Channel object to add.
        """
        if channel.node_a.node_id != self.node_id and channel.node_b.node_id != self.node_id:
            raise ValueError("Channel does not connect to this node")
        other_node = channel.get_other_node(self)
        other_id = other_node.node_id
        if other_id in self.channels:
            raise ValueError("Channel to this node already exists.")
        self.channels[other_id] = channel

    def get_neighbors(self):
        """
        Get a list of neighboring node IDs connected by channels.

        Returns:
            list: Neighbor node IDs.
        """
        return list(self.channels.keys())

    def change_fee(self, other_node_id: str, new_base_fee: int, new_fee_rate: float):
        """
        Change the fee parameters for a channel to another node.

        Args:
            other_node_id (str): Neighbor node ID.
            new_base_fee (int): New base fee.
            new_fee_rate (float): New fee rate.
        """
        if other_node_id not in self.channels:
            raise ValueError("Channel not found")
        channel = self.channels[other_node_id]
        channel.base_fee = new_base_fee
        channel.fee_rate = new_fee_rate


class Channel:
    """
    Represents a payment channel between two nodes.
    """
    def __init__(self, node_a: Node, node_b: Node, capacity: int, balance_a: int, balance_b: int,
                 base_fee: int, fee_rate: float, channel_id: str):
        """
        Initialize a Channel between two nodes.

        Args:
            node_a (Node): First node.
            node_b (Node): Second node.
            capacity (int): Total channel capacity.
            balance_a (int): Balance for node_a.
            balance_b (int): Balance for node_b.
            base_fee (int): Base fee for forwarding.
            fee_rate (float): Fee rate for forwarding.
            channel_id (str): Unique channel identifier.
        """
        if balance_a + balance_b != capacity:
            raise ValueError("Sum of balances must equal capacity")

        self.node_a = node_a
        self.node_b = node_b
        self.capacity = capacity
        self.balance_a = balance_a
        self.balance_b = balance_b
        self.base_fee = base_fee
        self.fee_rate = fee_rate
        self.channel_id = channel_id
        self.fee_earned = 0  # Track total fees earned on this channel

    def get_other_node(self, node: Node) -> Node:
        """
        Get the other node in the channel.

        Args:
            node (Node): One end of the channel.

        Returns:
            Node: The other node.
        """
        if node == self.node_a:
            return self.node_b
        elif node == self.node_b:
            return self.node_a
        else:
            raise ValueError("Node not part of this channel")

    def calculate_fee(self, amount: int) -> int:
        """
        Calculate the fee for forwarding a payment of a given amount.

        Args:
            amount (int): Payment amount.

        Returns:
            int: Total fee for forwarding.
        """
        return self.base_fee + int(amount * self.fee_rate)

    def can_forward(self, from_node: Node, amount: int) -> bool:
        """
        Check if the channel can forward a payment from a node with sufficient balance.

        Args:
            from_node (Node): Node sending the payment.
            amount (int): Payment amount.

        Returns:
            bool: True if payment can be forwarded, False otherwise.
        """
        if from_node == self.node_a:
            return self.balance_a >= amount
        elif from_node == self.node_b:
            return self.balance_b >= amount
        else:
            raise ValueError("Node not part of this channel")

    def update_balances(self, from_node: Node, amount: int):
        """
        Update channel balances after a payment is forwarded.

        Args:
            from_node (Node): Node sending the payment.
            amount (int): Payment amount.
        """
        if from_node == self.node_a:
            if self.balance_a < amount:
                return  # insufficient balance
            self.balance_a -= amount
            self.balance_b += amount
        elif from_node == self.node_b:
            if self.balance_b < amount:
                return
            self.balance_b -= amount
            self.balance_a += amount
        else:
            raise ValueError("Node not part of this channel")

    def __repr__(self):
        """
        String representation of the Channel.
        """
        return (f"Channel({self.node_a.node_id} <-> {self.node_b.node_id}, "
                f"capacity={self.capacity}, balance_a={self.balance_a}, balance_b={self.balance_b}, "
                f"base_fee={self.base_fee}, fee_rate={self.fee_rate}, fee_earned={self.fee_earned})")


class Network:
    """
    Represents the Lightning Network graph of nodes and channels.
    """
    def __init__(self):
        """
        Initialize an empty Network.
        """
        self.nodes = {}
        self.channels = {}

    def add_node(self, node_id: str) -> Node:
        """
        Add a node to the network.

        Args:
            node_id (str): Unique node identifier.

        Returns:
            Node: The created Node object.
        """
        if node_id in self.nodes:
            raise ValueError("Node already exists")
        node = Node(node_id)
        self.nodes[node_id] = node
        return node

    def add_channel(self, node_a_id: str, node_b_id: str, capacity: int, balance_a: int,
                    balance_b: int, base_fee: int, fee_rate: float) -> Channel:
        """
        Add a channel between two nodes in the network.

        Args:
            node_a_id (str): First node ID.
            node_b_id (str): Second node ID.
            capacity (int): Channel capacity.
            balance_a (int): Balance for node_a.
            balance_b (int): Balance for node_b.
            base_fee (int): Base fee for forwarding.
            fee_rate (float): Fee rate for forwarding.

        Returns:
            Channel: The created Channel object.
        """
        if node_a_id not in self.nodes or node_b_id not in self.nodes:
            raise ValueError("Both nodes must exist in the network")

        node_a = self.nodes[node_a_id]
        node_b = self.nodes[node_b_id]
        sorted_ids = sorted([node_a_id, node_b_id])
        channel_id = f"{sorted_ids[0]}-{sorted_ids[1]}"

        if channel_id in self.channels:
            raise ValueError("Channel already exists between these nodes")

        channel = Channel(node_a, node_b, capacity, balance_a, balance_b, base_fee, fee_rate, channel_id)
        self.channels[channel_id] = channel
        node_a.add_channel(channel_id, channel)
        node_b.add_channel(channel_id, channel)
        return channel

    def find_path(self, from_node_id: str, to_node_id: str, amount: int) -> dict:
        """
        Find a payment path from one node to another for a given amount using a shortest-path algorithm.

        Args:
            from_node_id (str): Sender node ID.
            to_node_id (str): Receiver node ID.
            amount (int): Payment amount.

        Returns:
            dict: {'path': list of node IDs, 'total_cost': int} or empty dict if no path found.
        """
        import heapq
        if from_node_id not in self.nodes or to_node_id not in self.nodes:
            return {}

        INF = float('inf')
        dist = {node_id: INF for node_id in self.nodes}
        dist[to_node_id] = amount
        pred = {node_id: None for node_id in self.nodes}
        pq = [(amount, to_node_id)]

        while pq:
            cur_dist, u = heapq.heappop(pq)
            if cur_dist > dist[u]:
                continue
            for v in self.nodes[u].get_neighbors():
                channel = self.nodes[u].channels[v]
                forward_amount = dist[u]
                if forward_amount == INF:
                    continue
                if channel.can_forward(self.nodes[v], forward_amount):
                    fee = channel.calculate_fee(forward_amount)
                    new_dist = dist[u] + fee
                    if new_dist < dist[v]:
                        dist[v] = new_dist
                        pred[v] = u
                        heapq.heappush(pq, (new_dist, v))

        if dist[from_node_id] == INF:
            return {}

        # Reconstruct forward path
        path = []
        current = from_node_id
        while current is not None:
            path.append(current)
            current = pred[current]
        if path[-1] != to_node_id:
            return {}

        return {'path': path, 'total_cost': dist[from_node_id]}

    def execute_payment(self, from_node_id: str, to_node_id: str, amount: int) -> tuple[bool, int]:
        """
        Execute a payment from one node to another, updating balances and fees.

        Args:
            from_node_id (str): Sender node ID.
            to_node_id (str): Receiver node ID.
            amount (int): Payment amount.

        Returns:
            tuple: (success (bool), total_fees (int)).
        """
        path_info = self.find_path(from_node_id, to_node_id, amount)
        if not path_info:
            return False, 0

        path = path_info['path']
        total_cost = path_info['total_cost']
        total_fees = total_cost - amount
        current_amount = amount

        for i in range(len(path) - 1, 0, -1):
            receiver_id = path[i]
            sender_id = path[i - 1]
            channel_id = f"{min(sender_id, receiver_id)}-{max(sender_id, receiver_id)}"
            channel = self.channels.get(channel_id)
            if not channel:
                return False, 0

            fee = channel.calculate_fee(current_amount)
            forward_amount = current_amount + fee
            sender_node = self.nodes[sender_id]
            channel.update_balances(sender_node, forward_amount)

            # Add fee to channel earnings (not node)
            channel.fee_earned += fee

            current_amount = forward_amount

        return True, total_fees

    def print_network(self):
        """
        Print a summary of all channels in the network.
        """
        print("Channels:")
        for channel_id, channel in self.channels.items():
            print(f" {channel}")


class TransactionManager:
    """
    Manages transactions and simulation for the Lightning Network.
    """
    def __init__(self, network: Network):
        """
        Initialize the TransactionManager.

        Args:
            network (Network): The network to manage transactions for.
        """
        self.network = network
        self.transaction_queue = []  # List of (from_id, to_id, amount)
        self.log = []  # List of simulation results

    def add_transaction(self, from_id: str, to_id: str, amount: int):
        """
        Add a transaction to the queue.

        Args:
            from_id (str): Sender node ID.
            to_id (str): Receiver node ID.
            amount (int): Payment amount.
        """
        self.transaction_queue.append((from_id, to_id, amount))

    def simulate(self, concurrent: bool = False):
        """
        Simulate all queued transactions, optionally using concurrency.

        Args:
            concurrent (bool): If True, process transactions concurrently.

        Returns:
            list: Log of transaction results.
        """
        self.log.clear()
        if concurrent:
            import threading
            threads = []
            for tx in self.transaction_queue:
                t = threading.Thread(target=self.process_tx, args=tx)
                threads.append(t)
                t.start()
            for t in threads:
                t.join()
        else:
            for tx in self.transaction_queue:
                self.process_tx(*tx)
        self.transaction_queue.clear()
        return self.log

    def process_tx(self, from_id: str, to_id: str, amount: int):
        """
        Process a single transaction and log the result.

        Args:
            from_id (str): Sender node ID.
            to_id (str): Receiver node ID.
            amount (int): Payment amount.
        """
        success, total_fees = self.network.execute_payment(from_id, to_id, amount)
        if success:
            result = f"Transaction {from_id} -> {to_id} ({amount} sat, total fees: {total_fees} sat): Success"
        else:
            result = f"Transaction {from_id} -> {to_id} ({amount} sat): Failed"
        self.log.append(result)

