import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
import numpy as np

# ========================================================================== #
# ================================== INFO ================================== #
# ========================================================================== #
# This program calculates the difference between one landfill and another
# for Tons <= 5.
# - Filter Invoicing Board:
#   - Tons <= 5
#   - Tons is not Blank
#   - Filter by disposal locations.
# ========================================================================== #
# ================================== TODO ================================== #
# ========================================================================== #
# TODO: Update data file path.
# ========================================================================== #


# Pricing Difference Data
data = pd.read_excel('path_to_your_file')

# print(data.head())
# print(data.tail())
# print(data.info())
# print(data.describe())
# print(data.columns)
# print(data.shape) 

# Adjust these column names if needed
disposal_cost_col = 'Disposal Cost'
tons_col = 'Tons'
gross_profit_col = 'Gross Profit'
driver_col = 'Driver'
new_rate = 86  # $86/ton

data['Gross Profit'] = data['Gross Profit'].fillna(0)

# Calculate the current total disposal cost
current_total_disposal_cost = data[disposal_cost_col].sum()
print(f"Current total disposal cost: ${current_total_disposal_cost:,.2f}")

current_total_gross_profit = data[gross_profit_col].sum()
print(f"Current total gross profit: ${current_total_gross_profit:,.2f}")

# Calculate the total tons
total_tons = data[tons_col].sum()

# Calculate the hypothetical cost at landfill rate
wm_total_cost = total_tons * new_rate
print(f"Total tons: {total_tons:,.2f}")
print(f"Total cost at New Disposal rate: ${wm_total_cost:,.2f}")

# Calculate the difference
pricing_difference = wm_total_cost - current_total_disposal_cost
print(f"Pricing difference (New rate - current): ${pricing_difference:,.2f}")

gross_profit_difference = current_total_gross_profit - pricing_difference
print(f"Gross Profit difference (New disposal rate): {gross_profit_difference:,.2f}")

# --- Group by driver and calculate sums --- #
driver_group = data.groupby(driver_col).agg({
    disposal_cost_col: 'sum',
    tons_col: 'sum'
}).reset_index()

# Calculate cost and pricing difference by driver
driver_group['WM Disposal Cost'] = driver_group[tons_col] * new_rate
driver_group['Pricing Difference'] = driver_group['WM Disposal Cost'] - driver_group[disposal_cost_col]

print("\nDisposal Cost and Pricing Difference by Driver (New Rate):")
for idx, row in driver_group.iterrows():
    print(f"Driver: {row[driver_col]}")
    print(f"  Current Total Disposal Cost: ${row[disposal_cost_col]:,.2f}")
    print(f"  New Rate Disposal Cost: ${row['WM Disposal Cost']:,.2f}")
    print(f"  Pricing Difference (New Rate - Current): ${row['Pricing Difference']:,.2f}\n")

# ========================================================================== #
# ========================= Current Disposal vs New Rate =================== #
# ========================================================================== #
# Ensure 'Date' is datetime
data['Date'] = pd.to_datetime(data['Date'])

# Group by month
data['Month'] = data['Date'].dt.to_period('M')
monthly = data.groupby('Month').agg({
    'Disposal Cost': 'sum',
    'Tons': 'sum'
}).reset_index()

monthly['WM Disposal Cost'] = monthly['Tons'] * new_rate

# Plot
x = range(len(monthly))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))
bars1 = ax.bar([i - width/2 for i in x], monthly['Disposal Cost'], 
               width, label='Current Disposal Cost')
bars2 = ax.bar([i + width/2 for i in x], monthly['WM Disposal Cost'], 
               width, label=f'New Disposal Cost (${new_rate}/ton)')

ax.set_xlabel('Month')
ax.set_ylabel('Total Disposal Cost')
ax.set_title(f'Monthly Disposal Cost: Actual vs. New Rate (${new_rate}/ton)')
ax.set_xticks(x)
ax.set_xticklabels([str(m) for m in monthly['Month']])
ax.legend()
plt.tight_layout()
plt.grid(axis='y', linestyle='-', alpha=0.5)

# Add mplcursors hovertips
cursor1 = mplcursors.cursor(bars1, hover=True)
cursor2 = mplcursors.cursor(bars2, hover=True)

