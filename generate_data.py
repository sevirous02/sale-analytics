import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import os

np.random.seed(42)
n_rows = 1_000_000

print("Generating 1,000,000 simulated orders...")

# 1. Order IDs with 1% duplicates
base_ids = np.arange(1000000, 1000000 + n_rows)
duplicate_indices = np.random.choice(n_rows, size=int(n_rows * 0.01), replace=False)
order_ids = base_ids.astype(str)
order_ids[duplicate_indices] = order_ids[np.random.choice(n_rows, size=len(duplicate_indices), replace=True)]
order_ids = "ORD-" + order_ids

# 2. Timestamps with traffic spikes (normalized probabilities)
raw_p = np.array([0.08, 0.03, 0.01, 0.01, 0.01, 0.01, 0.02, 0.03, 0.04, 0.05, 
                  0.06, 0.07, 0.08, 0.06, 0.05, 0.05, 0.05, 0.06, 0.07, 0.08, 
                  0.07, 0.06, 0.04, 0.02])
hour_probs = raw_p / raw_p.sum()

hours = np.random.choice(24, size=n_rows, p=hour_probs)
timestamps = pd.to_datetime('2026-11-11') + pd.to_timedelta(hours, unit='h') + pd.to_timedelta(np.random.randint(0, 60, size=n_rows), unit='m')

# 3. Regions
regions = np.random.choice(
    ['NCR', 'CALABARZON', 'Central Luzon', 'Central Visayas', 'Davao Region', 'Others'],
    size=n_rows, p=[0.45, 0.20, 0.15, 0.10, 0.05, 0.05]
)

# 4. Categories & Prices (explicitly converted to string/object to avoid PyArrow type mismatch)
categories = np.random.choice(['Electronics', 'Apparel', 'Beauty', 'Home & Living', 'Groceries', 'Sports', 'Toys', 'Books'], size=n_rows)
raw_prices = np.random.uniform(100, 15000, size=n_rows)
unit_prices = [f"₱{p:,.2f}" if np.random.rand() < 0.15 else f"{p:.2f}" for p in raw_prices]

# 5. Quantities (with negative quantities)
quantities = np.random.choice([1, 2, 3, 4, 5], size=n_rows, p=[0.6, 0.2, 0.1, 0.05, 0.05])
quantities[np.random.choice(n_rows, size=int(n_rows * 0.005), replace=False)] = -1

# 6. Payment Methods & Status
payment_methods = np.random.choice(['COD', 'GCash', 'Maya', 'Card'], size=n_rows, p=[0.5, 0.3, 0.1, 0.1])
statuses = ['Cancelled' if pm == 'COD' and np.random.rand() < 0.25 else 'Delivered' for pm in payment_methods]

df = pd.DataFrame({
    'order_id': order_ids, 
    'timestamp': timestamps.astype(str), 
    'region': regions,
    'category': categories, 
    'unit_price': unit_prices, 
    'quantity': quantities,
    'payment_method': payment_methods, 
    'status': statuses
})

# Inject dirty data: missing regions & mixed case
df.loc[np.random.choice(n_rows, size=int(n_rows * 0.02), replace=False), 'region'] = np.nan
mixed_idx = np.random.choice(n_rows, size=int(n_rows * 0.05), replace=False)
df.loc[mixed_idx, 'region'] = df.loc[mixed_idx, 'region'].str.lower()

# Save files
print("Saving CSV and Parquet files...")
df.to_csv('orders.csv', index=False)
df.to_parquet('orders.parquet', index=False)

csv_mb = os.path.getsize('orders.csv') / (1024 * 1024)
parquet_mb = os.path.getsize('orders.parquet') / (1024 * 1024)
print(f"Dataset generated! CSV: {csv_mb:.2f} MB | Parquet: {parquet_mb:.2f} MB")
