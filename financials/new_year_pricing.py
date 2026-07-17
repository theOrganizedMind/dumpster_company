import pandas as pd
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import os
from tkinter import filedialog, Label, Button
from tkinterdnd2 import DND_FILES, TkinterDnD

from financials_main import daily_operating_cost, PROFIT

# =========================================================================== #
# ================================ INFO ===================================== #
# =========================================================================== #
# This program is an interactive financial analysis tool for calculating 
# recommended new year pricing for dumpster services. It allows users to 
# select or drag-and-drop an Excel file containing operational data, and 
# adjust key financial parameters (daily operating cost and profit margin) 
# via the GUI. The program categorizes dumpster runs by type and size, 
# computes average disposal costs and tons, and uses these metrics to recommend 
# new year pricing for each category. Results are scaled to ensure total 
# daily revenue matches the overhead plus profit, and can be printed or 
# exported to Excel for further review.
# Steps:
# 1.) Export data to excel, drag and drop to process data. No filters added.
# =========================================================================== #
# ================================= TODO ==================================== #
# =========================================================================== #
# TODO: 
# =========================================================================== #

REQUIRED_COLUMNS = [
    'Description', 'Size', 'Type', 'Date', 'Disposal Cost', 'Tons',
    ]


todays_date = datetime.now().strftime("%m%d%Y")


def select_file():
    """
    Opens a file dialog for the user to select an Excel file (.xlsx or .xls).
    If a file is selected, closes the main window and processes the file.

    Returns:
        None
    """
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if file_path:
        root.withdraw()
        process_file(
            file_path, 
            float(operating_cost_var.get()),
            float(profit_margin_var.get())
        )

def handle_drop(event):
    """
    Handles the drag-and-drop event for an Excel file.
    Hides the main window and processes the dropped file.

    Args:
        event: The TkinterDnD event containing the file path.

    Returns:
        None
    """
    file_path = event.data.strip('{}')
    # root.quit()
    root.withdraw()  # Hide the main window
    process_file(
        file_path,
        float(operating_cost_var.get()),
        float(profit_margin_var.get())
    )

def cal_category_stats(df, avg_per_day, base_price, tons_col=True):
    """
    Calculates average disposal cost, average tons, and recommended price for a dumpster category.

    Args:
        df (pd.DataFrame): Filtered DataFrame for the category.
        avg_per_day (float): Average dumpsters per day for the category.
        base_price (float): Base price per dumpster before disposal cost.
        tons_col (bool, optional): Whether to calculate average tons. Defaults to True.

    Returns:
        tuple: (avg_disposal, avg_tons, price)
            avg_disposal (float): Average disposal cost for the category.
            avg_tons (float or str): Average tons for the category, or 'N/A' if not applicable.
            price (float): Recommended price for the category.
    """
    avg_disposal = df['Disposal Cost'].mean() if not df['Disposal Cost'].isna().all() else 0
    avg_tons = df['Tons'].mean() if tons_col and not df['Tons'].isna().all() else 'N/A'
    price = round(base_price + avg_disposal, 2)
    return avg_disposal, avg_tons, price

