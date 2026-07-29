import statistics
import matplotlib.pyplot as plt
import matplotlib as mpl
import mplcursors
import pandas as pd
import tkinter as tk
from tkinter import messagebox, ttk
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np  
from prophet import Prophet
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
from idlelib.tooltip import Hovertip
import os
from datetime import datetime
from tkinter import filedialog

from expenses import monthly_expenses, quickbooks_monthly_expenses
import payroll
from trucks import trucks
from dumpster_count import monthly_dumpster_count
from disposal import monthly_disposal_cost
from revenue import revenue
from monthly_sales import monthly_sales

# ========================================================================== #
# ================================== INFO ================================== #
# ========================================================================== #
#
# ========================================================================== #
# ================================== TODO ================================== #
# ========================================================================== #
# TODO: 
# ========================================================================== #

NUM_MONTHS = 12
WORK_DAYS_IN_MONTH = 20
NUM_TRUCKS = 3
NUM_DRIVERS = 3
DAILY_WORK_HOURS = 8
PROFIT = 1.25
AVG_DAILY_FUEL_PER_TRUCK = 150

todays_date = datetime.now().strftime("%m%d%Y")

# ========================================================================== #
# ================================ Payroll ================================= #
# ========================================================================== #
total_payroll = round(sum(payroll.employees.values()))
total_monthly_payroll = round(total_payroll / NUM_MONTHS, 2)
daily_payroll = total_monthly_payroll / WORK_DAYS_IN_MONTH

overhead_payroll = payroll.employees.get("John Doe")

# ========================================================================== #
# ================================ Expenses ================================ #
# ========================================================================== #
total_monthly_expenses = round(sum(monthly_expenses.values()), 2)

total_monthly_overhead_payroll = round(overhead_payroll / NUM_MONTHS, 2)

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

daily_operating_cost_per_driver_plus_markup = round(daily_operating_cost_per_driver 
                                                    * PROFIT, 2)

total_daily_overhead_payroll = round(total_monthly_overhead_payroll 
                                     / WORK_DAYS_IN_MONTH, 2)

avg_daily_sales = round(sum(monthly_sales.values()) / len(monthly_sales) 
                        / WORK_DAYS_IN_MONTH, 2)

hourly_rate = round(daily_operating_cost_per_driver / DAILY_WORK_HOURS * PROFIT, 2)

# ========================================================================== #
# =========================== Machine Learning ============================= #
# ========================================================================== #
def predict_and_plot_with_matplot(data_dict, column_name, future_months=3):
    """
    Makes a prediction for the specified number of future months for 
    Quickbooks expenses, Dumpster count, and Disposal cost using the 
    Prophet model.
    
    Parameters:
    data_dict (dict): Dictionary containing historical data.
    column_name (str): Name of the column to be used in the plot.
    future_months (int): Number of future months to predict. Default is 3.
    
    Returns:
    None
    """
    # Prepare the data
    data = pd.DataFrame(list(data_dict.items()), columns=['ds', 'y'])
    data['ds'] = pd.to_datetime(data['ds'])

    # Filter the data to only include the last twelve months
    data = data.tail(12)

    # Initialize the Prophet model
    model = Prophet()
    model.fit(data)

    # Create a dataframe for future dates
    future = model.make_future_dataframe(periods=future_months, freq='ME')
    
    # Predict the future values
    forecast = model.predict(future)

    # Plot the results
    plt.figure(figsize=(10, 5))

    # Plot the previous data (last twelve months)
    plt.plot(data['ds'], data['y'], 'bo-', label='Previous Data')

    # Plot predicted data (next three months)
    plt.plot(forecast['ds'], forecast['yhat'], 'ro--', label="Predicted Data")

    # Add labels and title
    plt.xlabel('Month')
    plt.ylabel(column_name)
    plt.title(f"{column_name}, For Past 12 Months and Predicted Next {future_months} Months")
    
    # Format the x-axis labels
    plt.gca().xaxis.set_major_formatter(mpl.dates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mpl.dates.MonthLocator(interval=1))
    plt.gcf().autofmt_xdate()

    # Add legend
    plt.legend()

    # Implement mplcurors for interactive tooltips
    cursor = mplcursors.cursor(hover=True)
    cursor.connect("add", lambda sel: sel.annotation.set_text(f"{sel.target[1]:,.0f}"))

    # Adjust layout to prevent x-axis labels from going off bottom of the screen
    plt.tight_layout()

    # Show plot
    plt.show()

