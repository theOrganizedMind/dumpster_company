import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
import numpy as np
import logging
import tkinter as tk
from tkinter import messagebox, ttk

from postgresql import fetch_all

LOGGER = logging.getLogger(__name__)

# ========================================================================== #
# ================================== INFO ================================== #
# ========================================================================== #
# This program calculates the disposal pricing difference directly from
# PostgreSQL and uses the returned rows for all summaries and charts.
# ========================================================================== #
# ================================== TODO ================================== #
# ========================================================================== #
# TODO: 
# ========================================================================== #

def fetch_disposal_pricing_diff(start_date, 
                                end_date, 
                                pricing_mode, 
                                ton_pricing=None, 
                                yard_pricing=None):
    """Fetch disposal pricing detail rows from PostgreSQL for the provided date range."""
    pricing_mode = str(pricing_mode).lower()
    if pricing_mode == "ton" and ton_pricing is None:
        raise ValueError("ton_pricing must be set when pricing_mode is 'ton'.")
    if pricing_mode != "ton" and yard_pricing is None:
        raise ValueError("yard_pricing must be set when pricing_mode is not 'ton'.")

    query = """
        WITH filtered AS (
            SELECT
                i.*,
                date_trunc('month', i.date)::date AS month,
                CASE
                    WHEN lower(%s) = 'ton' THEN
                        COALESCE(i.tons, 0) * %s
                    ELSE
                        COALESCE(
                            NULLIF(
                                substring(COALESCE(i.size::text, '') FROM '([0-9]+(\\.[0-9]+)?)'),
                                ''
                            )::numeric,
                            0
                        ) * %s
                END AS comparison_cost
            FROM invoicing i
            WHERE i.tons <= 5
              AND i.disposal IN (
                    'Triune (Centennial)',
                    'Triune (Hermitage)',
                    'Music City Transfer'
              )
              AND i.date BETWEEN %s AND %s
        )
        SELECT *
        FROM filtered
        ORDER BY month, driver, date;
    """

    rows, columns = fetch_all(
        query,
        (
            pricing_mode,
            ton_pricing if pricing_mode == "ton" else 0,
            yard_pricing if pricing_mode != "ton" else 0,
            start_date,
            end_date,
        ),
        include_columns=True,
    )

    if not rows:
        print("No projects found for the selected date range.")
        return pd.DataFrame(columns=columns)

    data = pd.DataFrame(rows, columns=columns)
    data.columns = [str(column).lower() for column in data.columns]

    for column in ("tons", "disposalcost", "comparison_cost"):
        if column in data.columns:
            data[column] = pd.to_numeric(data[column], errors="coerce").fillna(0)

    if "date" in data.columns:
        data["date"] = pd.to_datetime(data["date"], errors="coerce")
    if "month" in data.columns:
        data["month"] = pd.to_datetime(data["month"], errors="coerce").dt.to_period("M")

    return data


