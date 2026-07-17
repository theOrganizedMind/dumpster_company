import os
import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

# ============================================================================ #
# ===================================== INFO ================================= #
# ============================================================================ #
# - Download the project specific waste tickets from Invoicing board.
# - Run this program to rename the .jpg files starting from # 1. 
# - Attach and email to client. 
# ============================================================================ #
# ===================================== TODO ================================= #
# ============================================================================ #
# TODO: 
#
# ============================================================================ #

# Set to False to actually rename the files.
TEST_MODE: bool = False

downloads_folder = Path.home() / "Downloads"
today = datetime.date.today()
location = input("What is the job address? ")


def select_jpg_files():
    """Open a file dialog for the user to select .jpg files."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_paths = filedialog.askopenfilenames(
        title="Select waste ticket .jpg files",
        filetypes=[("JPEG files", "*.jpg")]
    )
    return [Path(fp) for fp in file_paths]

def rename_waste_tickets(test_mode=True):
    """
    Renames selected .jpg files to the format 'Waste Ticket 1.jpg', 'Waste Ticket 2.jpg', etc.
    If a file with the target name already exists, a numeric suffix is appended.
    """
    try:
        jpg_files_selected = select_jpg_files()
        if not jpg_files_selected:
            print("No files selected. Exiting.")
            return

        for idx, file in enumerate(jpg_files_selected, start=1):
            new_name = file.parent / f"{location} - Waste Ticket {idx}.jpg"
            try:
                if not new_name.exists():
                    if test_mode:
                        print(f"[TEST MODE] Would rename: {file} -> {new_name}")
                    else:
                        file.rename(new_name)
                        print(f"Renamed: {file} -> {new_name}")
                else:
                    # If file exists, append a unique suffix
                    suffix = 1
                    while True:
                        alt_name = file.parent / f"{location} - Waste Ticket {idx} ({suffix}).jpg"
                        if not alt_name.exists():
                            if test_mode:
                                print(f"[TEST MODE] Would rename: {file} -> {alt_name}")
                            else:
                                file.rename(alt_name)
                                print(f"Renamed: {file} -> {alt_name}")
                            break
                        suffix += 1
            except Exception as e:
                print(f"Error renaming {file}: {e}")
    except Exception as e:
        print(f"Error in rename_waste_tickets: {e}")

rename_waste_tickets(test_mode=TEST_MODE)
