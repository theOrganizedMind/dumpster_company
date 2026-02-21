import pandas as pd
import tkinter as tk
from tkinter import filedialog, Label, Button, Scrollbar, Frame
from tkinter import VERTICAL, BOTH, LEFT, RIGHT, Y
from tkinterdnd2 import DND_FILES, TkinterDnD

# =========================================================================== #
# =============================== INFO ====================================== #
# =========================================================================== #
# 
# =========================================================================== #
# =============================== TODO ====================================== #
# =========================================================================== #
#
# =========================================================================== #

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

# TkinterDnD GUI for file selection or drag-and-drop
root = TkinterDnD.Tk()
root.title("Annual Tonnage Report")
root.geometry("600x400")

instructions = (
    "Info:\n"
    "Steps:\n"
    "1.) Filter invoicing board for Prior Year and <City>.\n"
    "2.) Export to Excel.\n"
    "3.) Run this script to see the annual tonnage report.\n"
    "4.) Optionally save the results to an Excel file.\n"
)

instructions_label = Label(root, text=instructions, justify="left", 
                           font=("Times New Roman", 12), wraplength=480)
instructions_label.pack(pady=10)

Label(root, text="Select or Drag and Drop the Excel file for Annual Tonnage Report").pack(pady=10)
drop_label = Label(root, text="Drag and drop file here", relief="ridge", width=40, height=3)
drop_label.pack(pady=10)
drop_label.drop_target_register(DND_FILES)
drop_label.dnd_bind('<<Drop>>', handle_drop)
Button(root, text="Browse", command=select_file).pack(pady=10)
root.mainloop()
