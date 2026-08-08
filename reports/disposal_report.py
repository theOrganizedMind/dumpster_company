from datetime import datetime
import os, glob
import pandas as pd
import logging
import tkinter as tk
from tkinter import filedialog, Label, Button, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import re

from normalize_address import normalize_address


# =========================================================================== #
# ================================== INFO =================================== #
# =========================================================================== #
# 1.) Filter and Export disposal by job address from the TDC Invoicing board.
# 2.) Drag and drop the file into the GUI or select it using a file dialog.
# 3.) The program will process the file, clean it up, and save it back to the
#     Downloads folder with a modified name based on the location and today's date.
# =========================================================================== #
# ================================== TODO =================================== #
# =========================================================================== #
# 
# =========================================================================== #


# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

COLUMNS_TO_EXCLUDE = [
    'Files', 'Disposal Cost', 'Gross Profit',
    ]

todays_date = datetime.now().strftime("%m%d%Y")
downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")

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
    try:
        data = pd.read_excel(file_path, engine='openpyxl', header=2, skipfooter=1)
        data = data.rename(columns={"Name": "Invoice #"})
        data = data.drop(columns=[col for col in COLUMNS_TO_EXCLUDE if col in data.columns])

        data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
        data['Price'] = data['Price'].fillna(0.00)
        data['Price'] = data['Price'].replace(r'[\$,]', '', regex=True).astype(float)
        if 'Phone' in data.columns:
            data['Phone'] = data['Phone'].astype(str)
        if 'Tons' in data.columns:
            data['Tons'] = data['Tons'].astype(float)

        if 'Location' in data.columns:
            data['Location'] = data['Location'].apply(normalize_address)
            unique_locations = data['Location'].unique()
            if len(unique_locations) == 1:
                location_value = unique_locations[0]
            else:
                logging.warning("Multiple unique locations found.")
                location_value = "Multiple_Locations"
        else:
            logging.error("Location column not found in the data.")
            location_value = "Unknown_Location"

        # Ask user where to save the file, but suggest the Downloads folder and default name
        default_filename = f"Invoicing_{location_value}_({todays_date}).xlsx"
        save_path = filedialog.asksaveasfilename(
            initialdir=downloads_folder,
            initialfile=default_filename,
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if save_path:
            data.to_excel(save_path, index=False, freeze_panes=(1, 1))
            messagebox.showinfo("Success", f"File saved to {save_path}")
            logging.info(f"File saved to {save_path}")
        else:
            messagebox.showinfo("Cancelled", "Save operation cancelled.")
    except Exception:
        logging.exception("Error processing disposal report file.")
        messagebox.showerror(
            "Error",
            "The file could not be processed. Verify the file format and required columns, then try again.",
        )


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    root.title("Disposal Report")
    root.geometry("600x400")

    instructions = (
        "Info:\n"
        "This program will process the file, clean it up, and save it back to the "
        "Downloads folder with a modified name based on the location and today's date.\n"
        "Steps:\n"
        "1.) Filter and Export disposal by job address from Invoicing board.\n"
        "2.) Drag and drop the file into the GUI or select it using a file dialog.\n"
    )

    instructions_label = Label(root, text=instructions, justify="left", 
                            font=("Times New Roman", 12), wraplength=480)
    instructions_label.pack(pady=10)

    Label(root, text="Select or Drag and Drop the Excel file for Disposal Report").pack(pady=10)
    drop_label = Label(root, text="Drag and drop file here", relief="ridge", width=40, height=3)
    drop_label.pack(pady=10)
    drop_label.drop_target_register(DND_FILES)
    drop_label.dnd_bind('<<Drop>>', handle_drop)
    Button(root, text="Browse", command=select_file).pack(pady=10)
    root.mainloop()
