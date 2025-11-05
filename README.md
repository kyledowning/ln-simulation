# LN Simulation

This directory contains Python modules for simulating a Lightning Network (LN) and generating transactions. Below you'll find instructions for usage, descriptions of each file, and example workflows.

## Directory Contents
- `network.py`: Core classes for nodes, channels, and the network graph. Handles payment routing and fee calculations.
- `transaction_gen.py`: Utility for generating random transactions between nodes.
- `simulation_single.py`: Script for running a single simulation, varying channel fees and recording results.

## Getting Started
1. **Install Dependencies**
	 - Make sure you have Python 3.7+ installed.
	 - Required packages: `numpy`, `matplotlib`, `pandas` (if plotting or data analysis is needed).
	 - Install with pip:
		 ```bash
		 pip install numpy matplotlib pandas
		 ```

2. **Run a Simulation**
	 - The main entry point is `simulation_single.py`.
	 - Example:
		 ```bash
		 python simulation_single.py
		 ```
	 - This will create a network, vary the fee rate of a target channel, simulate transactions, and save results to `channel_fee_variation.csv`.

3. **Generate Transactions**
	 - Use `transaction_gen.py` to create random transactions for your network:
		 ```python
		 from transaction_gen import TransactionGenerator
		 generator = TransactionGenerator(max_balance=100_000, num_transactions=2000)
		 transactions = generator.generate_transactions(list_of_node_ids)
		 ```

4. **Network Operations**
	 - Use `network.py` to create nodes, channels, and route payments:
		 ```python
		 from network import Network, TransactionManager
		 net = Network()
		 net.add_node('A')
		 net.add_node('B')
		 net.add_channel('A', 'B', capacity=1000000, balance_a=500000, balance_b=500000, base_fee=10, fee_rate=0.001)
		 manager = TransactionManager(net)
		 manager.add_transaction('A', 'B', 10000)
		 manager.simulate()
		 ```

## File Descriptions
### network.py
- **Node**: Represents a network participant.
- **Channel**: Represents a payment channel between two nodes.
- **Network**: Manages nodes and channels, finds payment paths, executes payments.
- **TransactionManager**: Queues and simulates transactions.

### transaction_gen.py
- **TransactionGenerator**: Generates random transactions for simulation.

### simulation_single.py
- Creates a network, varies a channel's fee rate, simulates transactions, and records results.

## Output Files
- `channel_fee_variation.csv`: Contains results of fee variation experiments.

## Tips
- All classes and methods are documented with Python docstrings. Hover over function names in VS Code for descriptions.
- You can modify parameters in `simulation_single.py` to change the number of nodes, transactions, or fee ranges.

## License
This project is for research and educational purposes.