# ========================================================================== #
# ======================== Machine Learning using Plotly =================== #
# ========================================================================== #
def predict_and_plot_with_plotly(data_dicts, column_names, future_months=3):
    """
    Makes a prediction for the specified number of future months for 
    Quickbooks expenses, Dumpster count, and Disposal cost using the 
    Prophet model and plots the results using Plotly.
    
    Parameters:
    data_dicts (list of dict): List of dictionaries containing historical data.
    column_names (list of str): List of column names to be used in the plot.
    future_months (int): Number of future months to predict. Default is 3.
    
    Returns:
    fig: The Plotly figure object.
    """
    fig = make_subplots(rows=4, cols=1, shared_xaxes=False, 
                        vertical_spacing=0.1, subplot_titles=column_names)
    
    for i, (data_dict, column_name) in enumerate(zip(data_dicts, column_names), 
                                                 start=1):
        # Prepare the data
        data = pd.DataFrame(list(data_dict.items()), columns=['ds', 'y'])
        data['ds'] = pd.to_datetime(data['ds'])

        # Initialize the Prophet model
        model = Prophet()
        model.fit(data)

        # Create a dataframe for future dates
        future = model.make_future_dataframe(periods=future_months, freq='ME')
        
        # Predict the future values
        forecast = model.predict(future)

        # Add previous data to the subplot
        fig.add_trace(go.Scatter(
            x=data['ds'], 
            y=data['y'], 
            mode='lines+markers', 
            name=f'Previous Data - {column_name}',
            hovertemplate='%{x|%Y-%m}: %{y:,.2f}'  # Format tooltips
        ), row=i, col=1)

        # Add predicted data to the subplot
        fig.add_trace(go.Scatter(
            x=forecast['ds'], 
            y=forecast['yhat'], 
            mode='lines+markers', 
            name=f'Predicted Data - {column_name}',
            line=dict(dash='dashdot'),
            hovertemplate='%{x|%Y-%m}: %{y:,.2f}'  # Format tooltips
        ), row=i, col=1)
        
    # Update layout
    fig.update_layout(height=1200, width=2000, 
                      title_text="Predictions for Monthly Sales, "
                      "Quickbooks Monthly Expenses, "
                      "Monthly Dumpster Count, and Monthly Disposal Cost",
                      title_x=0.5,)
    fig.update_xaxes(title_text="Month", tickformat='%Y-%m')
    fig.update_yaxes(title_text="Values")

    # Ask the user if they want to save the predictions to an Excel file.
    save_to_excel = messagebox.askyesno("Save Predictions",
                                        "Would you like to save the predictions to an Excel file?")
    if save_to_excel:
        # Get the user's Downloads folder
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        file_path = os.path.join(downloads_folder, f"predictions_({todays_date}).xlsx")
        
        # Create a DataFrame to store all predictions
        combined_predictions = pd.DataFrame()

        # Create a dictionary to store historical and predicted data
        historical_data = pd.DataFrame()
        predicted_data = pd.DataFrame()

        for data_dict, column_name in zip(data_dicts, column_names):
            historical = pd.DataFrame(list(data_dict.items()), columns=['Date', column_name])
            historical['Date'] = pd.to_datetime(historical['Date']).dt.date

            # Add the historical data to the historical_data DataFrame
            if historical_data.empty:
                historical_data['Date'] = historical['Date']
            historical_data[column_name] = historical[column_name]

            # Prepare the data for Prophet
            data = pd.DataFrame(list(data_dict.items()), columns=['ds', 'y'])
            data['ds'] = pd.to_datetime(data['ds'])

            # Initialize the Prophet model
            model = Prophet()
            model.fit(data)

            # Create a dataframe for future dates
            future = model.make_future_dataframe(periods=future_months, freq='ME')
            
            # Predict the future values
            forecast = model.predict(future)

            predicted = forecast[forecast['ds'] > data['ds'].max()]
            if predicted_data.empty:
                predicted_data['Date'] = predicted['ds'].dt.date
            predicted_data[column_name] = predicted['yhat'].values

        # Save the historical and predicted data to an Excel file
        with pd.ExcelWriter(file_path) as writer:
            # Round historical data to two decimal places
            historical_data = historical_data.round(2)
            historical_data.to_excel(writer, sheet_name="Historical Data", index=False)

            # Round predicted data to two decimal places
            predicted_data = predicted_data.round(2)
            predicted_data.to_excel(writer, sheet_name="Predicted Data", index=False)

        # Notify the user
        messagebox.showinfo("File Saved", f"Predictions saved to {file_path}")

    # Show plot
    fig.show()

    return fig

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
                f"Daily Operating Cost per Driver plus {PROFIT}% Markup": 
                daily_operating_cost_per_driver_plus_markup,
                "Daily Overhead Payroll": total_daily_overhead_payroll,
                "Rate per Hour": hourly_rate,
                "Average Daily Sales": avg_daily_sales,
            }
            display_financials("Daily", financials)

        elif option == "Monthly":
            financials = {
                "Total monthly payroll": total_monthly_payroll,
                "Total monthly expenses": total_monthly_expenses,
                "Total monthly operating cost": monthly_operating_cost,
                "Total monthly overhead payroll": total_monthly_overhead_payroll,
                "Average monthly fuel cost": monthly_fuel_cost
            }
            display_financials("Monthly", financials)

        elif option == "Yearly":
            financials = {
                "Total yearly payroll": total_payroll,
                "Total yearly expenses": total_yearly_expenses,
                "Total average yearly fuel cost": total_avg_yearly_fuel_cost,
            }
            display_financials("Yearly", financials)

        elif option == "Sales":
            selected_months = list(monthly_sales.keys())[-number_of_months:]
            selected_values = list(monthly_sales.values())[-number_of_months:]
            total_sales = sum(selected_values)
            avg_sales_per_month = round(statistics.mean(selected_values))
            avg_sales_per_day = round(avg_sales_per_month / WORK_DAYS_IN_MONTH)
            avg_sales_day_per_driver = avg_sales_per_day / NUM_DRIVERS
            max_sales = max(monthly_sales.values())
            max_sales_month = max(monthly_sales, key=monthly_sales.get)
            avg_monthly_sales = round(sum(monthly_sales.values()) / len(monthly_sales), 2)
            avg_yearly_sales = avg_monthly_sales * NUM_MONTHS
            if 12 >= number_of_months:
                financials = {
                    f"The average daily sales in the past {number_of_months} months": avg_sales_per_day,
                    f"The average monthly sales in the past {number_of_months} months": avg_sales_per_month,
                    f"The total sales in the past {number_of_months} months": total_sales,
                    f"Max sales month {max_sales_month}": max_sales,                }
            else:
                financials = {
                    f"The average daily sales in the past {round(number_of_months / 12, 2)} years": avg_sales_per_day,
                    f"The average monthly sales in the past {round(number_of_months / 12, 2)} years": avg_sales_per_month,
                    f"The average yearly sales in the past {round(number_of_months / 12, 2)} years": avg_yearly_sales,
                    f"The total sales in the past {round(number_of_months / 12, 2)} years": total_sales,
                    f"Max sales month {max_sales_month}": max_sales,
                }
            display_financials("Sales", financials)
        
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
            avg_dumpsters_day = round(avg_dumpsters_month / WORK_DAYS_IN_MONTH)
            avg_dumpsters_day_per_driver = avg_dumpsters_day / NUM_DRIVERS
            avg_cost_per_dumpster = round(daily_operating_cost / avg_dumpsters_day, 2)
            max_dumpsters = max(monthly_dumpster_count.values())
            max_dumpsters_month = max(monthly_dumpster_count, 
                                       key=monthly_dumpster_count.get)
            rate_per_dumpster = round(monthly_operating_cost / avg_dumpsters_month)
            rate_per_dumpster_with_markup = round(rate_per_dumpster * PROFIT)
            if 12 >= number_of_months:
                financials = {
                    f"Total number of dumpsters ran in the past {number_of_months} months": total_num_dumpsters,
                    f"The average number of dumpster runs per month in the past {number_of_months} months": avg_dumpsters_month,
                    f"The average number of dumpster runs per day in the past {number_of_months} months": avg_dumpsters_day,
                    f"The average number of dumpster runs per day per driver in the past {number_of_months} months": avg_dumpsters_day_per_driver,
                    f"The average daily cost per dumpster in the past {number_of_months} months": avg_cost_per_dumpster,
                    f"Estimated net income per dumpster in the past {number_of_months} months should be": rate_per_dumpster,
                    f"Estimated net income per dumpster in the past {number_of_months} months with {PROFIT}% markup should be": rate_per_dumpster_with_markup,
                }
            else:
                financials = {
                    f"Total number of dumpsters ran in the past {round(number_of_months / 12, 2)} years": total_num_dumpsters,
                    f"The average number of dumpster runs per month in the past {round(number_of_months / 12, 2)} years": avg_dumpsters_month,
                    f"The average number of dumpster runs per day in the past {round(number_of_months / 12, 2)} years": avg_dumpsters_day,
                    f"The average number of dumpster runs per day per driver in the past {round(number_of_months / 12, 2)} years": avg_dumpsters_day_per_driver,
                    f"The average daily cost per dumpster in the past {round(number_of_months / 12, 2)} years": avg_cost_per_dumpster,
                    f"Estimated net income per dumpster in the past {round(number_of_months / 12, 2)} years should be": rate_per_dumpster,
                    f"Estimated net income per dumpster in the past {round(number_of_months / 12, 2)} years with {PROFIT}% markup should be": rate_per_dumpster_with_markup,
                    f"Max dumpster month {max_dumpsters_month}": max_dumpsters,
                }
            display_financials("Dumpsters", financials)

        elif option == "Disposal":
            # Calculate results based on the number of months
            selected_months = list(monthly_disposal_cost.keys())[-number_of_months:]
            selected_values = list(monthly_disposal_cost.values())[-number_of_months:]
            total_disposal_cost = sum(selected_values)
            avg_disposal_cost = round(statistics.mean(selected_values))
            avg_daily_disposal_cost = round(avg_disposal_cost / WORK_DAYS_IN_MONTH)
            max_disposal_cost = max(monthly_disposal_cost.values())
            max_disposal_month = max(monthly_disposal_cost, key=monthly_disposal_cost.get)            
            if 12 >= number_of_months:
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
                    f"Max disposal month {max_disposal_month}": max_disposal_cost,
                }
            display_financials("Disposal", financials)

        elif option == "Revenue":
            total_revenue = sum([year_data["revenue"] for year_data in revenue.values()])
            total_net_profit = sum([year_data["net profit"] for year_data in revenue.values()])
            num_employees = len(payroll.employees.keys())
            num_years = len(revenue)
            avg_revenue = round(total_revenue / num_years, 2)
            avg_net_profit = round(total_net_profit / num_years, 2)
            avg_net_profit_per_employee = round(avg_net_profit / num_employees, 2) if num_employees != 0 else 0
            avg_profit_margin = round(avg_net_profit / avg_revenue, 2) if avg_revenue != 0 else 0
            avg_revenue_per_employee = round(avg_revenue / num_employees, 2) if num_employees != 0 else 0
            print('\n')
            for key, values in revenue.items():
                print(f"{key.center(20, '-')}")
                print(f"Revenue: {values['revenue']:,.2f}")
                print(f"Net profit: {values['net profit']:,.2f}")
                print(f"Profit margin: {values['net profit'] / values['revenue']:,.2%}")

            financials = {
                "Total revenue": total_revenue,
                "Total net profit": total_net_profit,
                "Average revenue per year": avg_revenue,                
                "Average revenue per employee": avg_revenue_per_employee,
                "Average net profit": avg_net_profit,
                "Average net profit per employee": avg_net_profit_per_employee,
                "Average profit margin": avg_profit_margin,
            }
            display_financials("Revenue", financials)

        elif option == "Quickbooks":
            # Calculate results based on the number of months
            selected_months = list(quickbooks_monthly_expenses.keys())[-number_of_months:]
            selected_values = list(quickbooks_monthly_expenses.values())[-number_of_months:]
            total_qb_monthly_expenses = round(sum(selected_values), 2)
            avg_qb_monthly_expenses = round(statistics.mean(selected_values), 2)
            if 12 >= number_of_months:
                financials = {
                    f"Total quickbooks monthly expenses for the past "
                    f"{number_of_months} months": total_qb_monthly_expenses,
                    f"Average quickbooks monthly expense for the past "
                    f"{number_of_months} months": avg_qb_monthly_expenses,
                }
            else:
                financials = {
                    f"Total quickbooks monthly expenses for the past "
                    f"{round(number_of_months / 12, 2)} years": total_qb_monthly_expenses,
                    f"Average quickbooks monthly expense for the past "
                    f"{round(number_of_months / 12, 2)} years": avg_qb_monthly_expenses,
                }
            display_financials("Quickbooks", financials)

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


