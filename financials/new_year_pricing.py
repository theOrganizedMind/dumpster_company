from datetime import datetime
import logging
import pandas as pd
import tkinter as tk
from tkinter import messagebox, ttk

from postgresql import fetch_all
from financials_main import daily_operating_cost, PROFIT


LOGGER = logging.getLogger(__name__)

# =========================================================================== #
# ================================ INFO ===================================== #
# =========================================================================== #
# This program calculates recommended new year pricing using invoicing rows
# pulled directly from PostgreSQL.
# =========================================================================== #
# ================================= TODO ==================================== #
# =========================================================================== #
# TODO:
# =========================================================================== #

REQUIRED_COLUMNS = [
    "Description", "Size", "Type", "Date", "Disposal Cost", "Tons",
]


def fetch_new_year_pricing_data(start_date, end_date):
    """Fetch required invoicing rows from PostgreSQL for the selected date range."""
    query = """
        SELECT
            i.description AS "Description",
            i.size AS "Size",
            i.type AS "Type",
            i.date AS "Date",
            i.disposalcost AS "Disposal Cost",
            i.tons AS "Tons"
        FROM invoicing i
        WHERE i.date BETWEEN %s AND %s
        ORDER BY i.date;
    """

    rows, columns = fetch_all(
        query,
        (start_date, end_date),
        include_columns=True,
    )

    if not rows:
        return pd.DataFrame(columns=columns)

    data = pd.DataFrame(rows, columns=columns)
    data = data.fillna(0)

    for col in ["Disposal Cost", "Tons"]:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)

    data["Description"] = data["Description"].astype(str).str.strip().str.lower()
    data["Size"] = data["Size"].astype(str).str.strip().str.lower()
    data["Type"] = data["Type"].astype(str).str.strip().str.lower()
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce").dt.date

    return data


def cal_category_stats(df, base_price, tons_col=True):
    """Calculate average disposal, average tons, and category price."""
    avg_disposal = df["Disposal Cost"].mean() if not df["Disposal Cost"].isna().all() else 0
    avg_tons = df["Tons"].mean() if tons_col and not df["Tons"].isna().all() else "N/A"
    price = round(base_price + avg_disposal, 2)
    return avg_disposal, avg_tons, price


