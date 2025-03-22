import statistics
import matplotlib.pyplot as plt
import mplcursors
import tkinter as tk
from tkinter import messagebox, ttk
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np  
from idlelib.tooltip import Hovertip

from expenses import monthly_expenses
import payroll
from trucks import trucks
from dumpster_count import monthly_dumpster_count
from disposal import monthly_disposal_cost

# ========================================================================== #
# ================================== TODO ================================== #
# ========================================================================== #
# TODO: 
# ========================================================================== #

NUM_MONTHS = 12
WORK_DAYS_IN_MONTH = 20
NUM_TRUCKS = 3
NUM_DRIVERS = 3
DAILY_WORK_HOURS = 10
PROFIT_MARGIN = 1.35
AVG_DAILY_FUEL_PER_TRUCK = 150

# ========================================================================== #
# ================================ Payroll ================================= #
# ========================================================================== #
total_payroll = round(sum(payroll.employees.values()))
total_monthly_payroll = round(total_payroll / NUM_MONTHS, 2)
daily_payroll = total_monthly_payroll / WORK_DAYS_IN_MONTH

# ========================================================================== #
# ================================ Expenses ================================ #
# ========================================================================== #
total_monthly_expenses = round(sum(monthly_expenses.values()), 2)

total_yearly_expenses = total_monthly_expenses * NUM_MONTHS

total_avg_yearly_fuel_cost = (NUM_DRIVERS * AVG_DAILY_FUEL_PER_TRUCK 
                                * WORK_DAYS_IN_MONTH * NUM_MONTHS)

monthly_fuel_cost = NUM_DRIVERS * AVG_DAILY_FUEL_PER_TRUCK * WORK_DAYS_IN_MONTH

total_daily_expenses = total_monthly_expenses / WORK_DAYS_IN_MONTH

total_daily_fuel = AVG_DAILY_FUEL_PER_TRUCK * NUM_DRIVERS

daily_operating_cost = round(daily_payroll + total_daily_expenses
                            + total_daily_fuel, 2)

monthly_operating_cost = round(daily_operating_cost * WORK_DAYS_IN_MONTH, 2)

daily_operating_cost_per_driver = round(daily_operating_cost / NUM_DRIVERS, 2)

hourly_rate = round(daily_operating_cost_per_driver / DAILY_WORK_HOURS * PROFIT_MARGIN, 2)

# ========================================================================== #
# =========================== Machine Learning ============================= #
# ========================================================================== #
def predict_and_plot(data_dict, column_name, future_months=3):
    """
    Makes a prediction for the specified number of future months for 
    Dumpster count, and Disposal cost.
    
    Parameters:
    data_dict (dict): Dictionary containing historical data.
    column_name (str): Name of the column to be used in the plot.
    future_months (int): Number of future months to predict. Default is 3.
    
    Returns:
    None
    """
    # Prepare the data
    data_column = list(data_dict.values())
    X = np.arange(len(data_column)).reshape(-1, 1)
    y = np.array(data_column)

    # Split the data into training and testing sets using TimeSeriesSplit
    tscv = TimeSeriesSplit(n_splits=5)
    for train_index, test_index in tscv.split(X):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

    # Train the model on the training set
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Predict the future months
    X_future = np.arange(len(data_column), len(data_column) + future_months).reshape(-1, 1)
    y_future = model.predict(X_future)

    # Plot the results
    plt.figure(figsize=(10, 5))

    # Plot the previous data (last twelve months)
    plt.plot(X[-12:], y[-12:], 'bo-', label='Previous Data')

    # Plot predicted data (next three months)
    plt.plot(np.concatenate((X[-1:], X_future)), np.concatenate((y[-1:], y_future)), 
             'ro--', label="Predicted Data")

    # Add labels and title
    plt.xlabel('Month')
    plt.ylabel(column_name)
    plt.title(f"{column_name}, For Past 12 Months and Predicted Next 3 Months")

    # Add x-axis labels
    months = list(data_dict.keys())[-12:] + ["30 Days", "60 Days", "90 Days"]
    plt.xticks(np.arange(len(data_column) - 12, len(data_column) + future_months), 
               months, rotation=45)

    # Add legend
    plt.legend()

    # Implement mplcurors for interactive tooltips
    cursor = mplcursors.cursor(hover=True)
    cursor.connect("add", lambda sel: sel.annotation.set_text(f"{sel.target[1]:,.0f}"))

    # Adjust layout to prevent x-axis labels from going off bottom of the screen
    plt.tight_layout()

    # Show plot
    plt.show()

    # Evaluate the model on the testing set
    # y_pred = model.predict(X_test)
    # print(f"Model R^2 score: {model.score(X_test, y_test)}")
    # print(f"Mean Absolute Error: {mean_absolute_error(y_test, y_pred)}")
    # print(f"Mean Squared Error: {mean_squared_error(y_test, y_pred)}")
    # print(f"Root Mean Squared Error: {np.sqrt(mean_squared_error(y_test, y_pred))}")
    # print("Predicted values:", y_pred)
    # print("Actual values:", y_test)

