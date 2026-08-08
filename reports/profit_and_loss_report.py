import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import tkinter as tk
from tkinter import filedialog, Label, Button, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD

# =========================================================================== #
# ================================== INFO =================================== #
# =========================================================================== #
# - Iterates through the dataframe and prints the top 10 biggest expenses with
#    the name of the expense and total price.
# - Uses matplotlib to create a pie chart of the top 10 expenses.
# 1.) Filter profit and loss report for previous year and export as .csv.
# 2.) Delete all total rows from the file.
# 3.) Add 'Expenses' and 'Total' headers. 
# =========================================================================== #
# ================================== TODO =================================== #
# =========================================================================== #
# TODO: 
# =========================================================================== #

def select_file():
    """Open a file dialog for the user to select a CSV or Excel file."""
    file_path = filedialog.askopenfilename(filetypes=[("CSV/Excel files", "*.csv *.xlsx *.xls")])
    if file_path:
        root.withdraw()
        process_file(file_path)

def handle_drop(event):
    """Handle drag-and-drop event for a CSV or Excel file."""
    file_path = event.data.strip('{}')
    root.withdraw()
    process_file(file_path)

def process_file(file_path):
    """Process the selected file, display results, and optionally save to Excel."""
    # Read file based on extension
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        data = pd.read_csv(file_path)
    elif ext in [".xlsx", ".xls"]:
        data = pd.read_excel(file_path)
    else:
        messagebox.showerror("Error", "Unsupported file type.")
        return

    df = pd.DataFrame(data)

    # Remove rows where 'Expenses' contains 'Total'
    df = df[~df['Expenses'].str.lower().str.contains('total')]

    # Check for required columns
    try:
        if 'Expenses' not in df.columns or 'Total' not in df.columns:
            raise KeyError("Missing 'Expenses' or 'Total' column headers.")
    except KeyError:
        messagebox.showerror("Error", 
                             "Please ensure your file has 'Expenses' and 'Total' columns.")
        return
    
    # Remove commas from 'Total' column if present and convert to float
    if df['Total'].dtype == object:
        df['Total'] = df['Total'].replace({',': ''}, regex=True).astype(float)

    # Get top 10 expenses
    top_expenses = df.nlargest(10, 'Total')

    # Display results in a popup window
    show_popup(top_expenses)

    # Plot pie chart
    plt.figure(figsize=(10, 7))
    plt.title('Top 10 Biggest Expenses')
    wedges, texts, autotexts = plt.pie(top_expenses['Total'], autopct='%1.1f%%', startangle=140)
    labels = [f"{expense}: ${total:,.2f}" for expense, total in zip(top_expenses['Expenses'], top_expenses['Total'])]
    plt.legend(wedges, labels, title="Expenses", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    plt.show()

    # Ask user if they want to save results
    should_save = messagebox.askyesno("Save Results", 
                                      "Would you like to save the top 10 expenses to an Excel file?")
    if should_save:
        todays_date = datetime.now().strftime("%m%d%Y")
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        default_filename = f"top_ten_expenses_({todays_date}).xlsx"
        save_path = filedialog.asksaveasfilename(
            initialdir=downloads_folder,
            initialfile=default_filename,
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx *.xls")]
            )
        if save_path:
            top_expenses.to_excel(save_path, index=False, freeze_panes=(1, 1))
            messagebox.showinfo("Success", f"File saved to {save_path}")

def show_popup(df):
    """Display the top 10 expenses in a popup window."""
    popup = tk.Toplevel()
    popup.title("Top 10 Biggest Expenses")
    popup.geometry("600x350")
    text = tk.Text(popup, wrap="none", font=("Consolas", 11))
    text.pack(expand=True, fill="both", padx=10, pady=10)
    text.insert("end", f"{'Rank':<5} {'Expense':<35} {'Total':>15}\n")
    text.insert("end", "-"*60 + "\n")
    for i, row in enumerate(df.itertuples(), start=1):
        text.insert("end", f"{i:<5} {row.Expenses:<35} ${row.Total:>12,.2f}\n")
    text.config(state="disabled")


root = TkinterDnD.Tk()
root.title("Profit and Loss Report")
root.geometry("600x400")

instructions = (
    "Info:\n"
    "Iterates through the dataframe and prints the top 10 biggest expenses with "
    "the name of the expense and total price.\n"
    "Uses matplotlib to create a pie chart of the top 10 expenses.\n"
    "Steps:\n"
    "1.) Filter profit and loss report for previous year and export.\n"
    "2.) Delete total rows from the excel file.\n"
    "3.) Add 'Expense' and 'Total' headers.\n"
    "4.) Run this script to see the top 10 expenses and a pie chart.\n"
    "5.) Optionally save the results to an Excel file.\n"
)

instructions_label = Label(root, text=instructions, justify="left", 
                           font=("Times New Roman", 12), wraplength=480)
instructions_label.pack(pady=10)

Label(root, text="Select or Drag and Drop the CSV/Excel file for Profit and Loss Report").pack(pady=10)
drop_label = Label(root, text="Drag and drop file here", relief="ridge", width=40, height=3)
drop_label.pack(pady=10)
drop_label.drop_target_register(DND_FILES)
drop_label.dnd_bind('<<Drop>>', handle_drop)
Button(root, text="Browse", command=select_file).pack(pady=10)
root.mainloop()
