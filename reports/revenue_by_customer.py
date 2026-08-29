import pandas as pd
from datetime import datetime
import os
import logging
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from postgresql import get_db_connection

# =========================================================================== #
# ================================== INFO =================================== #
# =========================================================================== #
# 
# =========================================================================== #
# ================================== TODO =================================== #
# =========================================================================== #
# TODO:
# =========================================================================== #

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


DEFAULT_START_DATE = "2026-01-01"
DEFAULT_END_DATE = "2026-06-30"

# Fictitious data used when "Sample Data" is selected (no SQL/Excel source required).
SAMPLE_REVENUE = [
    ("Bluegrass Hauling Co.", 491020.00, 28.75, 147306.00, 30.00),
    ("Northgate Builders LLC", 362540.00, 21.22, 98285.80, 27.11),
    ("Crestview Excavation", 275890.00, 16.15, 71731.40, 26.00),
    ("Ironoak Contracting", 210430.00, 12.32, 46294.60, 22.00),
    ("Summit Site Services", 178650.00, 10.46, 33943.50, 19.00),
    ("Redstone Demolition", 138470.00, 8.10, 22155.20, 16.00),
    ("Foxridge Site Development", 51000.00, 2.98, 6120.00, 12.00),
]

def get_sample_revenue():
    """Return a fictitious sample dataset for demo purposes when no SQL/Excel source is available."""
    return list(SAMPLE_REVENUE)


def fetch_get_company_totals(start_date, end_date):
    """Fetch revenue by customer from PostgreSQL for the provided date range."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM get_company_totals(%s, %s)
                ORDER BY revenue DESC;
                """,
                (start_date, end_date),
            )
            rows = cur.fetchall()

    if not rows:
        print("No projects found for the selected date range.")
        return []

    NUMERIC_COL_WIDTH = 20
    company_width = max(len("Company"), max(len(company) for company, _, _, _, _ in rows)) + 3
    total_revenue_width = NUMERIC_COL_WIDTH
    revenue_pct_width = NUMERIC_COL_WIDTH
    total_gross_profit_width = NUMERIC_COL_WIDTH
    profit_pct_width = NUMERIC_COL_WIDTH
    divider_width = (company_width + total_revenue_width + revenue_pct_width
                    + total_gross_profit_width + profit_pct_width)
    row_format = (
        f"{{company:<{company_width}}}{{revenue:>{total_revenue_width}}}"
        f"{{revenue_pct:>{revenue_pct_width}}}{{total_gross_profit:>{total_gross_profit_width}}}"
        f"{{profit_pct:>{profit_pct_width}}}"
    )

    print(f"\nRevenue by Customer ({start_date} to {end_date})")
    print("-" * divider_width)
    print(row_format.format(company="Company",
                            revenue="Total Revenue",
                            revenue_pct="Revenue Percent",
                            total_gross_profit="Total Gross Profit",
                            profit_pct="Profit Percentage"))
    print("-" * divider_width)

    for company, revenue, revenue_pct, total_gross_profit, profit_percentage in rows:
        print(row_format.format(company=company,
                                revenue=f"${float(revenue):,.2f}",
                                revenue_pct=f"{float(revenue_pct):,.2f}%",
                                total_gross_profit=f"${float(total_gross_profit):,.2f}",
                                profit_pct=f"{float(profit_percentage):,.2f}%"))

    return rows


def calculate_data():
    """Choose the revenue data source based on the GUI selection."""
    data_source = data_source_var.get()

    if data_source == "Sample Data":
        rows = get_sample_revenue()
        sample_df = pd.DataFrame(
            rows,
            columns=["Company", "Price", "Revenue Percent", "Gross Profit", "Profit Percentage"],
        )
        sample_df["Revenue %"] = sample_df["Revenue Percent"].map(lambda x: f"{float(x):.2f}%")
        sample_df["Price"] = sample_df["Price"].map(lambda x: f"{float(x):,.2f}")
        sample_df["Gross Profit"] = sample_df["Gross Profit"].map(lambda x: f"{float(x):,.2f}")
        sample_df["Percent Profit"] = sample_df["Profit Percentage"].map(lambda x: f"{float(x):.2f}%")
        display_df = sample_df[["Company", "Price", "Revenue %", "Gross Profit", "Percent Profit"]]
        show_popup(display_df)
        return

    if data_source == "SQL":
        start_date = start_date_entry.get().strip() or DEFAULT_START_DATE
        end_date = end_date_entry.get().strip() or DEFAULT_END_DATE
        rows = fetch_get_company_totals(start_date, end_date)
        if not rows:
            return

        sql_df = pd.DataFrame(
            rows,
            columns=["Company", "Price", "Revenue Percent", "Gross Profit", "Profit Percentage"],
        )
        sql_df["Revenue %"] = sql_df["Revenue Percent"].map(lambda x: f"{float(x):.2f}%")
        sql_df["Price"] = sql_df["Price"].map(lambda x: f"{float(x):,.2f}")
        sql_df["Gross Profit"] = sql_df["Gross Profit"].map(lambda x: f"{float(x):,.2f}")
        sql_df["Percent Profit"] = sql_df["Profit Percentage"].map(lambda x: f"{float(x):.2f}%")
        display_df = sql_df[["Company", "Price", "Revenue %", "Gross Profit", "Percent Profit"]]
        show_popup(display_df)

        if messagebox.askyesno("Save Results", "Would you like to save the results to an Excel file?"):
            todays_date = datetime.now().strftime("%m%d%Y")
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            save_path = os.path.join(downloads_folder, f"revenue_by_customer_({todays_date}).xlsx")
            display_df.to_excel(save_path, index=False, freeze_panes=(1, 1))
            messagebox.showinfo("Success", f"File saved to {save_path}")
        else:
            logging.info("Results not saved to an Excel file.")
        return

    if data_source == "Excel":
        select_file()