def plot_bar_chart(title, labels, values, number_of_months=13):
    """
    Helper function to plot a bar chart.
    
    Parameters:
    title (str): The title of the bar chart.
    labels (list): The labels for the bar chart.
    values (list): The values for the bar chart.
    
    Returns:
    None
    """
    # Show only the past number of months
    labels = labels[-number_of_months:]
    values = values[-number_of_months:]

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


def plot_line_chart(title, x, y1, y2, label1, label2):
    """
    Helper function to plot a line chart with two lines.
    
    Parameters:
    title (str): The title of the line chart.
    x (list): The x-axis values for the line chart.
    y1 (list): The y-axis values for the first line.
    y2 (list): The y-axis values for the second line.
    label1 (str): The label for the first line.
    label2 (str): The label for the second line.
    
    Returns:
    None
    """
    # Calculate the percent profit
    percent_profit = [(net / rev) * 100 if rev != 0 else 0 for net, rev in zip(y2, y1)]

    # Round the values to the nearest two digits
    y1 = [round(value, 2) for value in y1]
    y2 = [round(value, 2) for value in y2]
    percent_profit = [round(value, 2) for value in percent_profit]

    # Format the 'Revenue' and 'Net Profit' values
    y1_formatted = [f'{value:,.2f}' for value in y1]
    y2_formatted = [f'{value:,.2f}' for value in y2]
    percent_profit_formatted = [f'{value:.2f}%' for value in percent_profit]

    fig, ax = plt.subplots(figsize=(10, 5))
    line1, = ax.plot(x, y1, 'o-', label=label1)
    line2, = ax.plot(x, y2, 'o-', label=label2)
    ax.set_title(title, fontsize=18)
    ax.set_ylabel('Values')
    ax.grid(axis='y', linewidth=0.25)
    plt.legend()
    plt.tight_layout()

    # Add mplcursors tooltips
    cursor1 = mplcursors.cursor(line1, hover=True)
    cursor1.connect("add", lambda sel: sel.annotation.set_text(f'{x[int(sel.index)]}: {y1[int(sel.index)]:,.2f}'))

    cursor2 = mplcursors.cursor(line2, hover=True)
    cursor2.connect("add", lambda sel: sel.annotation.set_text(
        f'{x[int(sel.index)]}: {y2[int(sel.index)]:,.2f}\nPercent Profit: {percent_profit[int(sel.index)]:.2f}%'))

    # Create a table at the bottom of the plot
    table_data = {
        'Year': x,
        'Revenue': y1_formatted,
        'Net Profit': y2_formatted,
        'Percent Profit (%)': percent_profit_formatted
    }
    table_df = pd.DataFrame(table_data)
    table_df = table_df.set_index('Year').transpose()
    table = plt.table(cellText=table_df.values,
                      rowLabels=table_df.index,
                      colLabels=table_df.columns,
                      cellLoc='center',
                      loc='bottom',
                      bbox=[0, -0.3, 1, 0.2])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)

    plt.subplots_adjust(left=0.1, bottom=0.3)
    plt.tight_layout()

    plt.show()

