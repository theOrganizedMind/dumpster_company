 
def calculate_yearly_pay(hourly_rate, regular_hours, overtime_hours=0):
    """
    Calculate the total yearly pay based on hourly rate, regular hours, 
    and optional overtime hours.

    Args:
        hourly_rate (float or int): The hourly wage.
        regular_hours (int): Number of regular hours worked per week.
        overtime_hours (int, optional): Number of overtime hours worked per week. 
            Overtime is paid at 1.5 times the hourly rate. Defaults to 0.

    Returns:
        float: The total yearly pay including regular and overtime pay.
    """
    # Calculate regular pay
    regular_pay = hourly_rate * regular_hours * 52

    # Calculate overtime pay (1.5 times the hourly rate for overtime hours)
    overtime_pay = hourly_rate * 1.5 * overtime_hours * 52

    # Calculate total yearly pay
    total_pay = regular_pay + overtime_pay

    return total_pay

def calculate_monthly_pay(hourly_rate, regular_hours, overtime_hours=0):
    """
    Calculate the total monthly pay based on hourly rate, regular hours, 
    and optional overtime hours.

    Args:
        hourly_rate (float or int): The hourly wage.
        regular_hours (int): Number of regular hours worked per week.
        overtime_hours (int, optional): Number of overtime hours worked per week. 
            Overtime is paid at 1.5 times the hourly rate. Defaults to 0.

    Returns:
        float: The total monthly pay including regular and overtime pay.
    """
    regular_pay = hourly_rate * regular_hours * 4.33

    overtime_pay = hourly_rate * 1.5 * overtime_hours * 4.33

    total_pay = regular_pay + overtime_pay

    return total_pay

def calculate_daily_pay(hourly_rate, regular_hours, overtime_hours=0):
    """
    Calculate the total daily pay based on hourly rate, regular hours, 
    and optional overtime hours.

    Args:
        hourly_rate (float or int): The hourly wage.
        regular_hours (int): Number of regular hours worked per day.
        overtime_hours (int, optional): Number of overtime hours worked per day. 
            Overtime is paid at 1.5 times the hourly rate. Defaults to 0.

    Returns:
        float: The total daily pay including regular and overtime pay.
    """
    regular_pay = hourly_rate * regular_hours

    overtime_pay = hourly_rate * 1.5 * overtime_hours

    total_pay = regular_pay + overtime_pay

    return total_pay

# Define the hourly rate range
# hourly_rates = range(20, 38)
hourly_rates = range(int(input("Enter the starting wage amount: $")), 
                     int(input("Enter the ending wage amount: $")) + 1)

choice = input("Would you like to calculate (d)aily, (m)onthly, or (y)early pay? ").lower()

print('\n')
# Calculate and print yearly pay for each hourly rate
for rate in hourly_rates:
    if choice == 'y':
        pay_40_hours = calculate_yearly_pay(rate, 40)
        pay_50_hours = calculate_yearly_pay(rate, 40, 10)
        print(f"At ${rate} an hour, the yearly pay will be ${pay_40_hours:,.2f} at 40 hours "
            f"and ${pay_50_hours:,.2f} at 50 hours.")
    elif choice == 'm':
        pay_40_hours = calculate_monthly_pay(rate, 40)
        pay_50_hours = calculate_monthly_pay(rate, 40, 10)
        print(f"At ${rate} an hour, the monthly pay will be ${pay_40_hours:,.2f} at 40 hours "
            f"and ${pay_50_hours:,.2f} at 50 hours.")
    elif choice == 'd':
        pay_8_hours = calculate_daily_pay(rate, 8)
        pay_10_hours = calculate_daily_pay(rate, 8, 2)
        print(f"At ${rate} an hour, the daily pay will be ${pay_8_hours:,.2f} at 8 hours "
            f"and ${pay_10_hours:,.2f} at 10 hours.")
