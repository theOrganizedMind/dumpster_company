import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
import logging
import tkinter as tk
from tkinter import Button, messagebox
from tkinterdnd2 import TkinterDnD
from datetime import datetime, date

from postgresql import fetch_all
from financials_main import monthly_operating_cost


LOGGER = logging.getLogger(__name__)

# ============================================================================ #
# ================================== INFO ==================================== #
# ============================================================================ #
# 
# ============================================================================ #
# ================================== TODO ==================================== #
# ============================================================================ #
#
# ============================================================================ #

PRICING_DIFF_DEFAULT = 50
DEFAULT_COMPANY_NAME = "Example Company" # <-- Add Default Company Name
DEFAULT_DUMPSTER_SIZE = "30 yard"
DEFAULT_MATERIAL_TYPE = "C&D"

# ========================================================================== #
# ======================= PostgreSQL Helper Functions ====================== #
# ========================================================================== #

def format_month_key(value):
    """Normalize a date-like value into a YYYY-MM month key string."""
    if isinstance(value, datetime):
        return value.strftime('%Y-%m')
    if isinstance(value, date):
        return value.strftime('%Y-%m')
    return str(value)[:7]

def fetch_monthly_disposal_cost(start_date, end_date):
    """Fetch monthly disposal totals from PostgreSQL for the provided date range."""
    monthly_costs = {}

    rows = fetch_all(
        "SELECT * FROM monthly_disposal_cost(%s, %s);",
        (start_date, end_date),
    )

    for row in rows:
        if len(row) < 2:
            continue
        month_key = format_month_key(row[0])
        monthly_costs[month_key] = float(row[1])

    return monthly_costs


def fetch_monthly_sales(start_date, end_date):
    """Fetch monthly sales totals from PostgreSQL for the provided date range."""
    monthly_sales_data = {}

    rows = fetch_all(
        "SELECT * FROM monthly_sales(%s, %s);",
        (start_date, end_date),
    )

    for row in rows:
        if len(row) < 2:
            continue
        month_key = format_month_key(row[0])
        monthly_sales_data[month_key] = float(row[1])

    return monthly_sales_data

def fetch_pricing_difference_data(start_date, end_date):
    """Fetch filtered invoicing rows from PostgreSQL for the selected date range."""

    rows = fetch_all(
        """
        SELECT date, price
        FROM invoicing
        WHERE company = %s
          AND size = %s
          AND type = %s
          AND description NOT IN (%s, %s, %s, %s)
          AND date BETWEEN %s AND %s
        ORDER BY date;
        """,
        (
            DEFAULT_COMPANY_NAME,
            DEFAULT_DUMPSTER_SIZE,
            DEFAULT_MATERIAL_TYPE,
            'Initial Drop',
            'Relocate',
            'Dead Haul',
            'Live Load',
            start_date,
            end_date,
        ),
    )

    if not rows:
        return pd.DataFrame(columns=['Date', 'Price'])

    data = pd.DataFrame(rows, columns=['Date', 'Price'])
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
    data['Price'] = pd.to_numeric(data['Price'], errors='coerce').fillna(0)
    return data


def get_required_date_range():
    """Read and validate start/end date values from the GUI."""
    start_date = start_date_entry.get().strip()
    end_date = end_date_entry.get().strip()

    if not start_date or not end_date:
        raise ValueError("Please enter both start and end dates in YYYY-MM-DD format.")

    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    if end < start:
        raise ValueError("End date must be on or after the start date.")

    return start_date, end_date


def process_sql_with_inputs():
    """Process pricing difference using PostgreSQL data for the selected date range."""
    try:
        global PRICING_DIFF, CURRENT_MONTHLY_OPERATING_COST, DEFAULT_COMPANY_NAME, \
        DEFAULT_DUMPSTER_SIZE, DEFAULT_MATERIAL_TYPE
        PRICING_DIFF = float(pricing_diff_var.get())
        CURRENT_MONTHLY_OPERATING_COST = float(operating_cost_var.get())
        DEFAULT_COMPANY_NAME = str(default_company_var.get())
        DEFAULT_DUMPSTER_SIZE = str(default_dumpster_var.get())
        DEFAULT_MATERIAL_TYPE = str(default_material_var.get())


        start_date, end_date = get_required_date_range()
        data = fetch_pricing_difference_data(start_date, end_date)

        if data.empty:
            messagebox.showwarning("No Results", 
                                   "No invoicing data was returned for that date range.")
            return

        sales_data = fetch_monthly_sales(start_date, end_date)
        disposal_data = fetch_monthly_disposal_cost(start_date, end_date)
        if not sales_data or not disposal_data:
            messagebox.showwarning(
                "No Results",
                "No monthly sales/disposal data was returned for that date range.",
            )
            return

        start_month = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y-%m')
        end_month = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y-%m')

        root.withdraw()
        process_pricing_difference(data, sales_data, disposal_data, start_month, end_month)
    except ValueError as exc:
        messagebox.showerror("Input Error", str(exc))
    except Exception as exc:
        LOGGER.exception("Failed to generate pricing difference report.")
        messagebox.showerror(
            "Error",
            "The pricing difference report could not be generated. Review your inputs and local data setup, then try again.",
        )