def plot_sales_vs_expenses(number_of_months=13):
    """
    Plots a grouped bar chart for Monthly Sales vs Quickbooks Expenses.
    Shows only the last `number_of_months` months.
    """
    # Combine and sort all months
    all_months = sorted(set(monthly_sales.keys()) | set(quickbooks_monthly_expenses.keys()))
    sales = [monthly_sales.get(m, 0) for m in all_months]
    expenses = [quickbooks_monthly_expenses.get(m, 0) for m in all_months]

    # Show only the last number_of_months
    all_months = all_months[-number_of_months:]
    sales = sales[-number_of_months:]
    expenses = expenses[-number_of_months:]

    x = np.arange(len(all_months))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5))
    bars_sales = ax.bar(x - width/2, sales, width, label='Monthly Sales')
    bars_expenses = ax.bar(x + width/2, expenses, width, label='Quickbooks Expenses')

    ax.set_title(f'Monthly Sales vs Quickbooks Expenses in the past {number_of_months} months'
                 , fontsize=18)
    ax.set_xlabel('Month')
    ax.set_ylabel('Values')
    ax.set_xticks(x)
    ax.set_xticklabels(all_months, rotation=45)
    ax.legend()
    ax.grid(axis='y', linewidth=0.25)
    plt.tight_layout()

    # Add mplcursors tooltips
    cursor_sales = mplcursors.cursor(bars_sales, hover=True)
    cursor_sales.connect("add", lambda sel: sel.annotation.set_text(f'{all_months[sel.index]} Sales: {sales[sel.index]:,.2f}'))
    cursor_expenses = mplcursors.cursor(bars_expenses, hover=True)
    cursor_expenses.connect("add", lambda sel: sel.annotation.set_text(f'{all_months[sel.index]} Expenses: {expenses[sel.index]:,.2f}'))

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
    - 'Quickbooks': Displays a bar chart of Quickbooks expenses for the past 12 months.
    - 'Predictions': Predicts and plots data for various categories.

    Each chart is displayed in a new figure window with appropriate titles and
    labels. 
    """
    try:
        option = options.get()
        number_of_months = num_months_entry.get()

        # Only require number_of_months for bar charts
        bar_chart_options = ['Sales', 'Dumpsters', 'Disposal', 'Quickbooks', 
                             'Sales vs Expenses(Matplot)']
        if option in bar_chart_options:
            if not number_of_months.strip():
                messagebox.showwarning(
                    "Input Required",
                    "Please enter the number of months before displaying a chart for this option."
                )
                return
            number_of_months_int = int(number_of_months)
        else:
            number_of_months_int = None

        if option == 'Monthly':
            labels = ['Payroll', 'Expenses', 'Avg. Fuel Cost']
            sizes = [total_monthly_payroll, total_monthly_expenses, 
                     monthly_fuel_cost]
            plot_pie_chart("Monthly Expenses", labels, sizes)

        elif option == 'Yearly':
            labels = ['Payroll', 'Expenses', 'Avg. Fuel Cost']
            sizes = [total_payroll, total_yearly_expenses, 
                     total_avg_yearly_fuel_cost]
            plot_pie_chart("Yearly Expenses", labels, sizes)

        elif option == 'Sales':
            labels = list(monthly_sales.keys())
            values = list(monthly_sales.values())
            plot_bar_chart(f"Monthly Sales for the Past {number_of_months} Months", 
                           labels, values, number_of_months_int)

        elif option == 'Trucks':
            labels = list(trucks.keys())
            values = list(trucks.values())
            plot_pie_chart("Truck Values", labels, values)

        elif option == 'Dumpsters':
            labels = list(monthly_dumpster_count.keys())
            values = list(monthly_dumpster_count.values())
            plot_bar_chart(f"Dumpster Counts for the Past {number_of_months} Months", 
                           labels, values, number_of_months_int)

        elif option == 'Disposal':
            labels = list(monthly_disposal_cost.keys())
            values = list(monthly_disposal_cost.values())
            plot_bar_chart(f"Disposal Costs for the Past {number_of_months} Months", 
                           labels, values, number_of_months_int)

        elif option == 'Revenue':
            labels = list(revenue.keys())
            total_revenue = [revenue[year]["revenue"] for year in revenue]
            net_profit = [revenue[year]["net profit"] for year in revenue]
            plot_line_chart("Revenue and Net Profit by Year", labels, 
                            total_revenue, net_profit, "Total Revenue", 
                            "Net Profit")

        elif option == 'Quickbooks':
            labels = list(quickbooks_monthly_expenses.keys())
            values = list(quickbooks_monthly_expenses.values())
            plot_bar_chart(f"Quickbooks Expenses for the Past {number_of_months} Months", 
                           labels, values, number_of_months_int)

        elif option == 'Predictions(Matplot)':
            # Predict and plot for each dictionary
            predict_and_plot_with_matplot(quickbooks_monthly_expenses, 
                                          'Quickbooks Monthly Expenses')
            predict_and_plot_with_matplot(monthly_dumpster_count, 
                                          'Monthly Dumpster Count')
            predict_and_plot_with_matplot(monthly_disposal_cost, 
                                          'Monthly Disposal Cost')

        elif option == 'Predictions(Plotly)':
            data_dicts = [monthly_sales, quickbooks_monthly_expenses, monthly_dumpster_count, 
                          monthly_disposal_cost]
            column_names = ['Monthly Sales',
                            'Quickbooks Monthly Expenses', 
                            'Monthly Dumpster Count', 
                            'Monthly Disposal Cost']
            
            predict_and_plot_with_plotly(data_dicts, column_names, 12)

        elif option == 'Sales vs Expenses(Matplot)':
            plot_sales_vs_expenses(number_of_months_int)

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
if __name__ == "__main__":
    root = tk.Tk()
    root.minsize(width=100, height=100)
    root.title("Dumpster Company Financials")
    root.config(padx=25, pady=25)

    num_months_entry = tk.Entry(root, width=10)
    num_months_entry.grid(column=1, row=0, padx=5, pady=10)
    num_months_label = tk.Label(text="Number of Months")
    num_months_label.grid(column=2, row=0, padx=5, pady=10)
    create_tooltip(num_months_label, "Enter the previous number of months you want\n"
                                    "to calculate and show results for\n"
                                    "'Sales', 'Dumpsters', 'Disposal' and 'Quickbooks.")

    options = ttk.Combobox(root, width=25, state="readonly", 
                            values=[
                                "Daily", 
                                "Monthly", 
                                "Yearly",
                                "Sales", 
                                "Trucks", 
                                "Dumpsters", 
                                "Disposal",
                                "Revenue",
                                "Quickbooks",
                                "Predictions(Matplot)",
                                "Sales vs Expenses(Matplot)",
                                "Predictions(Plotly)",
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
