from random import random

 # Generates random transactions for Lightning Network simulation.
class TransactionGenerator:
    """
    Generates random transactions for Lightning Network simulation.

    Args:
        max_balance (int): Maximum transaction amount.
        num_transactions (int): Number of transactions to generate.
    """
    def __init__(self, max_balance: int, num_transactions: int):
        """
        Initialize the transaction generator.

        Args:
            max_balance (int): Maximum transaction amount.
            num_transactions (int): Number of transactions to generate.
        """
        self.max_balance = max_balance
        self.num_transactions = num_transactions

    def generate_transactions(self, node_ids: list) -> list:
        """
        Generate a list of random transactions between nodes.

        Args:
            node_ids (list): List of node IDs to use as senders and receivers.

        Returns:
            list: List of (from_id, to_id, amount) tuples.
        """
        transactions = []
        for _ in range(self.num_transactions):
            from_id = self.random_choice(node_ids)
            to_id = self.random_choice(node_ids)
            while to_id == from_id:  # Avoid self-payments
                to_id = self.random_choice(node_ids)
            amount = self.randint(1000, self.max_balance)
            transactions.append((from_id, to_id, amount))
        return transactions

    def random_choice(self, lst):
        """
        Select a random element from a list.

        Args:
            lst (list): List to select from.

        Returns:
            Any: Randomly selected element.
        """
        return lst[int(random() * len(lst))]

    def randint(self, a, b):
        """
        Return a random integer between a and b (inclusive).

        Args:
            a (int): Lower bound.
            b (int): Upper bound.

        Returns:
            int: Random integer in [a, b].
        """
        return int(random() * (b - a + 1)) + a
    