# ========================================================================== #
# =========================== Calculate Financials ========================= #
# ========================================================================== #
def display_financials(title, financials):
    """
    Helper function to display financial metrics.
    
    Parameters:
    title (str): The title of the financial section.
    financials (dict): Dictionary containing financial metrics to display.
    
    Returns:
    None
    """
    print("\n")
    print(title.center(20, "-"))
    for key, value in financials.items():
        print(f"{key} = {value:,.2f}")


def calculate_financials():
    """
    Calculate and display various financial metrics based on the selected option.
    
    Returns: 
        None
    """
    try:
        option = options.get()
        number_of_months = num_months_entry.get()

        # Determine the number of months to calculate
        if number_of_months.isdigit():
            number_of_months = int(number_of_months)
        else:
            number_of_months = len(monthly_dumpster_count) # Default to all months

        if option == "Daily":
            financials = {
                "Daily Operating Cost": daily_operating_cost,
                "Daily Operating Cost per Driver": daily_operating_cost_per_driver,
                "Rate per Hour": hourly_rate
            }
            display_financials("Daily", financials)

        elif option == "Monthly":
            financials = {
                "Total monthly payroll": total_monthly_payroll,
                "Total monthly expenses": total_monthly_expenses,
                "Total monthly operating cost": monthly_operating_cost,
                "Total average monthly fuel cost": monthly_fuel_cost
            }
            display_financials("Monthly", financials)

        elif option == "Yearly":
            financials = {
                "Total yearly payroll": total_payroll,
                "Total yearly expenses": total_yearly_expenses,
                "Total average yearly fuel cost": total_avg_yearly_fuel_cost
            }
            display_financials("Yearly", financials)

        elif option == "Trucks":
            print("\n")
            print("Trucks".center(20, "-"))
            for t, v in trucks.items():
                print(f"{t}: ${v:,.2f}")
            total_trucks = round(sum(trucks.values()))
            avg_truck_cost = statistics.mean(trucks.values())
            financials = {
                "Total cost of all trucks": total_trucks,
                "Average truck cost": avg_truck_cost
            }
            display_financials("Trucks", financials)

        elif option == "Dumpsters":
            # Calculate results based on the number of months
            selected_months = list(monthly_dumpster_count.keys())[-number_of_months:]
            selected_values = list(monthly_dumpster_count.values())[-number_of_months:]
            total_num_dumpsters = sum(selected_values)
            avg_dumpsters_month = round(statistics.mean(selected_values))
            avg_dumpsters_day = avg_dumpsters_month // WORK_DAYS_IN_MONTH
            rate_per_dumpster = round(monthly_operating_cost / avg_dumpsters_month)
            if 12 > number_of_months:
                financials = {
                    f"Total number of dumpsters ran in the past {number_of_months} months": total_num_dumpsters,
                    f"The average number of dumpster runs per month in the past {number_of_months} months": avg_dumpsters_month,
                    f"The average number of dumpster runs per day in the past {number_of_months} months": avg_dumpsters_day,
                    f"Estimated net income per dumpster in the past {number_of_months} months should be": rate_per_dumpster,
                }
            else:
                financials = {
                    f"Total number of dumpsters ran in the past {round(number_of_months / 12, 2)} years": total_num_dumpsters,
                    f"The average number of dumpster runs per month in the past {round(number_of_months / 12, 2)} years": avg_dumpsters_month,
                    f"The average number of dumpster runs per day in the past {round(number_of_months / 12, 2)} years": avg_dumpsters_day,
                    f"Estimated net income per dumpster in the past {round(number_of_months / 12, 2)} years should be": rate_per_dumpster,
                }
            display_financials("Dumpsters", financials)

        elif option == "Disposal":
            # Calculate results based on the number of months
            selected_months = list(monthly_disposal_cost.keys())[-number_of_months:]
            selected_values = list(monthly_disposal_cost.values())[-number_of_months:]
            total_disposal_cost = sum(selected_values)
            avg_disposal_cost = round(statistics.mean(selected_values))
            avg_daily_disposal_cost = round(avg_disposal_cost / WORK_DAYS_IN_MONTH)
            if 12 > number_of_months:
                financials = {
                    f"Total disposal cost for the past {number_of_months} months": total_disposal_cost,
                    f"The average monthly disposal cost for the past {number_of_months} months": avg_disposal_cost,
                    f"The average daily disposal cost for the past {number_of_months} months": avg_daily_disposal_cost,
                }
            else:
                financials = {
                    f"Total disposal cost for the past {round(number_of_months / 12, 2)} years": total_disposal_cost,
                    f"The average monthly disposal cost for the past {round(number_of_months / 12, 2)} years": avg_disposal_cost,
                    f"The average daily disposal cost for the past {round(number_of_months / 12, 2)} years": avg_daily_disposal_cost,
                }
            display_financials("Disposal", financials)

        else:
            messagebox.showwarning("No Results", "Please choose a valid option.")

    except Exception as e:
        print(f"An error occurred: {e}")

