import pandas as pd
from datetime import datetime
import os
import tkinter as tk
from tkinter import filedialog, Label, Button, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from idlelib.tooltip import Hovertip
import logging

from postgresql import get_db_connection
from normalize_address import normalize_address


# =========================================================================== #
# ================================== INFO =================================== #
# =========================================================================== #
# 
# =========================================================================== #
# ================================== TODO =================================== #
# =========================================================================== #
# TODO: 
# =========================================================================== #

GET_DATA_FROM_SQL_DATABASE: bool = False # <-- Set to True to use SQL Database.
GET_DATA_FROM_SAMPLE_DATA: bool = True

# Fictitious data used when GET_DATA_FROM_SAMPLE_DATA is True (no SQL source required).
SAMPLE_ACTIVE_DUMPSTERS = [
    ("Bluegrass Hauling Co.", "142 Maplewood Ave", "Springvale", "20 Yard", 4),
    ("Northgate Builders LLC", "27 Foxridge Ln", "Millhaven", "30 Yard", 3),
    ("Crestview Excavation", "1203 Sunset Ridge Blvd", "Millhaven", "20 Yard", 2),
    ("Ironoak Contracting", "33 Prairie View Rd", "Ashford", "15 Yard", 5),
    ("Summit Site Services", "14 Redstone Ave", "Grantfield", "30 Yard", 1),
]

def get_sample_active_dumpsters():
    """Return a fictitious sample dataset for demo purposes when no SQL source is available."""
    return list(SAMPLE_ACTIVE_DUMPSTERS)


