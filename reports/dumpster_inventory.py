import pandas as pd
from datetime import datetime
import os
import tkinter as tk
from tkinter import filedialog, Label, Button, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import re
from idlelib.tooltip import Hovertip
import logging

from normalize_address import normalize_address


# =========================================================================== #
# ================================== INFO =================================== #
# =========================================================================== #
# This program loops through the invoicing excel file and adds the 'Initial Drop'
# address to unique locations and removes the address if the description is 
# 'Dump & Remove'. It appends the unique location to the specifed txt file.
# Typically run this script 28 days after every quarter.  
# Steps:
# 1.) Filter invoicing board by quarter and description == 'Initial Drop' and 
# 'Dump & Remove'.
# 2.) Export to excel.
# 3.) Save and select file.
# 4.) Run this script to append the unique locations to a text file.
# 5.) Search for dumpsters added to the text file. 
# =========================================================================== #
# ================================== TODO =================================== #
# =========================================================================== #
# TODO:
# =========================================================================== #

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

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

        # If txt_files/remaining_dumpster_locations.txt exists, append to it.
        # Else, save as new file in Downloads (do NOT create txt_files dir).
        if os.path.exists(output_file):
            save_path = output_file
            # Ensure txt_files exists (legacy support)
            # os.makedirs(os.path.dirname(output_file), exist_ok=True)
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
    
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


if __name__ == "__main__":
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
        "Steps:\n"
        "1.) Filter invoicing board by quarter and description == 'Initial Drop' and \n"
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