# ========================================================================== #
# ============================== Display Chart ============================= #
# ========================================================================== #
def plot_pie_chart(title, labels, sizes):
    """
    Helper function to plot a pie chart.
    
    Parameters:
    title (str): The title of the pie chart.
    labels (list): The labels for the pie chart.
    sizes (list): The sizes for the pie chart.
    
    Returns:
    None
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(sizes, labels=labels, autopct='%.1f%%')
    ax.set_title(title, fontsize=18)
    ax.axis('equal')
    plt.show()


def plot_bar_chart(title, labels, values):
    """
    Helper function to plot a bar chart.
    
    Parameters:
    title (str): The title of the bar chart.
    labels (list): The labels for the bar chart.
    values (list): The values for the bar chart.
    
    Returns:
    None
    """
    # Show only the past 13 months
    labels = labels[-13:]
    values = values[-13:]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(labels, values)
    ax.set_title(title, fontsize=18)
    ax.set_xlabel('Month')
    ax.set_ylabel('Values')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Add horizontal gridlines
    ax.grid(axis='y', linewidth=0.25)

    # Add mplcursors tooltips
    cursor = mplcursors.cursor(bars, hover=True)
    cursor.connect("add", lambda sel: sel.annotation.set_text(f'{labels[sel.index]}: {values[sel.index]:,.2f}'))

    plt.show()


def display_chart():
    """
    Displays various charts based on the selected option.

    The function retrieves the selected option from the 'options' object and
    displays a corresponding chart using matplotlib. If an invalid
    option is selected, a warning message is displayed. The available options and
    their respective charts are:

    - 'Monthly': Displays a pie chart of monthly expenses including Payroll, 
       Expenses, and Average Fuel Cost.
    - 'Yearly': Displays a pie chart of yearly expenses including Payroll, Expenses,
       and Average Fuel Cost.
    - 'Trucks': Displays a pie chart of truck values.
    - 'Dumpsters': Displays a bar chart of dumpster counts for the past 12 months.
    - 'Disposal': Displays a bar chart of disposal costs for the past 12 months.
    - 'Predictions': Predicts and plots data for various categories.

    Each chart is displayed in a new figure window with appropriate titles and
    labels. 
    """
    try:
        option = options.get()

        if option == 'Monthly':
            labels = ['Payroll', 'Expenses', 'Avg. Fuel Cost']
            sizes = [total_monthly_payroll, total_monthly_expenses, monthly_fuel_cost]
            plot_pie_chart("Monthly Expenses", labels, sizes)

        elif option == 'Yearly':
            labels = ['Payroll', 'Expenses', 'Avg. Fuel Cost']
            sizes = [total_payroll, total_yearly_expenses, total_avg_yearly_fuel_cost]
            plot_pie_chart("Yearly Expenses", labels, sizes)

        elif option == 'Trucks':
            labels = list(trucks.keys())
            values = list(trucks.values())
            plot_pie_chart("Truck Values", labels, values)

        elif option == 'Dumpsters':
            labels = list(monthly_dumpster_count.keys())
            values = list(monthly_dumpster_count.values())
            plot_bar_chart("Dumpster Counts for the Past 13 Months", labels, values)

        elif option == 'Disposal':
            labels = list(monthly_disposal_cost.keys())
            values = list(monthly_disposal_cost.values())
            plot_bar_chart("Disposal Costs for the Past 13 Months", labels, values)

        elif option == "Predictions":
            # Predict and plot for each dictionary
            predict_and_plot(monthly_dumpster_count, 'Monthly Dumpster Count')
            predict_and_plot(monthly_disposal_cost, 'Monthly Disposal Cost')

        else:
            messagebox.showwarning("No Results", 
                    "Sorry, we do not have a chart for that option to display.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

def create_tooltip(widget, text):
    """Creates tooltips for the tkinter launch_demo_window widgets"""
    Hovertip(widget, text, hover_delay=500)

# ========================================================================== #
# ============================== Tkinter GUI =============================== #
# ========================================================================== #
root = tk.Tk()
root.minsize(width=100, height=100)
root.title("Company Financials")
root.config(padx=25, pady=25)

num_months_entry = tk.Entry(root, width=10)
num_months_entry.grid(column=1, row=0, padx=5, pady=10)
num_months_label = tk.Label(text="Number of Months")
num_months_label.grid(column=2, row=0, padx=5, pady=10)
create_tooltip(num_months_label, "Enter the previous number of months you want\n"
               "to calculate and show results for 'Dumpsters' and 'Disposal'.\n"
               "Default is all months.")

options = ttk.Combobox(root, state="readonly", 
                           values=[
                               "Daily", 
                               "Monthly", 
                               "Yearly", 
                               "Trucks", 
                               "Dumpsters", 
                               "Disposal",
                               "Predictions",
                                ]
                            )

options.grid(column=1, row=1, padx=5, pady=10)
options_label = tk.Label(text="Options")
options_label.grid(column=2, row=1, padx=5, pady=10)

calculate_button = tk.Button(root, text="Calculate", command=calculate_financials)
calculate_button.grid(column=1, row=2, padx=5, pady=5)

chart_button = tk.Button(root, text="Display Chart", command=display_chart)
chart_button.grid(column=2, row=2, padx=5, pady=5)


root.mainloop()