def select_file():
    """Open a file dialog for the user to select an Excel file."""
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if file_path:
        if 'root' in globals():
            root.withdraw()
        process_file(file_path)


def handle_drop(event):
    """Handle drag-and-drop event for an Excel file."""
    file_path = event.data.strip('{}')
    if 'root' in globals():
        root.withdraw()
    process_file(file_path)

def process_file(file_path):
    data = pd.read_excel(file_path, engine='openpyxl', header=2, skipfooter=1)
    data[['Price', 'Gross Profit']] = data[['Price', 'Gross Profit']].fillna(0.00)

    # Group the data by customer and calculate the total revenue and gross profit for each customer
    total_revenue_by_customer = data.groupby('Company').agg({'Price': 'sum', 'Gross Profit': 'sum'}).reset_index()

    # Sort the companies in descending order by price
    total_revenue_by_customer = total_revenue_by_customer.sort_values(by='Price', ascending=False)

    total_revenue = total_revenue_by_customer['Price'].sum()

    # Calculate the revenue percentage and profit percentage, handling division by zero
    total_revenue_by_customer['Revenue %'] = total_revenue_by_customer.apply(
        lambda row: (row['Price'] / total_revenue) * 100 if total_revenue else 0, axis=1)
    total_revenue_by_customer['Percent Profit'] = total_revenue_by_customer.apply(
        lambda row: (row['Gross Profit'] / row['Price']) * 100 if row['Price'] != 0 else 0, axis=1)

    # Format the 'Price', 'Gross Profit', and 'Percent Profit' columns
    total_revenue_by_customer['Price'] = total_revenue_by_customer['Price'].apply(lambda x: f'{x:,.2f}')
    total_revenue_by_customer['Gross Profit'] = total_revenue_by_customer['Gross Profit'].apply(lambda x: f'{x:,.2f}')
    total_revenue_by_customer['Revenue %'] = total_revenue_by_customer['Revenue %'].apply(lambda x: f'{x:.2f}%')
    total_revenue_by_customer['Percent Profit'] = total_revenue_by_customer['Percent Profit'].apply(lambda x: f'{x:.2f}%')

    # Show results in a popup window
    show_popup(total_revenue_by_customer)

    # Ask user if they want to save results
    todays_date = datetime.now().strftime("%m%d%Y")
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    default_filename = f"Total_Revenue_By_Customer_({todays_date}).xlsx"
    save_path = filedialog.asksaveasfilename(
        initialdir=downloads_folder,
        initialfile=default_filename,
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx *.xls")]
        )
    if save_path:
        total_revenue_by_customer.to_excel(save_path, index=False, freeze_panes=(1, 1))
        messagebox.showinfo("Success", f"File saved to {save_path}")
    else:
        logging.info("Results not saved to an Excel file.")

    # Optionally, show a chart of the results
    if messagebox.askyesno("Show Chart", "Would you like to see a chart of the results?"):
        # Select the top 10 highest revenue companies
        top_10_revenue = total_revenue_by_customer.head(10).copy()
        top_10_revenue.loc[:, 'Price'] = top_10_revenue['Price'].str.replace(',', '').astype(float)
        # Format the 'Price' column for the table
        top_10_revenue['Price'] = top_10_revenue['Price'].apply(lambda x: f'{x:,.2f}')
        # Create a subplot with 2 rows and 1 column
        fig = make_subplots(
            rows=2, cols=1,
            specs=[[{"type": "pie"}], [{"type": "table"}]],
            vertical_spacing=0.3,
            row_heights=[0.5, 0.5]
        )
        # Add the pie chart to the first row
        fig.add_trace(
            go.Pie(labels=top_10_revenue['Company'],
                   values=top_10_revenue['Price'].str.replace(',', '').astype(float),
                   name="Revenue"),
            row=1, col=1
        )
        # Add the table to the second row
        fig.add_trace(
            go.Table(
                header=dict(values=["Company", "Revenue", "Gross Profit", "Percent Profit"],
                            fill_color='paleturquoise',
                            align='left'),
                cells=dict(values=[top_10_revenue['Company'], top_10_revenue['Price'],
                                   top_10_revenue['Gross Profit'],
                                   top_10_revenue['Percent Profit']],
                           fill_color='lavender',
                           align='left')
            ),
            row=2, col=1
        )
        fig.update_layout(
            title_text='Top 10 Highest Revenue Companies',
            height=1000
        )
        fig.show()
    else:
        logging.info("Chart not displayed.")

