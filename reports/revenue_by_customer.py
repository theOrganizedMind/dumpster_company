import pandas as pd
from datetime import datetime
import os
import logging
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import tkinter as tk
from tkinter import filedialog, Label, Button, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD

from postgresql import fetch_all

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

GET_DATA_FROM_SQL_DATABASE = True # <-- Set to False to use excel file.
START_DATE = "2026-01-01" # <-- Change start and end date to filter results.
END_DATE = "2026-06-30"


def fetch_get_company_totals(start_date, end_date):
    """Fetch revenue by customer from PostgreSQL for the provided date range."""
    rows = fetch_all(
        "SELECT * "
        "FROM get_company_totals(%s, %s)"
        "ORDER BY total_price DESC;",
        (start_date, end_date),
    )

    if not rows:
        print("No projects found for the selected date range.")
        return []

    print(f"\nRevenue by Customer ({start_date} to {end_date})")
    print("-" * 130)
    print(f"{'Company':<35} {'Total Price':<50} {'Total Gross Profit':<20} {'Profit Percentage':>12}")
    print("-" * 130)

    for company, total_price, total_gross_profit, profit_percentage in rows:
        print(f"{company:<35} {float(total_price):<50,.2f} {float(total_gross_profit):<20,.2f} {float(profit_percentage):>11,.2f}")

    return rows


def select_file():
    """Open a file dialog for the user to select an Excel file."""
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if file_path:
        root.withdraw()
        process_file(file_path)

def handle_drop(event):
    """Handle drag-and-drop event for an Excel file."""
    file_path = event.data.strip('{}')
    root.withdraw()
    process_file(file_path)

def process_file(file_path):
    data = pd.read_excel(file_path, engine='openpyxl', header=2, skipfooter=1)
    data[['Price', 'Gross Profit']] = data[['Price', 'Gross Profit']].fillna(0.00)

    # Group the data by customer and calculate the total revenue and gross profit for each customer
    total_revenue_by_customer = data.groupby('Company').agg({'Price': 'sum', 'Gross Profit': 'sum'}).reset_index()

    # Sort the companies in descending order by price
    total_revenue_by_customer = total_revenue_by_customer.sort_values(by='Price', ascending=False)

    # Calculate the percent profit, handling division by zero
    total_revenue_by_customer['Percent Profit'] = total_revenue_by_customer.apply(
        lambda row: (row['Gross Profit'] / row['Price']) * 100 if row['Price'] != 0 else 0, axis=1)

    # Format the 'Price', 'Gross Profit', and 'Percent Profit' columns
    total_revenue_by_customer['Price'] = total_revenue_by_customer['Price'].apply(lambda x: f'{x:,.2f}')
    total_revenue_by_customer['Gross Profit'] = total_revenue_by_customer['Gross Profit'].apply(lambda x: f'{x:,.2f}')
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
    popup = tk.Toplevel()
    popup.title("Revenue by Customer")
    popup.geometry("700x500")
    text = tk.Text(popup, wrap="none", font=("Consolas", 11))
    text.pack(expand=True, fill="both", padx=10, pady=10)
    text.insert("end", f"{'Company':<35} {'Revenue':>20} {'Gross Profit':>20} {'Percent Profit':>20}\n")
    text.insert("end", "-"*100 + "\n")
    for _, row in df.iterrows():
        text.insert("end", f"{row['Company']:<35} {row['Price']:>20} {row['Gross Profit']:>20} {row['Percent Profit']:>15}\n")

    # Calculate totals
    total_price = df['Price'].str.replace(',', '').astype(float).sum()
    total_gross_profit = df['Gross Profit'].str.replace(',', '').astype(float).sum()
    average_percent_profit = df['Percent Profit'].str.replace('%', '').astype(float).mean()

    # Add totals to the end of the text box
    text.insert("end", "\n" + "-"*100 + "\n")
    text.insert("end", f"{'TOTALS':<35} {total_price:>20,.2f} {total_gross_profit:>22,.2f} {average_percent_profit:>15.2f}%\n")
    text.config(state="disabled")

if __name__ == "__main__":
    if GET_DATA_FROM_SQL_DATABASE:
        fetch_get_company_totals(START_DATE, END_DATE)
    else:
        # TkinterDnD GUI for file selection or drag-and-drop
        root = TkinterDnD.Tk()
        root.title("Revenue by Customer")
        root.geometry("600x500")

        instructions = (
            "Info:\n"
            "This script will read the excel file and calculate the total revenue, "
            "gross profit and percent profit for each customer.\n"
            "Steps:\n"
            "1.) Export the TDC Invoicing board to excel\n"
            "2.) Select the file using the 'Browse' button or drag and drop the file "
            "into the designated area.\n"
            "3.) The results will be displayed in a popup window and you will have "
            "the option to save the results to an Excel file.\n"
            "4.) You can also choose to view a pie chart of the top 10 highest revenue "
            "companies.\n"
        )

        instructions_label = Label(root, text=instructions, justify="left", 
                                font=("Times New Roman", 12), wraplength=480)
        instructions_label.pack(pady=10)

        Label(root, text="Select or Drag and Drop the Excel file for Revenue by Customer").pack(pady=10)
        drop_label = Label(root, text="Drag and drop file here", relief="ridge", width=40, height=3)
        drop_label.pack(pady=10)
        drop_label.drop_target_register(DND_FILES)
        drop_label.dnd_bind('<<Drop>>', handle_drop)
        Button(root, text="Browse", command=select_file).pack(pady=10)
        root.mainloop()