@cursor1.connect("add")
def on_add_current(sel):
    idx = sel.index
    month = monthly['Month'].iloc[idx]
    value = monthly['Disposal Cost'].iloc[idx]
    sel.annotation.set_text(f"Month: {month}\nCurrent Disposal Cost: ${value:,.2f}")

@cursor2.connect("add")
def on_add_wm(sel):
    idx = sel.index
    month = monthly['Month'].iloc[idx]
    value = monthly['WM Disposal Cost'].iloc[idx]
    sel.annotation.set_text(f"Month: {month}\nNew Disposal Cost: ${value:,.2f}")

plt.show()

# ========================================================================== #
# =========================== Bar Chart by Driver ========================== #
# ========================================================================== #
drivers = driver_group[driver_col]
current_costs = driver_group[disposal_cost_col]
wm_costs = driver_group['WM Disposal Cost']

y = np.arange(len(drivers))
height = 0.35

fig, ax = plt.subplots(figsize=(12, 8))
bars1 = ax.barh(y - height/2, current_costs, height, 
                label='Current Disposal Cost', color='royalblue')
bars2 = ax.barh(y + height/2, wm_costs, height, 
                label=f'New Disposal Cost (${new_rate}/ton)', color='darkorange')

ax.set_yticks(y)
ax.set_yticklabels(drivers)
ax.set_xlabel('Total Disposal Cost')
ax.set_title(f'Disposal Cost by Driver: Actual vs. New Rate (${new_rate}/ton)')
ax.legend()
plt.tight_layout()
plt.grid(axis='x', linestyle='-', alpha=0.5)

# Add mplcursors hovertips
cursor1 = mplcursors.cursor(bars1, hover=True)
cursor2 = mplcursors.cursor(bars2, hover=True)

@cursor1.connect("add")
def on_add_current(sel):
    idx = sel.index
    driver = drivers.iloc[idx]
    value = current_costs.iloc[idx]
    sel.annotation.set_text(f"Driver: {driver}\nCurrent Disposal Cost: ${value:,.2f}")

@cursor2.connect("add")
def on_add_wm(sel):
    idx = sel.index
    driver = drivers.iloc[idx]
    value = wm_costs.iloc[idx]
    sel.annotation.set_text(f"Driver: {driver}\nNew Disposal Cost: ${value:,.2f}")

plt.show()

# ========================================================================== #
# =================== Top 10 Largest Projects by Location ================== #
# ========================================================================== #
# Group by 'Location'
location_group = data.groupby('Location').agg({
    disposal_cost_col: 'sum',
    tons_col: 'sum'
}).reset_index()

# Calculate WM cost by location
location_group['WM Disposal Cost'] = location_group[tons_col] * new_rate

# Get top 10 locations by actual disposal cost
top10_locations = location_group.nlargest(10, disposal_cost_col)

locations = top10_locations['Location']
actual_costs = top10_locations[disposal_cost_col]
wm_costs = top10_locations['WM Disposal Cost']

x = np.arange(len(locations))
width = 0.35

fig, ax = plt.subplots(figsize=(14, 8))
bars1 = ax.bar(x - width/2, actual_costs, width, 
               label='Actual Disposal Cost', color='royalblue')
bars2 = ax.bar(x + width/2, wm_costs, width, 
               label=f'New Disposal Cost (${new_rate}/ton)', color='darkorange')

ax.set_xticks(x)
short_labels = locations.str.split(',', n=1).str[0]
ax.set_xticklabels(short_labels, rotation=45, ha='right')
ax.set_ylabel('Total Disposal Cost')
ax.set_title('Top 10 Largest Projects by Location: Actual vs. New Disposal Cost')
ax.legend()
plt.tight_layout()
plt.grid(axis='y', linestyle='-', alpha=0.5)

# Add mplcursors hovertips
cursor1 = mplcursors.cursor(bars1, hover=True)
cursor2 = mplcursors.cursor(bars2, hover=True)

@cursor1.connect("add")
def on_add_actual(sel):
    idx = sel.index
    location = locations.iloc[idx]
    value = actual_costs.iloc[idx]
    sel.annotation.set_text(f"Location: {location}\nActual Disposal Cost: ${value:,.2f}")

@cursor2.connect("add")
def on_add_wm(sel):
    idx = sel.index
    location = locations.iloc[idx]
    value = wm_costs.iloc[idx]
    sel.annotation.set_text(f"Location: {location}\nNew Disposal Cost: ${value:,.2f}")

plt.show()