def fetch_get_active_dumpsters():
    """Fetch active dumpster inventory from PostgreSQL."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM get_active_dumpsters();",
                )
            rows = cur.fetchall()

    if not rows:
        print("No projects found for the selected date range.")
        return []

    company_width = max(len("Company"), max(len(company) for company, _, _, _, _ in rows)) + 3
    street_width = max(len("Street"), max(len(street) for _, street, _, _, _ in rows)) + 3
    city_width = max(len("City"), max(len(city) for _, _, city, _, _ in rows)) + 3
    size_width = max(len("Size"), max(len(size) for _, _, _, size, _ in rows)) + 3
    active_count_width = 20
    divider_width = company_width + street_width + city_width + size_width + active_count_width
    row_format = (
        f"{{company:<{company_width}}}{{street:<{street_width}}}"
        f"{{city:<{city_width}}}{{size:<{size_width}}}{{active_count:>{active_count_width}}}"
    )

    print(f"\nActive Dumpster Locations:")
    print("-" * divider_width)
    print(row_format.format(company="Company", street="Street", city="City", 
                            size="Size", active_count="Active Count"))
    print("-" * divider_width)

    for company, street, city, size, active_count in rows:
        print(row_format.format(company=company, street=street, city=city, size=size,
                                active_count=int(active_count)))

    return rows

def create_tooltip(widget, text):
    """Creates tooltips for the tkinter widgets"""
    Hovertip(widget, text, hover_delay=500)

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
    """
    Processes the selected Excel file to identify unique dumpster locations.

    For each row, normalizes the address in the 'Location' column and:
    - Adds the address to the unique locations if the 'Description' is 'Initial Drop'.
    - Removes the address from unique locations if the 'Description' is 'Dump & Remove'.

    The resulting unique locations are written to a text file:
    - If 'txt_files/remaining_dumpster_locations.txt' exists, appends results to it.
    - Otherwise, saves results as a new file in the user's Downloads folder.

    Args:
        file_path (str): Path to the selected Excel file.

    Returns:
        None. Displays a messagebox when complete.
    """
    try:

        # Log the date when the program is run
        logging.info(f"Program run date: {datetime.now().strftime("%Y-%m-%d")}")
        
        df = pd.read_excel(file_path, engine='openpyxl', header=2, skipfooter=1)
        if "Description" not in df.columns or "Location" not in df.columns:
            messagebox.showerror("Error", "Excel file must contain 'Description' and 'Location', columns.")
            return
    
        unique_locations = {}
        for index, row in df.iterrows():
            desc = str(row["Description"]).strip().lower()
            loc = str(row["Location"]).strip().lower()
            norm_loc = normalize_address(loc)
            if desc == "initial drop":
                unique_locations[norm_loc] = True
            elif desc == "dump & remove":
                unique_locations.pop(norm_loc, None)

        output_file = "txt_files/remaining_dumpster_locations.txt"
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        downloads_file = os.path.join(downloads_folder, "remaining_dumpster_locations.txt")

        if os.path.exists(output_file):
            save_path = output_file
            mode = "a"
        else:
            save_path = downloads_file
            mode = "w"

        existing = set()
        if os.path.exists(save_path):
            with open(save_path, "r") as f:
                existing = set(line.strip() for line in f)

        new_locations = [loc for loc in unique_locations if loc not in existing]
        with open(save_path, mode) as file:
            for loc in new_locations:
                file.write(loc + "\n")

        messagebox.showinfo("Success", f"{len(new_locations)} new locations saved to {save_path}")
    
    except Exception:
        logging.exception("Error processing dumpster inventory file.")
        messagebox.showerror(
            "Error",
            "The file could not be processed. Verify the file format and required columns, then try again.",
        )


if __name__ == "__main__":
    if GET_DATA_FROM_SQL_DATABASE:
        rows = fetch_get_active_dumpsters()
        if rows:
            active_dumpsters_df = pd.DataFrame(
                rows, columns=["Company", "Street", "City", "Size", "Active_Count"]
            )
            root = tk.Tk()
            root.withdraw()
            if messagebox.askyesno("Save Results", "Would you like to save the results to an Excel file?"):
                todays_date = datetime.now().strftime("%m%d%Y")
                downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
                save_path = os.path.join(downloads_folder, f"active_dumpster_locations_({todays_date}).xlsx")
                active_dumpsters_df.to_excel(save_path, index=False, freeze_panes=(1, 1))
                messagebox.showinfo("Success", f"File saved to {save_path}")
            else:
                logging.info("Results not saved to an Excel file.")
            root.destroy()
    elif GET_DATA_FROM_SAMPLE_DATA:
        rows = get_sample_active_dumpsters()
        active_dumpsters_df = pd.DataFrame(
            rows, columns=["Company", "Street", "City", "Size", "Active_Count"]
        )
        root = tk.Tk()
        root.withdraw()
        if messagebox.askyesno("Save Results", "Would you like to save the results to an Excel file?"):
            todays_date = datetime.now().strftime("%m%d%Y")
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            save_path = os.path.join(downloads_folder, f"active_dumpster_locations_({todays_date}).xlsx")
            active_dumpsters_df.to_excel(save_path, index=False, freeze_panes=(1, 1))
            messagebox.showinfo("Success", f"File saved to {save_path}")
        else:
            logging.info("Results not saved to an Excel file.")
        root.destroy()
    else:
        root = TkinterDnD.Tk()
        root.title("Dumpster Inventory")
        root.geometry("500x200")
        root.config(padx=20, pady=20)

        select_filel_label = Label(root, text="Select or Drag and Drop the Excel file for Dumpster Inventory (Tooltip)")
        select_filel_label.pack(pady=10)
        create_tooltip(select_filel_label, "Info:\n"  
            "This program loops through the invoicing excel file and adds the 'Initial Drop' \n"
            "address to unique locations and removes the address if the description is \n"
            "'Dump & Remove'. It appends the unique location to the specifed txt file. \n"
            "Typically run this script 28 days after every quarter.\n"
            "Steps:\n"
            "1.) Filter board by quarter and description == 'Initial Drop' and \n"
            "'Dump & Remove'.\n"
            "2.) Export to excel and select file.\n"
            "3.) Run this script to append the unique locations to a text file.\n"
            "4.) Search for dumpsters added to the text file.")
        drop_label = Label(root, text="Drag and drop file here", relief="ridge", width=40, height=3)
        drop_label.pack(pady=10)
        drop_label.drop_target_register(DND_FILES)
        drop_label.dnd_bind('<<Drop>>', handle_drop)
        Button(root, text="Browse", command=select_file).pack(pady=10)
        root.mainloop()