def show_popup(df):
    """Display the results in a popup window."""
    display_df = df.copy()

    if 'Revenue %' not in display_df.columns:
        if 'Revenue Percent' in display_df.columns:
            display_df['Revenue %'] = display_df['Revenue Percent']
        elif 'Profit Percentage' in display_df.columns:
            display_df['Revenue %'] = display_df['Profit Percentage']
        else:
            display_df['Revenue %'] = 0

    if 'Percent Profit' not in display_df.columns:
        if 'Profit Percentage' in display_df.columns:
            display_df['Percent Profit'] = display_df['Profit Percentage']
        else:
            display_df['Percent Profit'] = 0

    company_width = max(len("Company"), max(len(str(c)) for c in display_df['Company'])) + 3
    price_width = max(len("Revenue"), max(len(str(p)) for p in display_df['Price'])) + 3
    revenue_pct_width = max(len("Revenue %"), max(len(str(p)) for p in display_df['Revenue %'])) + 3
    gross_profit_width = max(len("Gross Profit"), max(len(str(p)) for p in display_df['Gross Profit'])) + 3
    percent_profit_width = max(len("Percent Profit"), max(len(str(p)) for p in display_df['Percent Profit'])) + 3
    divider_width = company_width + price_width + revenue_pct_width + gross_profit_width + percent_profit_width
    row_format = (
        f"{{company:<{company_width}}}{{price:>{price_width}}}"
        f"{{revenue_pct:>{revenue_pct_width}}}{{gross_profit:>{gross_profit_width}}}"
        f"{{percent_profit:>{percent_profit_width}}}"
    )

    popup = tk.Toplevel()
    popup.title("Revenue by Customer")
    popup.geometry("900x500")
    text = tk.Text(popup, wrap="none", font=("Consolas", 11))
    text.pack(expand=True, fill="both", padx=10, pady=10)
    text.insert("end", row_format.format(company="Company", price="Revenue", revenue_pct="Revenue %",
                                         gross_profit="Gross Profit", percent_profit="Percent Profit") + "\n")
    text.insert("end", "-" * divider_width + "\n")
    for _, row in display_df.iterrows():
        revenue_pct = row.get('Revenue %', 0)
        percent_profit = row.get('Percent Profit', 0)
        text.insert(
            "end",
            row_format.format(company=row['Company'], price=row['Price'], revenue_pct=str(revenue_pct),
                              gross_profit=row['Gross Profit'], percent_profit=str(percent_profit)) + "\n",
        )

    # Calculate totals
    total_price = display_df['Price'].astype(str).str.replace(',', '').astype(float).sum()
    total_gross_profit = display_df['Gross Profit'].astype(str).str.replace(',', '').astype(float).sum()
    revenue_pct_values = pd.to_numeric(
        display_df['Revenue %'].astype(str).str.replace('%', ''), errors='coerce'
    )
    average_percent_profit = pd.to_numeric(
        display_df['Percent Profit'].astype(str).str.replace('%', ''), errors='coerce'
    ).mean()

    # Add totals to the end of the text box
    text.insert("end", "\n" + "-" * divider_width + "\n")
    text.insert(
        "end",
        row_format.format(company="TOTALS", price=f"{total_price:,.2f}",
                          revenue_pct=f"{revenue_pct_values.mean():.2f}%",
                          gross_profit=f"{total_gross_profit:,.2f}",
                          percent_profit=f"{average_percent_profit:.2f}%") + "\n",
    )
    text.config(state="disabled")

if __name__ == "__main__":
        root = tk.Tk()
        root.title("Revenue by Customer")
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
