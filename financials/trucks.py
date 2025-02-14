trucks = {
    "Truck 1": 42641.90,
    "Truck 2": 30238.00,
    "Truck 3": 33070.00,
    }

if __name__ == "__main__":
    truck_total = (sum(trucks.values()))
    print(f"The total sum of all trucks = ${truck_total:,.2f}")