def process_data(data):
    """
    Process the data by calculating price differences and grouping by month.

    Args:
        data (pd.DataFrame): DataFrame containing the invoicing data.

    Returns:
        tuple: (processed DataFrame, monthly aggregated DataFrame)
    """
    data['Price_Difference'] = data['Price'] - PRICING_DIFF
    data['Month'] = pd.to_datetime(data['Date']).dt.to_period('M')
    monthly = data.groupby('Month').agg({
        'Price': 'sum',
        'Price_Difference': 'sum'
    }).reset_index()
    monthly['Month'] = monthly['Month'].astype(str)
    return data, monthly


def process_pricing_difference(data, sales_source, disposal_source, start_month, end_month):
    """Run pricing-difference calculations and charting for SQL input."""
    filtered_monthly_sales = filter_monthly_dict(sales_source, start_month, end_month)
    filtered_monthly_disposal_cost = filter_monthly_dict(disposal_source, start_month, end_month)

    data, monthly = process_data(data)

    total_original_price = sum(data['Price'])
    print(f"The total original amount = ${total_original_price:,.2f}")

    price_difference = sum(data['Price_Difference'])
    print(f"The total amount after deduct = ${price_difference:,.2f}")

    total_price_difference = total_original_price - price_difference
    print(f"The total price difference = ${total_price_difference:,.2f}")

    percent_difference = (total_price_difference / total_original_price) * 100 if total_original_price else 0
    print(f"The percent difference = {percent_difference:.2f}%")

    sales_minus_disposal = {}
    for month in filtered_monthly_sales:
        if month in filtered_monthly_disposal_cost:
            sales_minus_disposal[month] = filtered_monthly_sales[month] - filtered_monthly_disposal_cost[month]

    if not sales_minus_disposal:
        raise ValueError("No overlapping monthly sales and disposal data for the selected date range.")

    # Calculate adjusted difference using average monthly reduction.
    months_count = len(sales_minus_disposal)
    avg_monthly_reduction = total_price_difference / months_count

    adjusted_sales_minus_disposal = {
        month: value - avg_monthly_reduction
        for month, value in sales_minus_disposal.items()
    }

    total_sales_minus_disposal = (sum(sales_minus_disposal.values()))
    total_adjusted_sales_minus_disposal = (sum(adjusted_sales_minus_disposal.values()))
    print(f"\nTotal sales minus disposal = ${total_sales_minus_disposal:,.2f}")
    print(f"Total adjusted sales minus disposal = ${total_adjusted_sales_minus_disposal:,.2f}")
    total_adjusted_diff = total_sales_minus_disposal - total_adjusted_sales_minus_disposal
    print(f"The total adjusted difference = ${total_adjusted_diff:,.2f}")

    annotation = (
    f"The total original amount = ${total_original_price:,.2f}\n"
    f"The total amount after deduct = ${price_difference:,.2f}\n"
    f"The total price difference = ${total_price_difference:,.2f}\n"
    f"The percent difference = {percent_difference:.2f}%"
    )

    plot_chart(monthly, sales_minus_disposal, adjusted_sales_minus_disposal, annotation)