def calculate_new_year_pricing(data, daily_operating_cost_value, profit_margin_value):
    """Run pricing calculations and return categorized results and totals."""
    missing = [col for col in REQUIRED_COLUMNS if col not in data.columns]
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")

    num_unique_days = data["Date"].nunique()
    if num_unique_days == 0:
        raise ValueError("No valid dates were returned for this range.")

    initial_drop = data[data["Description"] == "initial drop"]
    cnd_30 = data[(data["Size"] == "30 yard") & (data["Type"] == "c&d") & (data["Description"] != "initial drop")]
    recycling_30 = data[(data["Size"] == "30 yard") & (data["Type"] == "recycling") & (data["Description"] != "initial drop")]
    cleanfill_30 = data[(data["Size"] == "30 yard") & (data["Type"] == "clean-fill") & (data["Description"] != "initial drop")]
    cnd_20 = data[(data["Size"] == "20 yard") & (data["Type"] == "c&d") & (data["Description"] != "initial drop")]
    cleanfill_20 = data[(data["Size"] == "20 yard") & (data["Type"] == "clean-fill") & (data["Description"] != "initial drop")]

    initial_drop_avg = initial_drop.shape[0] / num_unique_days
    cnd_30_avg = cnd_30.shape[0] / num_unique_days
    recycling_30_avg = recycling_30.shape[0] / num_unique_days
    cleanfill_30_avg = cleanfill_30.shape[0] / num_unique_days
    cnd_20_avg = cnd_20.shape[0] / num_unique_days
    cleanfill_20_avg = cleanfill_20.shape[0] / num_unique_days

    total_avg_dumpsters_per_day = (
        initial_drop_avg + cnd_30_avg + recycling_30_avg + cleanfill_30_avg + cnd_20_avg + cleanfill_20_avg
    )
    if total_avg_dumpsters_per_day == 0:
        raise ValueError("No qualifying dumpster runs found in this date range.")

    total_overhead_with_profit = daily_operating_cost_value * profit_margin_value
    base_price = total_overhead_with_profit / total_avg_dumpsters_per_day
    initial_drop_price = round(base_price * 0.8, 2)

    results = []

    if not initial_drop.empty:
        results.append({
            "Category": "Initial Drop",
            "Avg Dumpsters Per Day": round(initial_drop_avg, 2),
            "Avg Disposal Cost": 0,
            "Avg Tons": "N/A",
            "Recommended New Year Price": initial_drop_price,
        })

    if not cnd_30.empty:
        avg_disposal, avg_tons, price = cal_category_stats(cnd_30, base_price)
        results.append({
            "Category": "30 yard C&D",
            "Avg Dumpsters Per Day": round(cnd_30_avg, 2),
            "Avg Disposal Cost": round(avg_disposal, 2),
            "Avg Tons": round(avg_tons, 2),
            "Recommended New Year Price": price,
        })

    if not recycling_30.empty:
        avg_disposal, avg_tons, price = cal_category_stats(recycling_30, base_price)
        results.append({
            "Category": "30 yard Recycling",
            "Avg Dumpsters Per Day": round(recycling_30_avg, 2),
            "Avg Disposal Cost": 0,
            "Avg Tons": round(avg_tons, 2),
            "Recommended New Year Price": price,
        })

    if not cleanfill_30.empty:
        avg_disposal, _, price = cal_category_stats(cleanfill_30, base_price, tons_col=False)
        results.append({
            "Category": "30 yard Clean Fill",
            "Avg Dumpsters Per Day": round(cleanfill_30_avg, 2),
            "Avg Disposal Cost": round(avg_disposal, 2),
            "Avg Tons": "N/A",
            "Recommended New Year Price": price,
        })

    if not cnd_20.empty:
        avg_disposal, avg_tons, price = cal_category_stats(cnd_20, base_price)
        results.append({
            "Category": "20 yard C&D",
            "Avg Dumpsters Per Day": round(cnd_20_avg, 2),
            "Avg Disposal Cost": round(avg_disposal, 2),
            "Avg Tons": round(avg_tons, 2),
            "Recommended New Year Price": price,
        })

    if not cleanfill_20.empty:
        avg_disposal, _, price = cal_category_stats(cleanfill_20, base_price, tons_col=False)
        results.append({
            "Category": "20 yard Clean Fill",
            "Avg Dumpsters Per Day": round(cleanfill_20_avg, 2),
            "Avg Disposal Cost": round(avg_disposal, 2),
            "Avg Tons": "N/A",
            "Recommended New Year Price": price,
        })

    total_daily_revenue = sum(r["Recommended New Year Price"] * r["Avg Dumpsters Per Day"] for r in results)
    scaling_factor = total_overhead_with_profit / total_daily_revenue if total_daily_revenue else 1

    for r in results:
        r["Recommended New Year Price"] = round(r["Recommended New Year Price"] * scaling_factor, 2)

    other_prices = [r["Recommended New Year Price"] for r in results if r["Category"] != "Initial Drop"]
    min_other_price = min(other_prices) if other_prices else None
    for r in results:
        if r["Category"] == "Initial Drop" and min_other_price is not None:
            r["Recommended New Year Price"] = round(min_other_price * 0.8, 2)

    total_daily_revenue = sum(r["Recommended New Year Price"] * r["Avg Dumpsters Per Day"] for r in results)
    return results, total_daily_revenue, total_overhead_with_profit


def print_results(results, total_daily_revenue, total_overhead_with_profit):
    """Print pricing results to the terminal."""
    print("\nRecommended New Year Pricing:")
    for r in results:
        print(f"{r['Category']}")
        print(f"    Avg Dumpsters/Day: {r['Avg Dumpsters Per Day']}")
        print(f"    Avg Disposal Cost: ${r['Avg Disposal Cost']}")
        print(f"    Avg Tons: {r.get('Avg Tons', 'N/A')}")
        print(f"    Recommended New Year Price: ${r['Recommended New Year Price']}\n")

    print(f"Total daily revenue (price * avg dumpsters/day): ${total_daily_revenue:,.2f}")
    print(f"Total daily overhead with profit: ${total_overhead_with_profit:,.2f}")
    print(f"Difference (Revenue - Overhead): ${total_daily_revenue - total_overhead_with_profit:,.2f}")


