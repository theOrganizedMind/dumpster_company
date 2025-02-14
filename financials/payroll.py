employees = {
    "John Doe": 50000,
    "Jane Smith": 60000,
    "Alice Johnson": 55000,
    "Bob Brown": 58000,
    "Carol White": 62000,
    "David Black": 61000,
}

if __name__ == "__main__":
    total_yearly_payroll = (sum(employees.values()))
    print(f"Total yearly payroll = ${total_yearly_payroll:,.2f}")
    total_monthly_payroll = (sum(employees.values()) / 12)
    print(f"Total monthly payroll = ${total_monthly_payroll:,.2f}")
    total_weekly_payroll = (sum(employees.values()) / 52)
    print(f"Total weekly payroll = ${total_weekly_payroll:,.2f}")
    total_num_employees = len(employees)
    print(f"Total number of employees: {total_num_employees}")