import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
import tkinter as tk
from tkinter import filedialog, ttk

from postgresql import get_db_connection

# ========================================================================== #
# ================================ INFO ==================================== #
# ========================================================================== #
# 
# =========================================================================== #
# ================================= TODO ==================================== #
# =========================================================================== #
# TODO: 
# =========================================================================== #

DEFAULT_START_DATE = "2026-01-01"
DEFAULT_END_DATE = "2026-06-30"

# Fictitious data used when "Sample Data" is selected (no SQL/Excel source required).
SAMPLE_DRIVER_STATS = [
    ("Marcus Reid", 182, 45620.00, 128940.00, 83320.00, 64.62),
    ("Talia Novak", 165, 41230.00, 116850.00, 75620.00, 64.72),
    ("Dominic Farro", 149, 37040.00, 104580.00, 67540.00, 64.59),
    ("Priya Sathe", 133, 33125.00, 93460.00, 60335.00, 64.56),
    ("Isaiah Blackwood", 118, 29310.00, 82670.00, 53360.00, 64.55),
    ("Renee Castellan", 96, 23880.00, 67350.00, 43470.00, 64.54),
]

def get_sample_driver_stats():
    """Return a fictitious sample dataset for demo purposes when no SQL/Excel source is available."""
    return list(SAMPLE_DRIVER_STATS)


def fetch_get_driver_totals(start_date, end_date):
    """Fetch 10 largest projects from PostgreSQL for the provided date range."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT * 
                FROM get_driver_totals(%s, %s)
                WHERE driver IS NOT NULL
                ORDER BY total_price DESC;
                """,
                (start_date, end_date),
            )
            rows = cur.fetchall()

    if not rows:
        print("No projects found for the selected date range.")
        return []

    NUMERIC_COL_WIDTH = 20
    driver_width = max(len("Driver"), max(len(driver) for driver, _, _, _, _, _ in rows)) + 3
    dumpster_count_width = NUMERIC_COL_WIDTH
    total_disposal_cost_width = NUMERIC_COL_WIDTH
    total_price_width = NUMERIC_COL_WIDTH
    total_gross_profit_width = NUMERIC_COL_WIDTH
    gross_profit_percent_width = NUMERIC_COL_WIDTH
    divider_width = (driver_width + dumpster_count_width + total_disposal_cost_width
                    + total_price_width + total_gross_profit_width + gross_profit_percent_width)
    row_format = (
        f"{{driver:<{driver_width}}}{{dumpster_count:>{dumpster_count_width}}}"
        f"{{total_disposal_cost:>{total_disposal_cost_width}}}{{total_price:>{total_price_width}}}"
        f"{{total_gross_profit:>{total_gross_profit_width}}}{{gross_profit_percent:>{gross_profit_percent_width}}}"
    )

    print(f"\nDriver Stats ({start_date} to {end_date})")
    print("-" * divider_width)
    print(row_format.format(driver="Driver", 
                            dumpster_count="Dumpster Count", 
                            total_disposal_cost="Disposal Cost", 
                            total_price="Total Price",
                            total_gross_profit="Gross Profit",
                            gross_profit_percent="Gross Profit Percent"))
    print("-" * divider_width)

    for driver, dumpster_count, total_disposal_cost, total_price, total_gross_profit, gross_profit_percent in rows:
        print(row_format.format(driver=driver, 
                                dumpster_count=int(dumpster_count),
                                total_disposal_cost=f"${float(total_disposal_cost):,.2f}",
                                total_price=f"${float(total_price):,.2f}",
                                total_gross_profit=f"${float(total_gross_profit):,.2f}",
                                gross_profit_percent=f"{float(gross_profit_percent):,.2f}%"))

    return rows


