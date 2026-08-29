import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
import tkinter as tk
from tkinter import filedialog, Scrollbar, Frame, ttk
from tkinter import VERTICAL, BOTH, LEFT, RIGHT, Y

from postgresql import get_db_connection

# =========================================================================== #
# =============================== INFO ====================================== #
# =========================================================================== #
# 
# =========================================================================== #
# =============================== TODO ====================================== #
# =========================================================================== #
#
# =========================================================================== #

DEFAULT_START_DATE = "2026-01-01"
DEFAULT_END_DATE = "2026-06-30"

# Fictitious data used when "Sample Data" is selected (no SQL/Excel source required).
SAMPLE_TONNAGE = [
    ("Northgate Landfill", "Millhaven", 4820.75),
    ("Crestview Transfer Station", "Ashford", 3765.40),
    ("Bluegrass Regional Landfill", "Springvale", 3190.10),
    ("Ironoak Waste Facility", "Grantfield", 2475.60),
    ("Summit C&D Recycling", "Millhaven", 1980.25),
    ("Redstone Disposal Site", "Ashford", 1340.90),
]

def get_sample_tonnage():
    """Return a fictitious sample dataset for demo purposes when no SQL/Excel source is available."""
    return list(SAMPLE_TONNAGE)

def fetch_annual_tonnage_report(start_date, end_date):
    """Fetch annual tonnage report from PostgreSQL for the provided date range."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT * 
                FROM annual_tonnage_report(%s, %s)
                ORDER BY total_tons DESC;
                """,
                (start_date, end_date),
            )
            rows = cur.fetchall()

    if not rows:
        print("No projects found for the selected date range.")
        return []

    disposal_width = max(len("Disposal"), max(len(disposal) for disposal, _, _ in rows)) + 3
    city_width = max(len("City"), max(len(city) for _, city, _ in rows)) + 3
    total_tons_width = 20
    divider_width = disposal_width + city_width + total_tons_width
    row_format = (
        f"{{disposal:<{disposal_width}}}{{city:<{city_width}}}{{total_tons:>{total_tons_width}}}"
    )
    print(f"\nAnnual Tonnage Report ({start_date} to {end_date})")
    print("-" * divider_width)
    print(row_format.format(disposal="Disposal", city="City", total_tons="Total Tons"))
    print("-" * divider_width)

    for disposal, city, total_tons in rows:
        print(row_format.format(disposal=disposal, city=city, 
                                total_tons=f"{float(total_tons):,.2f}"))

    return rows

def plot_tonnage_by_disposal(df):
    """
    Plots total tons by disposal location as a horizontal bar chart (with hover
    tooltips) next to a pie chart in a single matplotlib figure.

    Args:
        df (DataFrame): DataFrame containing Disposal and Total_Tons columns.

    Returns:
        None
    """
    chart_df = df.copy()
    chart_df['Total_Tons'] = pd.to_numeric(chart_df['Total_Tons'], errors='coerce')
    chart_df = chart_df.groupby('Disposal', as_index=False)['Total_Tons'].sum()

    bar_df = chart_df.sort_values('Total_Tons', ascending=True)
    pie_df = chart_df.sort_values('Total_Tons', ascending=False)

    fig, (ax_bar, ax_pie) = plt.subplots(1, 2, figsize=(14, 6))

    bars = ax_bar.barh(bar_df['Disposal'].astype(str), bar_df['Total_Tons'], color='steelblue')
    ax_bar.set_xlabel('Total Tons')
    ax_bar.set_title('Total Tons by Disposal Location')

    cursor = mplcursors.cursor(bars, hover=True)
    cursor.connect(
        "add",
        lambda sel: sel.annotation.set_text(f"{bar_df['Total_Tons'].iloc[sel.index]:,.2f} tons"),
    )

    total_tons_sum = pie_df['Total_Tons'].sum()
    wedges = ax_pie.pie(pie_df['Total_Tons'], startangle=90)[0]
    ax_pie.set_title('Total Tons by Disposal Location')
    legend_labels = [
        f"{disposal} ({tons / total_tons_sum * 100:.1f}%)"
        for disposal, tons in zip(pie_df['Disposal'], pie_df['Total_Tons'])
    ]
    ax_pie.legend(
        wedges,
        legend_labels,
        title='Disposal',
        loc='center left',
        bbox_to_anchor=(1, 0, 0.5, 1),
    )
    ax_pie.axis('equal')

    fig.tight_layout()
    plt.show()

