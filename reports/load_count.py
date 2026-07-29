import pandas as pd
import tkinter as tk
from tkinter import filedialog, Label, Button
from tkinterdnd2 import DND_FILES, TkinterDnD

from normalize_address import normalize_address

# =========================================================================== #
# ================================ INFO ===================================== #
# =========================================================================== #
# - Counts the number of dumpsters by 'Location', 'Type' and 'Date' and prints
#   the results to the console.
# - Excludes 'Initial Drop' and 'Dead Haul'.
# =========================================================================== #
# ================================ TODO ===================================== #
# =========================================================================== #
# 
# =========================================================================== #


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
    Reads the Excel file, normalizes locations, counts items by day and type,
    and prints the results grouped by location and date.
    Excludes rows where 'Description' is 'Initial Drop' or 'Dead Haul'.
    """
    df = pd.read_excel(file_path, engine="openpyxl", header=2, skipfooter=1)

    # Normalize the location column
    if 'Location' not in df.columns or 'Date' not in df.columns or 'Type' not in df.columns or 'Description' not in df.columns:
        print("Error: Excel file must contain 'Location', 'Date', 'Type', and 'Description' columns.")
        return
    
    # Exclude rows with 'Initial Drop' or 'Dead Haul' in Description
    # The tilde ~ operator negates the boolean result, so it selects rows not matching those descriptions.
    df = df[~df['Description'].str.strip().str.lower().isin(['initial drop', 'dead haul'])]

    df['Location'] = df['Location'].apply(normalize_address)
    df['Date'] = pd.to_datetime(df['Date']).dt.date # Use only the date part.

    # Group by location, date, and type, and count items
    grouped = df.groupby(['Location', 'Date', 'Type']).size().reset_index(name='Count')

    # Print the results by location and date
    for location in grouped['Location'].unique():
        print(f"\nLocation: {location}")
        loc_data = grouped[grouped['Location'] == location]
        for date in loc_data['Date'].unique():
            print(f" Date: {date}")
            date_data = loc_data[loc_data['Date'] == date]
            for _, row in date_data.iterrows():
                # print(f"    Type: {row['Type']} - Count: {row['Count']}")
                print(f"    {row['Count']} {row['Type']}")

    # Print total count for each Type for all days at the end
    overall_type_totals = grouped.groupby('Type')['Count'].sum()
    print("\nTotal by Type (all days):")
    for type_name, total in overall_type_totals.items():
        print(f"    Total {type_name}: {total}")


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    root.title("Project Load Count")
    root.geometry("600x200")

    Label(root, text="Select or Drag and Drop the Excel file for Project Load Count").pack(pady=10)
    drop_label = Label(root, text="Drag and drop file here", relief="ridge", width=40, height=3)
    drop_label.pack(pady=10)
    drop_label.drop_target_register(DND_FILES)
    drop_label.dnd_bind('<<Drop>>', handle_drop)
    Button(root, text="Browse", command=select_file).pack(pady=10)
    root.mainloop()
