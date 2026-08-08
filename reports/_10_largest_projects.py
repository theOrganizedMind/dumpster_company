import pandas as pd
import tkinter as tk
from tkinter import filedialog, Label, Button
from tkinterdnd2 import DND_FILES, TkinterDnD

from postgresql import fetch_all
from normalize_address import normalize_address

# =========================================================================== #
# ================================ INFO ===================================== #
# =========================================================================== #
# 
# =========================================================================== #
# ================================ TODO ===================================== #
# =========================================================================== #
#
# =========================================================================== #

GET_DATA_FROM_SQL_DATABASE = True # <-- Set to False to use excel file.
START_DATE = "2026-01-01" # <-- Change start and end date to filter results.
END_DATE = "2026-06-30"

def fetch_10_largest_projects(start_date, end_date):
    """Fetch 10 largest projects from PostgreSQL for the provided date range."""
    rows = fetch_all(
        "SELECT * FROM _10_largest_projects(%s, %s);",
        (start_date, end_date),
    )

    if not rows:
        print("No projects found for the selected date range.")
        return []

    print(f"\n10 Largest Projects ({start_date} to {end_date})")
    print("-" * 110)
    print(f"{'Company':<35} {'Street':<40} {'City':<20} {'Total Price':>12}")
    print("-" * 110)

    for company, street, city, total_price in rows:
        print(f"{company:<35} {street:<40} {city:<20} ${float(total_price):>11,.2f}")

    return rows

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
        process_file(file_path)

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
    process_file(file_path)

def process_file(file_path):
    """
    Processes the selected or dropped Excel file to find the 10 largest projects.
    Aggregates the total price by company and location, then displays the top 10
    projects in a popup window.

    Args:
        file_path (str): Path to the Excel file.

    Returns:
        None
    """
    data = pd.read_excel(file_path, engine="openpyxl", header=2, skipfooter=1)
    data['Price'] = data['Price'].fillna(0)
    company_location_price = {}
    for index, row in data.iterrows():
        # Normalize the location before using it as a key.
        normalized_location = normalize_address(str(row['Location']))
        key = (row['Company'], normalized_location)
        if key in company_location_price:
            company_location_price[key] += row['Price']
        else:
            company_location_price[key] = row['Price']
    df = pd.DataFrame(company_location_price.items(), columns=['Company_Location', 'Total_Price'])
    df[['Company', 'Location']] = pd.DataFrame(df['Company_Location'].tolist(), index=df.index)
    df.drop(columns=['Company_Location'], inplace=True)
    largest_projects = df.nlargest(10, 'Total_Price')
    show_popup(largest_projects)

def show_popup(df):
    """
    Displays the 10 largest projects in a popup window using a Tkinter Text widget.

    Args:
        df (DataFrame): DataFrame containing the top 10 projects with columns
                        'Company', 'Location', and 'Total_Price'.

    Returns:
        None
    """
    popup = tk.Toplevel()
    popup.title("10 Largest Projects")
    popup.geometry("800x300")
    text = tk.Text(popup, wrap="none", font=("Consolas", 11))
    text.pack(expand=True, fill="both", padx=10, pady=10)
    # Add column headers
    # :<25 left align company name in 25 spaces.
    # :<50 left align location in 50 spaces.
    # :>15 right align total price in 15 spaces.
    text.insert("end", f"{'Company':<25} {'Location':<50} {'Total Price':>15}\n")
    text.insert("end", "-"*100 + "\n")
    # Add each row
    for _, row in df.iterrows():
        text.insert("end", f"{row['Company']:<25} {row['Location']:<50} ${row['Total_Price']:>12,.2f}\n")
    text.config(state="disabled")


if __name__ == "__main__":
    if GET_DATA_FROM_SQL_DATABASE:
        fetch_10_largest_projects(START_DATE, END_DATE)
    else:
    # Tkinter GUI for file selection or drag-and-drop
        root = TkinterDnD.Tk()
        root.title("10 Largest Projects")
        root.geometry("600x400")

        instructions = (
            "Info:\n"
            "This program should be ran once a year when the pollution liability insurance "
            "renews.\n"
            "Steps:\n"
            "1.) Filter the invoicing board for the prior year.\n"
            "2.) Select or drag and drop the Excel file with project data.\n"
            "3.) The program will display the 10 largest projects with company name, "
            "location, and total price.\n"
            "4.) Optionally, you can modify the code to save the results to a file.\n"
        )

        instructions_label = Label(root, text=instructions, justify="left", 
                                font=("Times New Roman", 12), wraplength=480)
        instructions_label.pack(pady=10)

        Label(root, text="Select or Drag and Drop the Excel file for 10 Largest Projects").pack(pady=10)
        drop_label = Label(root, text="Drag and drop file here", relief="ridge", width=40, height=3)
        drop_label.pack(pady=10)
        drop_label.drop_target_register(DND_FILES)
        drop_label.dnd_bind('<<Drop>>', handle_drop)
        Button(root, text="Browse", command=select_file).pack(pady=10)
        root.mainloop()