def plot_chart(monthly, sales_minus_disposal, adjusted_sales_minus_disposal, annotation):
    """
    Plot the line chart comparing sales, disposal costs, and their differences.
    Adds tooltips, gridlines, a horizontal reference line, and annotation.

    Args:
        monthly (pd.DataFrame): Monthly aggregated DataFrame.
        sales_minus_disposal (dict): Dictionary of sales minus disposal cost per month.
        adjusted_sales_minus_disposal (dict): Dictionary of adjusted sales minus disposal per month.
        annotation (str): Annotation text to display on the chart.

    Returns:
        None
    """
    diff_months = list(sales_minus_disposal.keys())
    diff_values = list(sales_minus_disposal.values())
    adj_diff_months = list(adjusted_sales_minus_disposal.keys())
    adj_diff_values = list(adjusted_sales_minus_disposal.values())

    plt.figure(figsize=(10, 6))
    # Plot the difference as line 3
    line1, = plt.plot(diff_months, diff_values, marker='o', 
                    label='Sales - Disposal Cost', color='purple')
    line2, = plt.plot(adj_diff_months, adj_diff_values, marker='o',
                    label='Sales - Disposal (After Deduct)', color='orange'
    )
    plt.xlabel('Month')
    plt.ylabel('Total Amount')
    plt.title(f'Monthly Original Price vs Price After ${PRICING_DIFF:.2f} Difference')
    plt.xticks(rotation=45)
    plt.legend([line1, line2], [line1.get_label(), line2.get_label()], loc='lower right')
    plt.tight_layout()

    # Add the annotation to the top left corner
    plt.text(
        0.01, 0.99, annotation,
        transform=plt.gca().transAxes,
        fontsize=10,
        verticalalignment='top',
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray')
    )

    cursor = mplcursors.cursor([line1, line2], hover=True)
    @cursor.connect('add')
    def on_add(sel):
        line = sel.artist
        idx = int(sel.index)
        # Get the x and y data for the hovered pint
        xdata = line.get_xdata()
        ydata = line.get_ydata()
        month = xdata[idx]
        value = ydata[idx]
        if line is line1:
            sel.annotation.set_text(f"Month: {month}\nSales - Disposal: ${value:,.2f}")
        else:
            sel.annotation.set_text(f"Month: {month}\nAdj. Sales - Disposal ${value:,.2f}")

    plt.grid(True, color='lightgray')

    # Show monthly operating cost horizontal line.
    plt.axhline(y=CURRENT_MONTHLY_OPERATING_COST, color='red', linestyle='--', 
                linewidth=2)
    plt.text(
        0.01, CURRENT_MONTHLY_OPERATING_COST + 2000,
        'Current total monthly operating cost',
        color='red',
        fontsize=10,
        verticalalignment='bottom'
    )

    plt.show()

def filter_monthly_dict(monthly_dict, start_month, end_month):
    """
    Filters a monthly dictionary to only include keys between start_month and 
    end_month (inclusive).
    Args:
        monthly_dict (dict): Dictionary with keys as 'YYYY-MM'.
        start_month (str): Start month in 'YYYY-MM' format.
        end_month (str): End month in 'YYYY-MM' format.
    Returns:
        dict: Filtered dictionary.
    """
    return {month: value for month, value in monthly_dict.items() if start_month <= month <= end_month}


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    root.title(f"Pricing Difference")
    root.geometry("500x400")
    root.config(padx=50, pady=50)

    start_date_label = tk.Label(root, text="Start Date YYYY-MM-DD:")
    start_date_label.grid(column=0, row=0, padx=5, pady=5, sticky="e")
    start_date_entry = tk.Entry(root, width=20)
    start_date_entry.grid(column=1, row=0, padx=5, pady=10)

    end_date_label = tk.Label(root, text="End Date YYYY-MM-DD:")
    end_date_label.grid(column=0, row=1, padx=5, pady=5, sticky="e")
    end_date_entry = tk.Entry(root, width=20)
    end_date_entry.grid(column=1, row=1, padx=5, pady=10)

    pricing_diff_var = tk.StringVar(value=str(PRICING_DIFF_DEFAULT))
    operating_cost_var = tk.StringVar(value=str(monthly_operating_cost))
    default_company_var = tk.StringVar(value=str(DEFAULT_COMPANY_NAME))
    default_dumpster_var = tk.StringVar(value=str(DEFAULT_DUMPSTER_SIZE))
    default_material_var = tk.StringVar(value=str(DEFAULT_MATERIAL_TYPE))

    tk.Label(root, text="Pricing Difference ($):").grid(column=0, 
                                                        row=2,
                                                        pady=5, 
                                                        sticky="e")
    pricing_diff_entry = tk.Entry(root, textvariable=pricing_diff_var)
    pricing_diff_entry.grid(column=1, row=2, pady=5)

    tk.Label(root, text="Current Monthly Operating Cost ($):").grid(column=0, 
                                                                    row=3, 
                                                                    pady=5, 
                                                                    sticky="e")
    operating_cost_entry = tk.Entry(root, textvariable=operating_cost_var)
    operating_cost_entry.grid(column=1, row=3, pady=5)

    tk.Label(root, text="Company Name:").grid(column=0, row=4, pady=5, sticky="e")
    company_entry = tk.Entry(root, textvariable=default_company_var)
    company_entry.grid(column=1, row=4, pady=5)

    tk.Label(root, text="Dumpster Size:").grid(column=0, row=5, pady=5, sticky="e")
    dumpster_entry = tk.Entry(root, textvariable=default_dumpster_var)
    dumpster_entry.grid(column=1, row=5, pady=5)

    tk.Label(root, text="Material Type:").grid(column=0, row=6, pady=5, sticky="e")
    material_entry = tk.Entry(root, textvariable=default_material_var)
    material_entry.grid(column=1, row=6, pady=5)

    Button(root, text="Calculate", 
           command=process_sql_with_inputs).grid(column=1, row=7, padx=10, pady=10)
    
    root.mainloop()
