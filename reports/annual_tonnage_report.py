import pandas as pd
import tkinter as tk
from tkinter import filedialog, Label, Button, Scrollbar, Frame
from tkinter import VERTICAL, BOTH, LEFT, RIGHT, Y
from tkinterdnd2 import DND_FILES, TkinterDnD

from postgresql import fetch_all

# =========================================================================== #
# =============================== INFO ====================================== #
# =========================================================================== #
# 
# =========================================================================== #
# =============================== TODO ====================================== #
# =========================================================================== #
#
# =========================================================================== #

GET_DATA_FROM_SQL_DATABASE = True # <-- Set to False to use excel file.
START_DATE = "2026-01-01" # <-- Change start and end date to filter results.
END_DATE = "2026-06-30"

def fetch_annual_tonnage_report(start_date, end_date):
    """Fetch annual tonnage report from PostgreSQL for the provided date range."""
    rows = fetch_all(
        "SELECT * FROM annual_tonnage_report(%s, %s);",
        (start_date, end_date),
    )

    if not rows:
        print("No projects found for the selected date range.")
        return []

    print(f"\nAnnual Tonnage Report ({start_date} to {end_date})")
    print("-" * 90)
    print(f"{'Disposal':<35} {'City':<40} {'Total Tons':<10}")
    print("-" * 90)

    for disposal, city, total_tons in rows:
        print(f"{disposal:<35} {city:<40} {float(total_tons):<10,.2f}")

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
    """Process the Excel file and display the annual tonnage report in a popup window."""
    data = pd.read_excel(file_path, engine='openpyxl', header=2, skipfooter=1)
    data['Tons'] = data['Tons'].fillna(0)
    grouped_data = data.groupby('Disposal')['Tons'].sum()
    sorted_disposal_locations = sorted(grouped_data.items(), key=lambda x: x[1], reverse=True)

    # Show results in a popup window with a Text widget
    popup = tk.Toplevel()
    popup.title("Annual Tonnage Report")
    popup.geometry("600x400")
    frame = Frame(popup)
    frame.pack(fill=BOTH, expand=True)
    scrollbar = Scrollbar(frame, orient=VERTICAL)
    text = tk.Text(frame, yscrollcommand=scrollbar.set, width=60, height=20, font=("Consolas", 11))
    text.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.config(command=text.yview)
    scrollbar.pack(side=RIGHT, fill=Y)

    # Add header
    text.insert("end", f"{'Disposal Location':<35} {'Total Tons':>15}\n")
    text.insert("end", "-"*52 + "\n")
    for location, tons in sorted_disposal_locations:
        text.insert("end", f"{location:<35} {tons:>15,.2f}\n")
    text.config(state="disabled")

if __name__ == "__main__":
    if GET_DATA_FROM_SQL_DATABASE:
        fetch_annual_tonnage_report(START_DATE, END_DATE)
    else:
        # TkinterDnD GUI for file selection or drag-and-drop
        root = TkinterDnD.Tk()
        root.title("Annual Tonnage Report")
        root.geometry("600x400")

        Label(root, text="Select or Drag and Drop the Excel file for Annual Tonnage Report").pack(pady=10)
        drop_label = Label(root, text="Drag and drop file here", relief="ridge", width=40, height=3)
        drop_label.pack(pady=10)
        drop_label.drop_target_register(DND_FILES)
        drop_label.dnd_bind('<<Drop>>', handle_drop)
        Button(root, text="Browse", command=select_file).pack(pady=10)
        root.mainloop()
