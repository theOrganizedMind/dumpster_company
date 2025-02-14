monthly_disposal_cost = {
    "Jan_23": 28746.96, "Feb_23": 75139.33, "Mar_23": 9609.84, "Apr_23": 7841.84, 
    "May_23": 22373.33, "Jun_23": 89105.77, "Jul_23": 47241.33, "Aug_23": 96054.70, 
    "Sep_23": 118583.62, "Oct_23": 59554.24, "Nov_23": 56924.12, "Dec_23": 76883.61,
    "Jan_24": 111019.29,
}

if __name__ == "__main__":
    total_disposal = (sum(monthly_disposal_cost.values()))
    print(f"Total disposal cost = ${total_disposal:,.2f}")
    num_months = len(monthly_disposal_cost)
    print(f"Number of months: {num_months}")
    avg_disposal_cost = round(total_disposal / num_months, 2)
    print(f"Average monthly disposal cost = ${avg_disposal_cost:,.2f}")