def show_popup(df):
    """Display annual tonnage results in a popup window."""
    disposal_width = max(len("Disposal Location"), max(len(str(d)) for d in df['Disposal'])) + 3
    total_tons_width = 20
    divider_width = disposal_width + total_tons_width
    row_format = f"{{disposal:<{disposal_width}}}{{total_tons:>{total_tons_width}}}"

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

    text.insert("end", row_format.format(disposal="Disposal Location", total_tons="Total Tons") + "\n")
    text.insert("end", "-" * divider_width + "\n")
    for _, row in df.iterrows():
        disposal = str(row.get('Disposal', ''))
        total_tons = float(row.get('Total_Tons', 0))
        text.insert("end", row_format.format(disposal=disposal, total_tons=f"{total_tons:,.2f}") + "\n")
    text.config(state="disabled")

    plot_tonnage_by_disposal(df)

def calculate_data():
    """Choose SQL or Excel as the report data source."""
    data_source = data_source_var.get()

    if data_source == "Sample Data":
        rows = get_sample_tonnage()
        sample_df = pd.DataFrame(rows, columns=["Disposal", "City", "Total_Tons"])
        show_popup(sample_df[["Disposal", "Total_Tons"]])
        return

    if data_source == "SQL":
        start_date = start_date_entry.get().strip() or DEFAULT_START_DATE
        end_date = end_date_entry.get().strip() or DEFAULT_END_DATE
        rows = fetch_annual_tonnage_report(start_date, end_date)
        if not rows:
            return

        sql_df = pd.DataFrame(rows, columns=["Disposal", "City", "Total_Tons"])
        show_popup(sql_df[["Disposal", "Total_Tons"]])
        return

    if data_source == "Excel":
        select_file()

def select_file():
    """Open a file dialog for the user to select an Excel file."""
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if file_path:
        if 'root' in globals():
            root.withdraw()
        process_file(file_path)

def handle_drop(event):
    """Handle drag-and-drop event for an Excel file."""
    file_path = event.data.strip('{}')
    if 'root' in globals():
        root.withdraw()
    process_file(file_path)

def process_file(file_path):
    """Process the Excel file and return the annual tonnage report as a DataFrame."""
    data = pd.read_excel(file_path, engine='openpyxl', header=2, skipfooter=1)
    data['Tons'] = data['Tons'].fillna(0)
    grouped_data = data.groupby('Disposal')['Tons'].sum().reset_index(name='Total_Tons')
    grouped_data = grouped_data.sort_values('Total_Tons', ascending=False).reset_index(drop=True)
    show_popup(grouped_data)
    return grouped_data

if __name__ == "__main__":
        root = tk.Tk()
        root.title("Annual Tonnage Report")
        root.config(width=450, height=250, padx=25, pady=25)

        data_source_label = tk.Label(root, text="Data Source:")
        data_source_label.grid(column=0, row=0, padx=5, pady=5, sticky="e")

        data_source_var = tk.StringVar(value="Sample Data")

        data_source_options = ttk.Combobox(
            root,
            width=20,
            state="readonly",
            textvariable=data_source_var,
            values=["SQL", "Excel", "Sample Data"],
        )
        data_source_options.grid(column=1, row=0, padx=5, pady=5)

        start_date_label = tk.Label(root, text="Start Date YYYY-MM-DD:")
        start_date_label.grid(column=0, row=1, padx=5, pady=5)
        start_date_entry = tk.Entry(root, width=20)
        start_date_entry.insert(0, DEFAULT_START_DATE)
        start_date_entry.grid(column=1, row=1, padx=5, pady=5)

        end_date_label = tk.Label(root, text="End Date YYYY-MM-DD:")
        end_date_label.grid(column=0, row=2, padx=5, pady=5)
        end_date_entry = tk.Entry(root, width=20)
        end_date_entry.insert(0, DEFAULT_END_DATE)
        end_date_entry.grid(column=1, row=2, padx=5, pady=5)

        calculate_button = ttk.Button(
            root,
            text="Calculate",
            command=calculate_data,
        )
        calculate_button.grid(column=1, row=3, padx=5, pady=5)

        root.mainloop()