def print_and_plot_disposal_pricing_diff(data, 
                                         start_date, 
                                         end_date, 
                                         pricing_mode, 
                                         ton_pricing=None, 
                                         yard_pricing=None):
    """Print disposal pricing summaries and render charts from SQL data."""
    if data.empty:
        return

    pricing_mode = str(pricing_mode).lower()
    if pricing_mode == "ton":
        comparison_label = f"New Disposal Cost (${ton_pricing}/ton)"
        comparison_title = f"New Rate (${ton_pricing}/ton)"
    else:
        comparison_label = f"Flat Rate Disposal Cost (${yard_pricing}/yard)"
        comparison_title = f"Flat Rate (${yard_pricing}/yard)"

    disposal_cost_col = "disposalcost"
    tons_col = "tons"
    driver_col = "driver"
    location_col = "street"
    comparison_col = "comparison_cost"

    print(f"\nDisposal Pricing Difference ({start_date} to {end_date})")
    print("-" * 100)

    current_total_disposal_cost = data[disposal_cost_col].sum()
    comparison_total_cost = data[comparison_col].sum()
    comparison_difference = comparison_total_cost - current_total_disposal_cost
    total_tons = data[tons_col].sum() if tons_col in data.columns else 0

    print(f"Current total disposal cost: ${current_total_disposal_cost:,.2f}")
    print(f"Total cost at {comparison_title}: ${comparison_total_cost:,.2f}")
    print(f"Pricing difference ({comparison_title} - current): ${comparison_difference:,.2f}")
    print(f"Total tons: {total_tons:,.2f}")

    if "grossprofit" in data.columns:
        current_total_gross_profit = data["grossprofit"].fillna(0).sum()
        print(f"Current total gross profit: ${current_total_gross_profit:,.2f}")
        gross_profit_difference = current_total_gross_profit - comparison_difference
        print(f"Gross Profit difference ({comparison_title}): {gross_profit_difference:,.2f}")

    driver_group = data.groupby(driver_col).agg({
        disposal_cost_col: "sum",
        comparison_col: "sum",
    }).reset_index()
    driver_group["pricing_difference"] = driver_group[comparison_col] - driver_group[disposal_cost_col]

    print(f"\nDisposal Cost and Pricing Difference by Driver ({comparison_title}):")
    for _, row in driver_group.iterrows():
        print(f"Driver: {row[driver_col]}")
        print(f"  Current Total Disposal Cost: ${row[disposal_cost_col]:,.2f}")
        print(f"  {comparison_label}: ${row[comparison_col]:,.2f}")
        print(f"  Pricing Difference ({comparison_title} - Current): ${row['pricing_difference']:,.2f}\n")

    monthly = data.groupby("month").agg({
        disposal_cost_col: "sum",
        comparison_col: "sum",
    }).reset_index()
    monthly["pricing_difference"] = monthly[comparison_col] - monthly[disposal_cost_col]

    print(f"\nMonthly Disposal Cost and Pricing Difference ({comparison_title}):")
    for _, row in monthly.iterrows():
        print(f"Month: {row['month']}")
        print(f"  Current Disposal Cost: ${row[disposal_cost_col]:,.2f}")
        print(f"  {comparison_label}: ${row[comparison_col]:,.2f}")
        print(f"  Pricing Difference ({comparison_title} - Current): ${row['pricing_difference']:,.2f}\n")

    x = range(len(monthly))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar([i - width / 2 for i in x], monthly[disposal_cost_col], width, label="Current Disposal Cost")
    bars2 = ax.bar([i + width / 2 for i in x], monthly[comparison_col], width, label=comparison_label)

    ax.set_xlabel("Month")
    ax.set_ylabel("Total Disposal Cost")
    ax.set_title(f"Monthly Disposal Cost: Actual vs. {comparison_title}")
    ax.set_xticks(list(x))
    ax.set_xticklabels([str(month) for month in monthly["month"]])
    ax.legend()
    plt.tight_layout()
    plt.grid(axis="y", linestyle="-", alpha=0.5)

    cursor1 = mplcursors.cursor(bars1, hover=True)
    cursor2 = mplcursors.cursor(bars2, hover=True)

    @cursor1.connect("add")
    def on_add_current(sel):
        idx = sel.index
        month = monthly["month"].iloc[idx]
        value = monthly[disposal_cost_col].iloc[idx]
        sel.annotation.set_text(f"Month: {month}\nCurrent Disposal Cost: ${value:,.2f}")

    @cursor2.connect("add")
    def on_add_comparison(sel):
        idx = sel.index
        month = monthly["month"].iloc[idx]
        value = monthly[comparison_col].iloc[idx]
        sel.annotation.set_text(f"Month: {month}\n{comparison_label}: ${value:,.2f}")

    plt.show()

    drivers = driver_group[driver_col]
    current_costs = driver_group[disposal_cost_col]
    comparison_costs = driver_group[comparison_col]

    y = np.arange(len(drivers))
    height = 0.35

    fig, ax = plt.subplots(figsize=(12, 8))
    bars1 = ax.barh(y - height / 2, current_costs, height, label="Current Disposal Cost", color="royalblue")
    bars2 = ax.barh(y + height / 2, comparison_costs, height, label=comparison_label, color="darkorange")

    ax.set_yticks(y)
    ax.set_yticklabels(drivers)
    ax.set_xlabel("Total Disposal Cost")
    ax.set_title(f"Disposal Cost by Driver: Actual vs. {comparison_title}")
    ax.legend()
    plt.tight_layout()
    plt.grid(axis="x", linestyle="-", alpha=0.5)

    cursor1 = mplcursors.cursor(bars1, hover=True)
    cursor2 = mplcursors.cursor(bars2, hover=True)

    @cursor1.connect("add")
    def on_add_driver_current(sel):
        idx = sel.index
        driver = drivers.iloc[idx]
        value = current_costs.iloc[idx]
        sel.annotation.set_text(f"Driver: {driver}\nCurrent Disposal Cost: ${value:,.2f}")

    @cursor2.connect("add")
    def on_add_driver_comparison(sel):
        idx = sel.index
        driver = drivers.iloc[idx]
        value = comparison_costs.iloc[idx]
        sel.annotation.set_text(f"Driver: {driver}\n{comparison_label}: ${value:,.2f}")

    plt.show()

    location_group = data.groupby(location_col).agg({
        disposal_cost_col: "sum",
        comparison_col: "sum",
    }).reset_index()
    location_group["pricing_difference"] = location_group[comparison_col] - location_group[disposal_cost_col]
    top10_locations = location_group.nlargest(10, disposal_cost_col)

    print(f"\nPricing Difference by Location ({comparison_title}, Top 10 Actual Disposal Cost Locations):")
    for _, row in top10_locations.iterrows():
        print(f"Location: {row[location_col]}")
        print(f"  Current Disposal Cost: ${row[disposal_cost_col]:,.2f}")
        print(f"  {comparison_label}: ${row[comparison_col]:,.2f}")
        print(f"  Pricing Difference ({comparison_title} - Current): ${row['pricing_difference']:,.2f}\n")

    locations = top10_locations[location_col]
    actual_costs = top10_locations[disposal_cost_col]
    comparison_costs = top10_locations[comparison_col]

    x = np.arange(len(locations))
    width = 0.35

    fig, ax = plt.subplots(figsize=(14, 8))
    bars1 = ax.bar(x - width / 2, actual_costs, width, label="Actual Disposal Cost", color="royalblue")
    bars2 = ax.bar(x + width / 2, comparison_costs, width, label=comparison_label, color="darkorange")

    ax.set_xticks(x)
    short_labels = locations.astype(str).str.split(",", n=1).str[0]
    ax.set_xticklabels(short_labels, rotation=45, ha="right")
    ax.set_ylabel("Total Disposal Cost")
    ax.set_title(f"Top 10 Largest Projects by Location: Actual vs. {comparison_title}")
    ax.legend()
    plt.tight_layout()
    plt.grid(axis="y", linestyle="-", alpha=0.5)

    cursor1 = mplcursors.cursor(bars1, hover=True)
    cursor2 = mplcursors.cursor(bars2, hover=True)

    @cursor1.connect("add")
    def on_add_location_actual(sel):
        idx = sel.index
        location = locations.iloc[idx]
        value = actual_costs.iloc[idx]
        sel.annotation.set_text(f"Location: {location}\nActual Disposal Cost: ${value:,.2f}")

    @cursor2.connect("add")
    def on_add_location_comparison(sel):
        idx = sel.index
        location = locations.iloc[idx]
        value = comparison_costs.iloc[idx]
        sel.annotation.set_text(f"Location: {location}\n{comparison_label}: ${value:,.2f}")

    plt.show()


