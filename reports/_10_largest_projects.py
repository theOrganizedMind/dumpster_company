import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
import tkinter as tk
from tkinter import filedialog, ttk

from postgresql import get_db_connection
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

DEFAULT_START_DATE = "2026-01-01" 
DEFAULT_END_DATE = "2026-07-31"

# Fictitious data used when "Sample Data" is selected (no SQL/Excel source required).
SAMPLE_PROJECTS = [
    ("Bluegrass Hauling Co.", "142 Maplewood Ave", "Springvale", 187650.00),
    ("Bluegrass Hauling Co.", "89 Copper Creek Rd", "Springvale", 164320.00),
    ("Bluegrass Hauling Co.", "310 Willow Bend Dr", "Springvale", 139075.00),
    ("Northgate Builders LLC", "27 Foxridge Ln", "Millhaven", 121500.00),
    ("Northgate Builders LLC", "455 Cobblestone Way", "Millhaven", 108990.00),
    ("Crestview Excavation", "1203 Sunset Ridge Blvd", "Millhaven", 96410.00),
    ("Crestview Excavation", "76 Timberlake Ct", "Ashford", 84275.00),
    ("Ironoak Contracting", "33 Prairie View Rd", "Ashford", 71850.00),
    ("Ironoak Contracting", "588 Hollow Brook St", "Ashford", 58620.00),
    ("Summit Site Services", "14 Redstone Ave", "Grantfield", 45300.00),
]

def get_sample_projects():
    """Return a fictitious sample dataset for demo purposes when no SQL/Excel source is available."""
    return list(SAMPLE_PROJECTS)

def fetch_10_largest_projects(start_date, end_date):
    """Fetch 10 largest projects from PostgreSQL for the provided date range."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM _10_largest_projects(%s, %s);",
                (start_date, end_date),
            )
            rows = cur.fetchall()

    if not rows:
        print("No projects found for the selected date range.")
        return []

    company_width = max(len("Company"), max(len(company) for company, _, _, _ in rows)) + 3
    street_width = max(len("Street"), max(len(street) for _, street, _, _ in rows)) + 3
    city_width = max(len("City"), max(len(city) for _, _, city, _ in rows)) + 3
    total_price_width = 20
    divider_width = company_width + street_width + city_width + total_price_width
    row_format = (
        f"{{company:<{company_width}}}{{street:<{street_width}}}"
        f"{{city:<{city_width}}}{{total_price:>{total_price_width}}}"
    )

    print(f"\n10 Largest Projects ({start_date} to {end_date})")
    print("-" * divider_width)
    print(row_format.format(company="Company", street="Street", city="City", 
                            total_price="Total Price"))
    print("-" * divider_width)

    for company, street, city, total_price in rows:
        print(row_format.format(company=company, street=street, city=city, 
                                total_price=f"${float(total_price):,.2f}"))

    return rows

def select_file():
    """
    Opens a file dialog for the user to select an Excel file (.xlsx or .xls).
    If a file is selected, processes the file and displays the top 10 projects.

    Returns:
        None
    """
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if file_path:
        process_file(file_path)

def calculate_data():
    """Choose the data source based on the combo box selection."""
    data_source = data_source_var.get()

    if data_source == "Sample Data":
        rows = get_sample_projects()
        sample_df = pd.DataFrame(rows, columns=["Company", "Street", "City", "Total_Price"])
        sample_df["Location"] = (
            sample_df["Street"].fillna("").astype(str).str.strip()
            + ", "
            + sample_df["City"].fillna("").astype(str).str.strip()
        )
        show_popup(sample_df[["Company", "Location", "Total_Price"]])
        return

    if data_source == "SQL":
        start_date = start_date_entry.get().strip() or DEFAULT_START_DATE
        end_date = end_date_entry.get().strip() or DEFAULT_END_DATE
        rows = fetch_10_largest_projects(start_date, end_date)
        if not rows:
            return

        sql_df = pd.DataFrame(rows, columns=["Company", "Street", "City", "Total_Price"])
        sql_df["Location"] = (
            sql_df["Street"].fillna("").astype(str).str.strip()
            + ", "
            + sql_df["City"].fillna("").astype(str).str.strip()
        )
        sql_df["Location"] = sql_df["Location"].str.replace(r"^,\s*|,\s*$", "", regex=True)
        sql_df["Location"] = sql_df["Location"].str.replace(r",\s*,", ",", regex=True)
        sql_df["Location"] = sql_df["Location"].str.strip(", ")
        show_popup(sql_df[["Company", "Location", "Total_Price"]])
        return

    if data_source == "Excel":
        select_file()

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
        DataFrame: Top 10 projects ready for display.
    """
    data = pd.read_excel(file_path, engine="openpyxl", header=2, skipfooter=1)
    data['Price'] = data['Price'].fillna(0)
    company_location_price = {}
    for _, row in data.iterrows():
        normalized_location = normalize_address(str(row['Location']))
        key = (row['Company'], normalized_location)
        if key in company_location_price:
            company_location_price[key] += row['Price']
        else:
            company_location_price[key] = row['Price']
    df = pd.DataFrame(company_location_price.items(), columns=['Company_Location', 'Total_Price'])
    df[['Company', 'Location']] = pd.DataFrame(df['Company_Location'].tolist(), index=df.index)
    df.drop(columns=['Company_Location'], inplace=True)
    largest_projects = df.nlargest(10, 'Total_Price').reset_index(drop=True)
    show_popup(largest_projects)
    return largest_projects

