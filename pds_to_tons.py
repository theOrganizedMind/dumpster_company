import pyperclip
import os
import time


short_ton = 2000
long_ton = 2240
calculating = True
leed_disposal_price = 98


def clear_screen():
    """Clears the screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


while calculating:
    print("Type 'exit' at any time to quit.\n")
    try:
        trash_or_recycling = input("Is this trash, recycling, long ton or leed? (t/r/lt/leed): ").lower()
        if trash_or_recycling == 'r':
            clear_screen()
            gross_tons = float(input("What is the recycling gross weight in tons?: "))
            pyperclip.copy(gross_tons)
            print(f"{gross_tons} tons have been copied to the clipboard.")
        elif trash_or_recycling == 'lt':
            clear_screen()
            pounds = int(input("What is the recycling net weight in pounds?: "))
            tons = round(pounds / long_ton, 2)
            pyperclip.copy(tons)
            print(f"{tons} long tons have been copied to the clipboard.")
        elif trash_or_recycling == 't':
            clear_screen()
            pounds = int(input("What is the trash weight in pounds?: "))
            tons = round(pounds / short_ton, 2)
            pyperclip.copy(tons)
            print(f"{tons} tons have been copied to the clipboard.")
            disposal_cost = float(input("What is the disposal cost: $"))
            pyperclip.copy(disposal_cost)
            print(f"${disposal_cost} disposal cost has been copied to the clipboard.")
        elif trash_or_recycling == 'leed':
            clear_screen()
            pounds = int(input("What is the trash weight in pounds?: "))
            tons = round(pounds / short_ton, 2)
            pyperclip.copy(tons)
            print(f"{tons} tons have been copied to the clipboard.")
            time.sleep(1) # Sleep for 1 second to allow for copy of tons
            # disposal_cost = float(input("What is the disposal cost: $"))
            disposal_cost = round(tons * leed_disposal_price, 2)
            pyperclip.copy(disposal_cost)
            print(f"${disposal_cost} disposal cost has been copied to the clipboard.")
            time.sleep(1) # Sleep for 1 second to allow for copy of disposal_cost
            if tons <= 8:
                leed_pricing = round((tons * 20) + 750)
            elif tons > 8:
                weight_overage = tons - 8
                weight_overage_fee = (weight_overage * 100)
                leed_pricing = round((tons * 20) + weight_overage_fee + 750)
            pyperclip.copy(leed_pricing)
            print(f"{leed_pricing} LEED pricing has been copied to the clipboard.")
        elif trash_or_recycling == 'exit':
            break
        else:
            print("Invalid input. Please enter 't' for trash, 'r' for recycling, "
                  "or 'lt' for long ton.")
            continue            
    except ValueError:
        print("Invalid input. Please enter a valid integer.")
        continue