def plot_driver_stats(df):
    """
    Plots driver stats in a single figure with:
    - Top left: horizontal bar chart of dumpster count by driver (hover tooltips).
    - Bottom left: grouped bar chart of disposal cost and total price by driver.
    - Right: pie chart of gross profit by driver with a legend showing gross
      profit percent next to each driver's name.

    Args:
        df (DataFrame): DataFrame with Driver, Dumpster_Count,
            Total_Disposal_Cost, Total_Price, and Total_Gross_Profit columns.

    Returns:
        None
    """
    chart_df = df.copy()
    numeric_cols = ['Dumpster_Count', 'Total_Disposal_Cost', 'Total_Price', 'Total_Gross_Profit']
    chart_df[numeric_cols] = chart_df[numeric_cols].apply(pd.to_numeric, errors='coerce')

    bar_df = chart_df.sort_values('Dumpster_Count', ascending=True)
    grouped_df = chart_df.sort_values('Total_Price', ascending=False)
    pie_df = chart_df.sort_values('Total_Gross_Profit', ascending=False)

    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(2, 2)
    ax_bar = fig.add_subplot(gs[0, 0])
    ax_grouped = fig.add_subplot(gs[1, 0])
    ax_pie = fig.add_subplot(gs[:, 1])

    bars = ax_bar.barh(bar_df['Driver'].astype(str), bar_df['Dumpster_Count'], color='steelblue')
    ax_bar.set_xlabel('Dumpster Count')
    ax_bar.set_title('Dumpster Count by Driver')

    bar_cursor = mplcursors.cursor(bars, hover=True)
    bar_cursor.connect(
        "add",
        lambda sel: sel.annotation.set_text(f"{bar_df['Dumpster_Count'].iloc[sel.index]:,.0f}"),
    )

    x_positions = range(len(grouped_df))
    bar_width = 0.35
    disposal_bars = ax_grouped.bar(
        [x - bar_width / 2 for x in x_positions],
        grouped_df['Total_Disposal_Cost'],
        bar_width,
        label='Disposal Cost',
        color='indianred',
    )
    price_bars = ax_grouped.bar(
        [x + bar_width / 2 for x in x_positions],
        grouped_df['Total_Price'],
        bar_width,
        label='Total Price',
        color='seagreen',
    )
    ax_grouped.set_xticks(list(x_positions))
    ax_grouped.set_xticklabels(grouped_df['Driver'].astype(str), rotation=45, ha='right')
    ax_grouped.set_ylabel('$')
    ax_grouped.set_title('Disposal Cost vs Total Price by Driver')
    ax_grouped.legend()

    grouped_cursor = mplcursors.cursor([disposal_bars, price_bars], hover=True)
    grouped_cursor.connect("add", lambda sel: sel.annotation.set_text(f"${sel.target[1]:,.2f}"))

    total_gross_profit = pie_df['Total_Gross_Profit'].sum()
    wedges = ax_pie.pie(pie_df['Total_Gross_Profit'], startangle=90)[0]
    ax_pie.set_title('Gross Profit by Driver')
    legend_labels = [
        f"{driver} ({gross_profit / total_gross_profit * 100:.1f}%)"
        for driver, gross_profit in zip(pie_df['Driver'], pie_df['Total_Gross_Profit'])
    ]
    ax_pie.legend(
        wedges,
        legend_labels,
        title='Driver',
        loc='center left',
        bbox_to_anchor=(1, 0, 0.5, 1),
    )
    ax_pie.axis('equal')

    fig.tight_layout()
    plt.show()


def process_file(file_path):
    invoicing_df = pd.read_excel(file_path, engine="openpyxl", header=2, skipfooter=1)
    # print(invoicing_df.head())

    # Convert the 'Date' column to datetime format
    invoicing_df['Date'] = pd.to_datetime(invoicing_df['Date'])

    # Create a new column to have month and year
    invoicing_df['YearMonth'] = invoicing_df['Date'].dt.to_period('M')

    # Define the list of drivers to exclude
    excluded_drivers = ['Renee Castellan']

    # Filter out the excluded drivers
    filtered_invoicing_df = invoicing_df[~invoicing_df['Driver'].isin(excluded_drivers)]

    # Group by 'Driver' and 'YearMonth' and count the number of items
    item_counts = filtered_invoicing_df.groupby(['Driver', 
                                                'YearMonth']).size().reset_index(name='Item Count')
    # print("Item Counts:")
    # print(item_counts.head())

    # Group by 'Driver' and 'YearMonth' and sum the 'Gross Profit'
    gross_profit_sum = filtered_invoicing_df.groupby(['Driver', 
                                                    'YearMonth'])['Gross Profit'].sum().reset_index()
    # print("Gross Profit Sum:")
    # print(gross_profit_sum.head())

    # Count total number of items per driver
    total_items_per_driver = filtered_invoicing_df.groupby('Driver').size()

    # Calculate total unique days in the filtered data
    total_days = filtered_invoicing_df['Date'].dt.date.nunique()
    
    # Calculate daily average number of dumpster runs per driver
    daily_avg_per_driver = total_items_per_driver / total_days if total_days else 0

    print("\nTotal Number of Items per Driver:")
    print(total_items_per_driver)

    print("\nTotal Daily Average Number of Dumpster Runs per Driver:")
    print(round(daily_avg_per_driver))

    # Calculate the average values

    average_items_df = item_counts.groupby(['Driver', 'YearMonth']).mean().reset_index()
    # print("Average Items DataFrame:")
    # print(average_items_df.head())
    average_gp_df = gross_profit_sum.groupby(['Driver', 'YearMonth']).mean().reset_index()
    # print("Average Gross Profit DataFrame:")
    # print(average_gp_df.head())

    return item_counts, gross_profit_sum


