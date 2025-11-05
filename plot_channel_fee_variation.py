import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv('channel_fee_variation.csv')

# Plot Fee Rate vs Channel Fee Earned
plt.figure(figsize=(20, 10))
plt.plot(df['Fee Rate'], df['Channel Fee Earned'], marker='o', linestyle='-')
plt.xlabel('Fee Rate')
plt.ylabel('Channel Fee Earned')
plt.title('Channel Fee Earned vs Fee Rate')
plt.grid(True)
plt.tight_layout()
plt.savefig('channel_fee_variation_plot.png')
plt.show()