def plot_top_10_projects(df):
    """
    Plots the 10 largest projects as a horizontal bar chart (by street) next to
    a pie chart (by company) in a single matplotlib figure.

    Args:
        df (DataFrame): DataFrame containing Company, Total_Price, and either
            Street or Location columns for the top 10 projects.

    Returns:
        None
    """
    chart_df = df.copy()
    chart_df['Total_Price'] = pd.to_numeric(chart_df['Total_Price'], errors='coerce')
    chart_df = chart_df.nlargest(10, 'Total_Price')
    street_col = 'Street' if 'Street' in chart_df.columns else 'Location'

    bar_df = chart_df.sort_values('Total_Price', ascending=True)
    pie_df = chart_df.groupby('Company')['Total_Price'].sum().sort_values(ascending=False)

    fig, (ax_bar, ax_pie) = plt.subplots(1, 2, figsize=(14, 6))

    bars = ax_bar.barh(bar_df[street_col].astype(str), bar_df['Total_Price'], color='steelblue')
    ax_bar.set_xlabel('Total Price ($)')
    ax_bar.set_title('10 Largest Projects by Street')
    ax_bar.xaxis.set_major_formatter(lambda x, _: f'${x:,.0f}')

    cursor = mplcursors.cursor(bars, hover=True)
    cursor.connect(
        "add",
        lambda sel: sel.annotation.set_text(f"${bar_df['Total_Price'].iloc[sel.index]:,.2f}"),
    )

    ax_pie.pie(pie_df, labels=pie_df.index, autopct='%1.1f%%', startangle=90)
    ax_pie.set_title('10 Largest Projects by Company')
    ax_pie.axis('equal')

    fig.tight_layout()
    plt.show()

def show_popup(df):
    """
    Displays the 10 largest projects in a popup window using a Tkinter Text widget.

    Args:
        df (DataFrame): DataFrame containing the top 10 projects.

    Returns:
        None
    """
    display_df = df.copy()

    if 'Location' not in display_df.columns and 'Street' in display_df.columns and 'City' in display_df.columns:
        display_df['Location'] = (
            display_df['Street'].fillna('').astype(str).str.strip()
            + ', '
            + display_df['City'].fillna('').astype(str).str.strip()
        )
        display_df['Location'] = display_df['Location'].str.replace(r'^,\s*|,\s*$', '', regex=True)
        display_df['Location'] = display_df['Location'].str.replace(r',\s*,', ',', regex=True)
        display_df['Location'] = display_df['Location'].str.strip(', ')

    company_width = max(len("Company"), max(len(str(c)) for c in display_df['Company'])) + 3
    location_width = max(len("Location"), max(len(str(l)) for l in display_df['Location'])) + 3
    total_price_width = 20
    divider_width = company_width + location_width + total_price_width
    row_format = f"{{company:<{company_width}}}{{location:<{location_width}}}{{total_price:>{total_price_width}}}"

    popup = tk.Toplevel()
    popup.title("10 Largest Projects")
    popup.geometry("800x300")
    text = tk.Text(popup, wrap="none", font=("Consolas", 11))
    text.pack(expand=True, fill="both", padx=10, pady=10)
    text.insert("end", row_format.format(company="Company", 
                                         location="Location", 
                                         total_price="Total Price") + "\n")
    text.insert("end", "-" * divider_width + "\n")

    for _, row in display_df.iterrows():
        company = str(row.get('Company', ''))
        location = str(row.get('Location', ''))
        total_price = row.get('Total_Price', 0)
        text.insert("end", row_format.format(company=company, 
                                             location=location,
                                             total_price=f"${float(total_price):,.2f}") + "\n")

    text.config(state="disabled")

    plot_top_10_projects(display_df)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("10 Largest Projects")
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