def process_and_display(file_path):
    item_counts, gross_profit_sum = process_file(file_path)


def calculate_data():
    """Choose the report data source based on the user selection."""
    data_source = data_source_var.get()

    if data_source == "Sample Data":
        rows = get_sample_driver_stats()
        driver_df = pd.DataFrame(
            rows,
            columns=[
                "Driver",
                "Dumpster_Count",
                "Total_Disposal_Cost",
                "Total_Price",
                "Total_Gross_Profit",
                "Gross_Profit_Percent",
            ],
        )
        plot_driver_stats(driver_df)
        return

    if data_source == "SQL":
        start_date = start_date_entry.get().strip() or DEFAULT_START_DATE
        end_date = end_date_entry.get().strip() or DEFAULT_END_DATE
        rows = fetch_get_driver_totals(start_date, end_date)
        if not rows:
            return

        driver_df = pd.DataFrame(
            rows,
            columns=[
                "Driver",
                "Dumpster_Count",
                "Total_Disposal_Cost",
                "Total_Price",
                "Total_Gross_Profit",
                "Gross_Profit_Percent",
            ],
        )
        plot_driver_stats(driver_df)

    if data_source == "Excel":
        select_file()


def select_file():
    """
    Opens a file dialog for the user to select an Excel file (.xlsx or .xls).
    If a file is selected, closes the main window and processes the file.

    Returns:
        None
    """
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if file_path:
        if 'root' in globals():
            root.withdraw()
        process_and_display(file_path)


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
    if 'root' in globals():
        root.withdraw()  # Hide the main window
    process_and_display(file_path)


if __name__ == "__main__":
        root = tk.Tk()
        root.title("Driver Stats")
        root.config(width=450, height=250, padx=25, pady=25)

        data_source_label = tk.Label(root, text="Data Source:")
        data_source_label.grid(column=0, row=0, padx=5, pady=5, sticky="e")

        data_source_var = tk.StringVar(value="Sample Data")

        data_source_options = ttk.Combobox(
            root,
            width=20,
            state="readonly",
            textvariable=data_source_var,
            values=["SQL", "Excel", "Sample Data"],
        )
        data_source_options.grid(column=1, row=0, padx=5, pady=5)

        start_date_label = tk.Label(root, text="Start Date YYYY-MM-DD:")
        start_date_label.grid(column=0, row=1, padx=5, pady=5)
        start_date_entry = tk.Entry(root, width=20)
        start_date_entry.insert(0, DEFAULT_START_DATE)
        start_date_entry.grid(column=1, row=1, padx=5, pady=5)

        end_date_label = tk.Label(root, text="End Date YYYY-MM-DD:")
        end_date_label.grid(column=0, row=2, padx=5, pady=5)
        end_date_entry = tk.Entry(root, width=20)
        end_date_entry.insert(0, DEFAULT_END_DATE)
        end_date_entry.grid(column=1, row=2, padx=5, pady=5)

        calculate_button = ttk.Button(
            root,
            text="Calculate",
            command=calculate_data,
        )
        calculate_button.grid(column=1, row=3, padx=5, pady=5)

        root.mainloop()
