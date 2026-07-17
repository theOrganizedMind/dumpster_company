import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
import os
import tkinter as tk
from tkinter import filedialog, Label, Button, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from idlelib.tooltip import Hovertip

from disposal import monthly_disposal_cost
from monthly_sales import monthly_sales
from financials_main import monthly_operating_cost

# ============================================================================ #
# ================================== INFO ==================================== #
# ============================================================================ #
# This program subtracts the 'PRICING_DIFF' from the original price and displays
# a line chart of the original price amount and the adjusted price amount after
# subtracting the percent difference. This program was created to show the difference
# in revenue from lowering pricing from $800 to $750.
# This program automatically takes the beginning and ending date from the excel
# file and matches it to the monthly_disposal_cost and monthly_sales keys and 
# displays the matching months for that date range.  
# Steps:
# 1.) Filter Invoicing Board by Company, 30 yard, C&D, Price <= 1000, 
# do not include Initial Drop, Recycling, Clean-fill, Relocate or Dead-haul.
# - Initial Date Range before price change.
# ============================================================================ #
# ================================== TODO ==================================== #
# ============================================================================ #
#
# ============================================================================ #

PRICING_DIFF_DEFAULT = 50

def create_tooltip(widget, text):
    """Creates tooltips for the tkinter widgets"""
    Hovertip(widget, text, hover_delay=500)


def process_with_inputs(file_path):
    """
    Retrieves user input values from the entry widgets, converts them to the 
    appropriate types, and sets the global variables PRICING_DIFF, 
    CURRENT_MONTHLY_OPERATING_COST, and NUM_MONTHS_TO_INCLUDE.
    Then hides the main window and processes the selected file using these parameters.

    Args:
        file_path (str): Path to the selected Excel file.

    Raises:
        Shows a messagebox if any input value is invalid.
    """
    try:
        global PRICING_DIFF, CURRENT_MONTHLY_OPERATING_COST
        PRICING_DIFF = float(pricing_diff_var.get())
        CURRENT_MONTHLY_OPERATING_COST = float(operating_cost_var.get())
        root.withdraw()
        process_file(file_path)
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers for all fields.")


def select_file():
    """Open a file dialog for the user to select an Excel file."""
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if file_path:
        process_with_inputs(file_path)


def handle_drop(event):
    """Handle drag-and-drop event for an Excel file."""
    file_path = event.data.strip('{}')
    process_with_inputs(file_path)


def load_data(filepath):
    """
    Load the invoicing Excel file and validate required columns.

    Args:
        filepath (str): Path to the Excel file.

    Returns:
        pd.DataFrame: DataFrame containing the loaded data.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If required columns are missing.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    data = pd.read_excel(filepath, engine="openpyxl", header=2, skipfooter=1)
    if 'Price' not in data.columns or 'Date' not in data.columns:
        raise ValueError("Excel file must contain 'Price' and 'Date' columns.")
    # Clean data
    data['Price'] = pd.to_numeric(data['Price'], errors='coerce').fillna(0)
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
    return data


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

def process_file(file_path):
    try:
        data = load_data(file_path)
        min_date = data['Date'].min()
        max_date = data['Date'].max()
        start_month = min_date.strftime('%Y-%m')
        end_month = max_date.strftime('%Y-%m')

        filtered_monthly_sales = filter_monthly_dict(monthly_sales, start_month, end_month)
        filtered_monthly_disposal_cost = filter_monthly_dict(monthly_disposal_cost, start_month, end_month)

        data, monthly = process_data(data)

        total_original_price = sum(data['Price'])
        print(f"The total original amount = ${total_original_price:,.2f}")

        price_difference = sum(data['Price_Difference'])
        print(f"The total amount after deduct = ${price_difference:,.2f}")

        total_price_difference = total_original_price - price_difference
        print(f"The total price difference = ${total_price_difference:,.2f}")

        percent_difference = (total_price_difference / total_original_price) * 100
        print(f"The percent difference = {percent_difference:.2f}%")

        sales_minus_disposal = {}
        for month in filtered_monthly_sales:
            if month in filtered_monthly_disposal_cost:
                sales_minus_disposal[month] = filtered_monthly_sales[month] - filtered_monthly_disposal_cost[month]

        # Calcuate the adjusted difference
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
    except Exception as e:
        messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    root.title(f"Pricing Difference")
    root.geometry("500x400")
    root.config(padx=50, pady=50)

    pricing_diff_var = tk.StringVar(value=str(PRICING_DIFF_DEFAULT))
    operating_cost_var = tk.StringVar(value=str(monthly_operating_cost))

    tk.Label(root, text="Pricing Difference ($):").grid(column=0, 
                                                        row=0,
                                                        pady=5, 
                                                        sticky="e")
    pricing_diff_entry = tk.Entry(root, textvariable=pricing_diff_var)
    pricing_diff_entry.grid(column=1, row=0, pady=5)

    tk.Label(root, text="Current Monthly Operating Cost ($):").grid(column=0, 
                                                                    row=1, 
                                                                    pady=5, 
                                                                    sticky="e")
    operating_cost_entry = tk.Entry(root, textvariable=operating_cost_var)
    operating_cost_entry.grid(column=1, row=1, pady=5)

    select_file_label = Label(root, text="Select or Drag and Drop the Excel file for Pricing Difference (Tooltip)")
    select_file_label.grid(column=0, row=3, columnspan=2, pady=10)
    create_tooltip(select_file_label, "This program subtracts the pricing difference \n"
                   "from the original price and displays a line chart of the \n"
                   "original price amount and the adjusted price amount after \n"
                    "subtracting the average difference.\n"
                    "Steps:\n"
                    "1.) Filter Invoicing Board by Company, Dumpster Size, C&D, Price <= 1000, \n"
                    "do not include Initial Drop, Recycling, Clean-fill, Relocate or Dead-haul.\n"
                )
    drop_label = Label(root, text="Drag and drop file here", relief="ridge", 
                       width=40, height=3)
    drop_label.grid(column=0, row=4, columnspan=2, pady=10)
    drop_label.drop_target_register(DND_FILES)
    drop_label.dnd_bind('<<Drop>>', handle_drop)

    Button(root, text="Browse", command=select_file).grid(column=0, row=5, 
                                                          columnspan=2, 
                                                          padx=10, pady=10)
    root.mainloop()