def run_report_from_gui(start_date_entry, end_date_entry, pricing_mode_var, pricing_var):
    """Read GUI values, run the SQL query, and render the report."""
    start_date = start_date_entry.get().strip()
    end_date = end_date_entry.get().strip()
    pricing_mode = pricing_mode_var.get().strip().lower()
    pricing_value = pricing_var.get().strip()

    if not start_date or not end_date:
        messagebox.showerror("Input Error", 
                             "Please enter both start and end dates in YYYY-MM-DD format.")
        return

    if pricing_mode not in {"ton", "yard"}:
        messagebox.showerror("Input Error", 
                             "Pricing mode must be either 'ton' or 'yard'.")
        return

    try:
        pricing_value = float(pricing_value)
    except ValueError:
        messagebox.showerror("Input Error", "Pricing must be a numeric value.")
        return

    try:
        if pricing_mode == "ton":
            data = fetch_disposal_pricing_diff(start_date, 
                                               end_date, 
                                               pricing_mode, 
                                               ton_pricing=pricing_value)
            ton_pricing = pricing_value
            yard_pricing = None
        else:
            data = fetch_disposal_pricing_diff(start_date, 
                                               end_date, 
                                               pricing_mode, 
                                               yard_pricing=pricing_value)
            ton_pricing = None
            yard_pricing = pricing_value

        print_and_plot_disposal_pricing_diff(
            data,
            start_date,
            end_date,
            pricing_mode,
            ton_pricing=ton_pricing,
            yard_pricing=yard_pricing,
        )
    except Exception:
        LOGGER.exception("Failed to generate disposal pricing difference report.")
        messagebox.showerror(
            "Error",
            "The report could not be generated. Review your inputs and local data setup, then try again.",
        )


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Disposal Pricing Difference")
    root.geometry("430x250")
    root.resizable(False, False)
    root.config(padx=24, pady=24)

    start_date_label = tk.Label(root, text="Start Date YYYY-MM-DD:")
    start_date_label.grid(column=0, row=0, padx=5, pady=5, sticky="e")
    start_date_entry = tk.Entry(root, width=20)
    start_date_entry.grid(column=1, row=0, padx=5, pady=10)

    end_date_label = tk.Label(root, text="End Date YYYY-MM-DD:")
    end_date_label.grid(column=0, row=1, padx=5, pady=5, sticky="e")
    end_date_entry = tk.Entry(root, width=20)
    end_date_entry.grid(column=1, row=1, padx=5, pady=10)

    pricing_mode_var = tk.StringVar(value=str("yard"))
    pricing_var = tk.StringVar(value=str("16"))

    ttk.Label(root, text="Pricing Mode:").grid(column=0, row=2, padx=6, pady=6, sticky="e")
    pricing_mode_options = ttk.Combobox(
        root,
        width=19,
        state="readonly",
        textvariable=pricing_mode_var,
        values=["yard", "ton"],
    )
    pricing_mode_options.grid(column=1, row=2, padx=6, pady=6, sticky="w")

    ttk.Label(root, text="Pricing:").grid(column=0, row=3, padx=6, pady=6, sticky="e")
    pricing_entry = ttk.Entry(root, width=22, textvariable=pricing_var)
    pricing_entry.grid(column=1, row=3, padx=6, pady=6, sticky="w")

    calculate_button = ttk.Button(
        root,
        text="Calculate",
        command=lambda: run_report_from_gui(start_date_entry, end_date_entry, pricing_mode_var, pricing_var),
    )
    calculate_button.grid(column=1, row=4, padx=6, pady=16, sticky="w")

    root.mainloop()