def show_results_popup(results, total_daily_revenue, total_overhead_with_profit, start_date, end_date):
    """Display pricing results in a popup window."""
    popup = tk.Toplevel(root)
    popup.title("New Year Pricing Results")
    popup.geometry("820x420")

    text = tk.Text(popup, wrap="none", font=("Consolas", 10))
    text.pack(expand=True, fill="both", padx=10, pady=10)

    text.insert("end", f"Recommended New Year Pricing ({start_date} to {end_date})\n")
    text.insert("end", "-" * 110 + "\n")
    text.insert(
        "end",
        f"{'Category':<24}{'Avg Dumpsters/Day':>20}{'Avg Disposal Cost':>22}{'Avg Tons':>14}{'Recommended Price':>20}\n",
    )
    text.insert("end", "-" * 110 + "\n")

    for r in results:
        avg_tons = r.get("Avg Tons", "N/A")
        avg_tons_display = f"{avg_tons:.2f}" if isinstance(avg_tons, (int, float)) else str(avg_tons)
        text.insert(
            "end",
            f"{r['Category']:<24}{r['Avg Dumpsters Per Day']:>20.2f}{r['Avg Disposal Cost']:>22.2f}{avg_tons_display:>14}{r['Recommended New Year Price']:>20.2f}\n",
        )

    text.insert("end", "\n" + "-" * 110 + "\n")
    text.insert("end", f"Total daily revenue (price * avg dumpsters/day): ${total_daily_revenue:,.2f}\n")
    text.insert("end", f"Total daily overhead with profit: ${total_overhead_with_profit:,.2f}\n")
    text.insert("end", f"Difference (Revenue - Overhead): ${total_daily_revenue - total_overhead_with_profit:,.2f}\n")
    text.config(state="disabled")


def process_sql_with_inputs():
    """Read GUI values, fetch SQL data, run pricing calculations, and display results."""
    try:
        start_date = start_date_entry.get().strip()
        end_date = end_date_entry.get().strip()

        if not start_date or not end_date:
            raise ValueError("Please enter both start and end dates in YYYY-MM-DD format.")

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        if end < start:
            raise ValueError("End date must be on or after the start date.")

        daily_cost_value = float(operating_cost_var.get())
        profit_margin_value = float(profit_margin_var.get())

        data = fetch_new_year_pricing_data(start_date, end_date)
        if data.empty:
            messagebox.showwarning("No Results", "No invoicing data was returned for that date range.")
            return

        results, total_daily_revenue, total_overhead_with_profit = calculate_new_year_pricing(
            data,
            daily_cost_value,
            profit_margin_value,
        )

        print_results(results, total_daily_revenue, total_overhead_with_profit)
        show_results_popup(results, total_daily_revenue, total_overhead_with_profit, start_date, end_date)

    except ValueError as exc:
        messagebox.showerror("Input Error", str(exc))
    except Exception as exc:
        LOGGER.exception("Failed to generate new year pricing report.")
        messagebox.showerror(
            "Error",
            "The pricing report could not be generated. Review your inputs and local data setup, then try again.",
        )


if __name__ == "__main__":
    root = tk.Tk()
    root.title("New Year Pricing")
    root.geometry("390x245")
    root.config(padx=20, pady=20)

    operating_cost_var = tk.StringVar(value=str(daily_operating_cost))
    profit_margin_var = tk.StringVar(value=str(PROFIT))

    ttk.Label(root, text="Start Date YYYY-MM-DD:").grid(column=0, row=0, padx=5, pady=5, sticky="e")
    start_date_entry = ttk.Entry(root, width=20)
    start_date_entry.grid(column=1, row=0, padx=5, pady=8)

    ttk.Label(root, text="End Date YYYY-MM-DD:").grid(column=0, row=1, padx=5, pady=5, sticky="e")
    end_date_entry = ttk.Entry(root, width=20)
    end_date_entry.grid(column=1, row=1, padx=5, pady=8)

    ttk.Label(root, text="Daily Operating Cost:").grid(column=0, row=2, padx=5, pady=8, sticky="e")
    operating_cost_entry = ttk.Entry(root, width=20, textvariable=operating_cost_var)
    operating_cost_entry.grid(column=1, row=2, padx=5, pady=8)

    ttk.Label(root, text="Profit Margin:").grid(column=0, row=3, padx=5, pady=8, sticky="e")
    profit_margin_entry = ttk.Entry(root, width=20, textvariable=profit_margin_var)
    profit_margin_entry.grid(column=1, row=3, padx=5, pady=8)

    calculate_button = ttk.Button(root, text="Calculate", command=process_sql_with_inputs)
    calculate_button.grid(column=1, row=4, padx=5, pady=10, sticky="w")

    root.mainloop()
