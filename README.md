# Dumpster Company Financials

This project is a financial management and reporting tool for a dumpster company. 
It calculates and displays various financial metrics, including payroll, expenses, 
truck values, dumpster counts, disposal costs, and revenue. It also includes machine 
learning predictions for future dumpster counts and disposal costs, as well as a suite 
of reporting scripts for analyzing operational data.

## Project Structure

### Root Files

- **hourly_rate.py**: Calculates daily, monthly, and yearly pay based on hourly wage and overtime.
- **pds_to_tons.py**: Converts pounds to tons (short, long, or recycling) and copies the result to clipboard.
- **requirements.txt**: Lists all required Python packages.
- **LICENSE.txt**: MIT License.
- **README.md**: Project documentation.

### financials/

- **expenses.py**: Contains data for loans, subscriptions, insurance, and monthly expenses.
- **dumpster_count.py**: Contains data for monthly dumpster counts.
- **disposal.py**: Contains data for monthly disposal costs.
- **payroll.py**: Contains data for employee payroll and summary calculations.
- **trucks.py**: Contains data for truck values and summary calculations.
- **monthly_sales.py**: Contains data for monthly sales.
- **revenue.py**: Contains yearly revenue and net profit data.
- **financials_main.py**: Main script that calculates and displays financial metrics,
and includes machine learning predictions.

### reports/

- **_10_largest_projects.py**: Finds and displays the 10 largest projects by company and location.
- **annual_tonnage_report.py**: Summarizes annual tonnage by disposal location.
- **disposal_report.py**: Cleans and processes disposal reports, saving results to Excel.
- **dumpster_inventory.py**: Tracks unique dumpster locations and updates inventory text files.
- **load_count.py**: Counts loads by location, date, and type, excluding certain descriptions.
- **normalize_address.py**: Normalizes address strings for consistency across reports.
- **profit_and_loss_report.py**: Displays and charts the top 10 biggest expenses from profit and loss reports.
- **revenue_by_customer.py**: Calculates and charts revenue, gross profit, and percent profit by customer.

## Requirements

Install all required packages using:

sh
pip install -r requirements.txt

## Usage

### Financials

To run the main financial management tool, execute:

sh
python financials/financials_main.py


This opens a Tkinter GUI for calculating and displaying financial metrics or charts.

### Reports

Each script in the reports/ directory is standalone and provides a GUI for file
selection or drag-and-drop. Run any script directly, for example:

sh
python reports/annual_tonnage_report.py


Follow the instructions in each GUI to process your Excel or CSV files.

## Options in financials_main.py

- **Daily**: Displays daily operating cost, per driver, and rate per hour.
- **Monthly**: Displays total monthly payroll, expenses, operating cost, and average fuel cost.
- **Yearly**: Displays total yearly payroll, expenses, and average yearly fuel cost.
- **Sales**: Displays sales metrics for selected months.
- **Trucks**: Displays truck values and averages.
- **Dumpsters**: Displays dumpster run counts and averages.
- **Disposal**: Displays disposal cost metrics.
- **Revenue**: Displays revenue and profit metrics.
- **Quickbooks**: Displays Quickbooks monthly expenses.
- **Predictions**: Predicts and plots data for sales, expenses, dumpster count, and disposal cost.
- **Sales vs Expenses(Matplot)**: Compares sales and expenses in a grouped bar chart.

## License

This project is licensed under the MIT License.  
See the (LICENSE.txt) file for details.
