import pyperclip
import os


short_ton = 2000
long_ton = 2240
calculating = True


def clear_screen():
    """Clears the screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


while calculating:
    print("Type 'exit' at any time to quit.\n")
    try:
        trash_or_recycling = input("Is this trash, recycling or long ton? (t/r/lt): ").lower()
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
        elif trash_or_recycling == 'exit':
            break
        else:
            print("Invalid input. Please enter 't' for trash, 'r' for recycling, "
                  "or 'lt' for long ton.")
            continue            
    except ValueError:
        print("Invalid input. Please enter a valid integer.")
        continue

