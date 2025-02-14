# Dumpster Company Financials

This project is a financial management tool for a dumpster company. 
It calculates and displays various financial metrics, including payroll, 
expenses, truck values, dumpster counts, and disposal costs. It also includes 
machine learning predictions for future dumpster counts and disposal costs.

## Project Structure

### Files

- **financials/expenses.py**: Contains data for loans, subscriptions, and 
  insurance expenses.
- **financials/dumpster_count.py**: Contains data for monthly dumpster counts.
- **financials/disposal.py**: Contains data for monthly disposal costs.
- **financials/payroll.py**: Contains data for employee payroll.
- **financials/trucks.py**: Contains data for truck values.
- **financials/financials_main.py**: Main script that calculates and displays 
  financial metrics, and includes machine learning predictions.

## Requirements

The project requires the following Python packages:

- contourpy==1.3.1
- cycler==0.12.1
- fonttools==4.56.0
- joblib==1.4.2
- kiwisolver==1.4.8
- matplotlib==3.10.0
- mplcursors==0.6
- numpy==2.2.3
- packaging==24.2
- pandas==2.2.3
- pillow==11.1.0
- pyparsing==3.2.1
- python-dateutil==2.9.0.post0
- pytz==2025.1
- scikit-learn==1.6.1
- scipy==1.15.1
- six==1.17.0
- threadpoolctl==3.5.0
- tzdata==2025.1

You can install the required packages using the following command:

```sh
pip install -r requirements.txt
```

## Usage
To run the financial management tool, execute the financials_main.py script:

This will open a Tkinter GUI where you can select various options to calculate 
and display financial metrics or display charts.

## Options
- Daily: Displays daily operating cost, daily operating cost per driver, and 
  rate per hour.
- Monthly: Displays total monthly payroll, total monthly expenses, total monthly 
  operating cost, and total average monthly fuel cost.
- Yearly: Displays total yearly payroll, total yearly expenses, and total average 
  yearly fuel cost.
- Trucks: Displays the total cost of all trucks and the average truck cost.
- Dumpsters: Displays the total number of dumpsters ran, the average number of 
  dumpster runs per month, the average number of dumpster runs per day, and the 
  estimated net income per dumpster.
- Disposal: Displays the total disposal cost, the average monthly disposal cost, 
  and the average daily disposal cost.
- Predictions: Predicts and plots data for monthly dumpster count and monthly 
  disposal cost for the next three months.

## License
This project is licensed under the MIT License. 
See the LICENSE.txt file for details.