def process_file(file_path, DAILY_OPERATING_COST, PROFIT_MARGIN):
    """
    Processes the selected or dropped Excel file to calculate recommended pricing.
    Fills all empty or NaN values with 0.
    """
    try:
        data = pd.read_excel(file_path, engine="openpyxl", header=2, skipfooter=1)
    except Exception as e:
        messagebox.showerror("File Error", f"Could not read excel file:\n{e}")
        return
    
    data = data.fillna(0)

    for col in ['Disposal Cost', 'Tons']:
        data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)

    missing = [col for col in REQUIRED_COLUMNS if col not in data.columns]
    if missing:
        messagebox.showerror("Missing Columns", f"Missing columns: {', '.join(missing)}")
        return

    # Normalize colums for consistent matching
    data['Description'] = data["Description"].str.strip().str.lower()
    data['Size'] = data["Size"].astype(str).str.strip().str.lower()
    data['Type'] = data['Type'].str.strip().str.lower()
    data['Date'] = pd.to_datetime(data['Date']).dt.date

    num_unique_days = data['Date'].nunique()

    # Calculate average dumpsters per day for each category
    initial_drop = data[data['Description'] == 'initial drop']
    cnd_30 = data[(data['Size'] == '30 yard') & (data['Type'] == 'c&d') 
                  & (data['Description'] != 'initial drop')]
    recycling_30 = data[(data['Size'] == '30 yard') & (data['Type'] == 'recycling') 
                        & (data['Description'] != 'initial drop')]
    cleanfill_30 = data[(data['Size'] == '30 yard') & (data['Type'] == 'clean-fill') 
                        & (data['Description'] != 'initial drop')]
    cnd_20 = data[(data['Size'] == '20 yard') & (data['Type'] == 'c&d') 
                  & (data['Description'] != 'initial drop')]
    cleanfill_20 = data[(data['Size'] == '20 yard') & (data['Type'] == 'clean-fill') 
                        & (data['Description'] != 'initial drop')]

    initial_drop_avg = initial_drop.shape[0] / num_unique_days if num_unique_days else 0
    cnd_30_avg = cnd_30.shape[0] / num_unique_days if num_unique_days else 0
    recycling_30_avg = recycling_30.shape[0] / num_unique_days if num_unique_days else 0
    cleanfill_30_avg = cleanfill_30.shape[0] / num_unique_days if num_unique_days else 0
    cnd_20_avg = cnd_20.shape[0] / num_unique_days if num_unique_days else 0
    cleanfill_20_avg = cleanfill_20.shape[0] / num_unique_days if num_unique_days else 0

    total_avg_dumpsters_per_day = (initial_drop_avg + cnd_30_avg + recycling_30_avg 
                                   + cleanfill_30_avg + cnd_20_avg + cleanfill_20_avg)

    # Calculate base cost per dumpster so that sum of all category revenues matches total overhead with profit
    total_overhead_with_profit = DAILY_OPERATING_COST * PROFIT_MARGIN

    # Calculate base price per dumpster (excluding disposal)
    base_price = total_overhead_with_profit / total_avg_dumpsters_per_day if total_avg_dumpsters_per_day else 0

    # Initial Drop price (80% of base price, always lowest)
    initial_drop_price = round(base_price * 0.8, 2)

    results = []

    # 1. Initial Drop (all sizes/types)
    if not initial_drop.empty:
        results.append({
            'Category': 'Initial Drop',
            'Avg Dumpsters Per Day': round(initial_drop_avg, 2),
            'Avg Disposal Cost': 0,
            'Recommended New Year Price': initial_drop_price
        })

    # 2. 30 yard C&D (excluding Initial Drop)
    if not cnd_30.empty:
        avg_disposal, avg_tons, price = cal_category_stats(cnd_30, cnd_30_avg, base_price)
        results.append({
            'Category': '30 yard C&D',
            'Avg Dumpsters Per Day': round(cnd_30_avg, 2),
            'Avg Disposal Cost': round(avg_disposal, 2),
            'Avg Tons': round(avg_tons, 2),
            'Recommended New Year Price': price
        })

    # 3. 30 yard Recycling (excluding Initial Drop)
    if not recycling_30.empty:
        avg_disposal, avg_tons, price = cal_category_stats(recycling_30, recycling_30_avg, base_price)
        results.append({
            'Category': '30 yard Recycling',
            'Avg Dumpsters Per Day': round(recycling_30_avg, 2),
            'Avg Disposal Cost': 0,
            'Avg Tons': round(avg_tons, 2),
            'Recommended New Year Price': price
        })

    # 4. 30 yard Clean Fill (excluding Initial Drop)
    if not cleanfill_30.empty:
        avg_disposal, avg_tons, price = cal_category_stats(cleanfill_30, cleanfill_30_avg, base_price)
        results.append({
            'Category': '30 yard Clean Fill',
            'Avg Dumpsters Per Day': round(cleanfill_30_avg, 2),
            'Avg Disposal Cost': round(avg_disposal, 2),
            'Avg Tons': 'N/A',
            'Recommended New Year Price': price
        })

    # 5. 20 yard C&D (excluding Initial Drop)
    if not cnd_20.empty:
        avg_disposal, avg_tons, price = cal_category_stats(cnd_20, cnd_20_avg, base_price)
        results.append({
            'Category': '20 yard C&D',
            'Avg Dumpsters Per Day': round(cnd_20_avg, 2),
            'Avg Disposal Cost': round(avg_disposal, 2),
            'Avg Tons': round(avg_tons, 2),
            'Recommended New Year Price': price
        })

    # 6. 20 yard Clean Fill (excluding Initial Drop)
    if not cleanfill_20.empty:
        avg_disposal, avg_tons, price = cal_category_stats(cleanfill_20, cleanfill_20_avg, base_price)
        results.append({
            'Category': '20 yard Clean Fill',
            'Avg Dumpsters Per Day': round(cleanfill_20_avg, 2),
            'Avg Disposal Cost': round(avg_disposal, 2),
            'Avg Tons': 'N/A',
            'Recommended New Year Price': price
        })

    # Calculate total daily revenue with current prices
    total_daily_revenue = sum(r['Recommended New Year Price'] * r['Avg Dumpsters Per Day'] for r in results)

    # Calculate scaling factor to bring total revenue closer to overhead+profit
    scaling_factor = total_overhead_with_profit / total_daily_revenue if total_daily_revenue else 1

    # Scale prices
    for r in results:
        r['Recommended New Year Price'] = round(r['Recommended New Year Price'] * scaling_factor, 2)

    # Ensure Initial Drop is always less than other categories
    other_prices = [r['Recommended New Year Price'] for r in results if r['Category'] != 'Initial Drop']
    min_other_price = min(other_prices) if other_prices else None
    for r in results:
        if r['Category'] == 'Initial Drop' and min_other_price is not None:
            r['Recommended New Year Price'] = round(min_other_price * 0.8, 2)

    # Print results in desired format
    print("\nRecommended New Year Pricing:")
    for r in results:
        print(f"{r['Category']}")
        print(f"    Avg Dumpsters/Day: {r['Avg Dumpsters Per Day']}")
        print(f"    Avg Disposal Cost: ${r['Avg Disposal Cost']}")
        print(f"    Avg Tons: {r.get('Avg Tons', 'N/A')}")
        print(f"    Recommended New Year Price: ${r['Recommended New Year Price']}\n")

    # Calculate total daily revenue (price * avg dumpsters/day for each category)
    total_daily_revenue = sum(r['Recommended New Year Price'] * r['Avg Dumpsters Per Day'] for r in results)

    print(f"Total daily revenue (price * avg dumpsters/day): ${total_daily_revenue:,.2f}")
    print(f"Total daily overhead with profit: ${total_overhead_with_profit:,.2f}")
    print(f"Difference (Revenue - Overhead): ${total_daily_revenue - total_overhead_with_profit:,.2f}")
    
    save_to_excel = messagebox.askyesno("Save to Excel", "Do you want to save the categorized and predicted data to an Excel file?")
    if save_to_excel:
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        file_path = os.path.join(downloads_folder, f"tdc_new_year_pricing_{todays_date}.xlsx")
        pd.DataFrame(results).to_excel(file_path, index=False)
        messagebox.showinfo("File Saved", f"Data saved to {file_path}")


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    root.title("New Year Pricing")
    root.geometry("600x300")
    root.config(padx=20, pady=20)

    operating_cost_var = tk.StringVar(value=str(daily_operating_cost))
    profit_margin_var = tk.StringVar(value=str(PROFIT))

    Label(root, text="Daily Operating Cost:").pack()
    operating_cost_entry = tk.Entry(root, textvariable=operating_cost_var)
    operating_cost_entry.pack()

    Label(root, text="Profit Margin:").pack()
    profit_margin_entry = tk.Entry(root, textvariable=profit_margin_var)
    profit_margin_entry.pack()

    Label(root, text="Select or Drag and Drop the Excel file for New Year Pricing").pack(pady=10)
    drop_label = Label(root, text="Drag and drop file here", relief="ridge", width=40, height=3)
    drop_label.pack(pady=10)
    drop_label.drop_target_register(DND_FILES)
    drop_label.dnd_bind('<<Drop>>', handle_drop)
    Button(root, text="Browse", command=select_file).pack(pady=10)
    root.mainloop()
