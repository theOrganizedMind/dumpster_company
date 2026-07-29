import pyperclip
import os
import json
import subprocess
import time
import tkinter as tk
from tkinter import messagebox, ttk
from idlelib.tooltip import Hovertip

# ========================================================================== #
# ================================ INFO ==================================== #
# ========================================================================== #
# - 
# =========================================================================== #
# ================================= TODO ==================================== #
# =========================================================================== #
# TODO: 
# =========================================================================== #


CONFIG_FILE = os.path.join(os.path.dirname(__file__), "pds_to_tons_config.json")

def create_tooltip(widget, text):
    """Creates tooltips for the tkinter widgets"""
    Hovertip(widget, text, hover_delay=500)

def load_config():
    """Load ton settings from config file only and validate required keys."""
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")

    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        loaded_config = json.load(file)

    if not isinstance(loaded_config, dict):
        raise TypeError("Config must be a JSON object with 'short_ton' and 'long_ton'.")

    if "short_ton" not in loaded_config or "long_ton" not in loaded_config \
        or "customer_trash_pricing" not in loaded_config \
        or "leed_disposal_cost" not in loaded_config \
        or "leed_disposal_markup" not in loaded_config:
        raise KeyError("Config must include both 'short_ton' and 'long_ton'.")

    return {
        "short_ton": int(loaded_config["short_ton"]),
        "long_ton": int(loaded_config["long_ton"]),
        "customer_trash_pricing": int(loaded_config["customer_trash_pricing"]),
        "leed_disposal_cost": int(loaded_config["leed_disposal_cost"]),
        "leed_disposal_markup": int(loaded_config["leed_disposal_markup"])
    }

try:
    config_values = load_config()
    short_ton = config_values["short_ton"]
    long_ton = config_values["long_ton"]
    customer_trash_pricing = config_values["customer_trash_pricing"]
    leed_disposal_cost = config_values["leed_disposal_cost"]
    leed_disposal_markup = config_values["leed_disposal_markup"]
except Exception as error:
    messagebox.showerror("Config Error", f"Could not load config file.\n\nDetails: {error}")
    raise SystemExit(1)


def clear_screen():
    """Clears the screen."""
    command = 'cls' if os.name == 'nt' else 'clear'
    subprocess.run(command, shell=True, check=False)
    

def calculate_and_copy():
    """Calculate tonnage/pricing by selected type and copy results to clipboard.

    Reads values from the Tkinter form, performs the calculation for the chosen
    option (Recycling, Long Ton, Trash, or LEED), and copies one or more results
    to the clipboard in sequence. For Trash, disposal cost is copied after tons;
    for LEED, disposal cost and LEED pricing are derived from tons.
    """
    try:
        option = type_options.get()
        pds_to_tons = int(pds_to_tons_entry.get())
        disposal_cost_text = disposal_cost_entry.get().strip()
        disposal_cost = float(disposal_cost_text) if disposal_cost_text else None

        if option == 'Recycling':
            clear_screen()
            pyperclip.copy(pds_to_tons)
            print(f"{pds_to_tons} tons have been copied to the clipboard.")
        elif option == 'Long Ton':
            clear_screen()
            tons = round(pds_to_tons / long_ton, 2)
            pyperclip.copy(tons)
            print(f"{tons} long tons have been copied to the clipboard.")
        elif option == 'Trash':
            clear_screen()
            tons = round(pds_to_tons / short_ton, 2)
            pyperclip.copy(tons)
            print(f"{tons} tons have been copied to the clipboard.")
            time.sleep(1)
            pyperclip.copy(disposal_cost)
            print(f"${disposal_cost} disposal cost has been copied to the clipboard.")
        elif option == 'LEED':
            clear_screen()
            tons = round(pds_to_tons / short_ton, 2)
            pyperclip.copy(tons)
            print(f"{tons} tons have been copied to the clipboard.")
            time.sleep(1) # Sleep for 1 second to allow for copy of tons
            disposal_cost = round(tons * leed_disposal_cost, 2)
            pyperclip.copy(disposal_cost)
            print(f"${disposal_cost} disposal cost has been copied to the clipboard.")
            time.sleep(1) # Sleep for 1 second to allow for copy of disposal_cost
            if tons <= 5:
                leed_pricing = round((tons * leed_disposal_markup) 
                                     + customer_trash_pricing)
            elif tons > 5:
                weight_overage = tons - 5
                weight_overage_fee = (weight_overage * 100)
                leed_pricing = round((tons * leed_disposal_markup) 
                                     + weight_overage_fee + customer_trash_pricing)
            pyperclip.copy(leed_pricing)
            print(f"{leed_pricing} LEED pricing has been copied to the clipboard.")
        else:
            messagebox.showwarning("No Results", "Please choose a valid option.")

    except Exception as e:
        print(f"An error occurred: {e}")


def open_config_editor():
    """Open a separate text editor window for the JSON config."""
    editor = tk.Toplevel(root)
    editor.title("Edit pds_to_tons Config")
    editor.minsize(width=420, height=260)
    editor.config(padx=10, pady=10)

    text_widget = tk.Text(editor, wrap="none", width=50, height=12, 
                          font=("Times New Roman", 12))
    text_widget.grid(column=0, row=0, padx=5, pady=5)

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            current_config = json.load(file)
        if not isinstance(current_config, dict):
            raise ValueError("Config must be a JSON object.")
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        messagebox.showerror(
            "Config Error",
            "The config file is invalid. Please fix and reopen the editor."
        )
        editor.destroy()
        return

    text_widget.insert("1.0", json.dumps(current_config, indent=4))

    def save_config_from_editor():
        global short_ton, long_ton

        raw_text = text_widget.get("1.0", tk.END).strip()
        try:
            updated_config = json.loads(raw_text)
            updated_short_ton = int(updated_config["short_ton"])
            updated_long_ton = int(updated_config["long_ton"])
            updated_customer_trash_pricing = int(updated_config["customer_trash_pricing"])
            updated_leed_disposal_cost = int(updated_config["leed_disposal_cost"])
            updated_leed_disposal_markup = int(updated_config["leed_disposal_markup"])

            clean_config = {
                "short_ton": updated_short_ton,
                "long_ton": updated_long_ton,
                "customer_trash_pricing": updated_customer_trash_pricing, 
                "leed_disposal_cost": updated_leed_disposal_cost, 
                "leed_disposal_markup": updated_leed_disposal_markup,
            }

            with open(CONFIG_FILE, "w", encoding="utf-8") as file:
                json.dump(clean_config, file, indent=4)

            short_ton = updated_short_ton
            long_ton = updated_long_ton
            customer_trash_pricing = updated_customer_trash_pricing
            leed_disposal_cost = updated_leed_disposal_cost
            leed_disposal_markup =updated_leed_disposal_markup

            messagebox.showinfo("Config Saved", "Config updated successfully.")
            editor.destroy()
        except KeyError:
            messagebox.showerror(
                "Invalid Config",
                "Config must include both 'short_ton' and 'long_ton' keys."
            )
        except (ValueError, TypeError):
            messagebox.showerror(
                "Invalid Values",
                "Both 'short_ton' and 'long_ton' must be valid numbers."
            )
        except json.JSONDecodeError as error:
            messagebox.showerror("Invalid JSON", f"Could not parse JSON.\n\nDetails: {error}")

    save_button = tk.Button(editor, text="Save", width=12, command=save_config_from_editor)
    save_button.grid(column=0, row=1, pady=8)


if __name__ == "__main__":
    root = tk.Tk()
    root.minsize(width=300, height=100)
    root.title("Pds to Tons")
    root.config(padx=20, pady=20)

    type_label = tk.Label(root, text="Enter Type:")
    type_label.grid(column=0, row=0, padx=5, pady=5)
    type_options = ttk.Combobox(root, width=15, state="readonly",
                           values=[
                               "Trash",
                               "Recycling",
                               "Long Ton",
                               "LEED",
                           ])
    type_options.grid(column=1, row=0, padx=5, pady=5)
    create_tooltip(type_label, "User Guide:\n"
                   "Automatically copies results to the clipboard.\n"
                   "Trash: Enter LBS to convert to tons and enter disposal cost.\n"
                   "Recycling: Enter the Ton amount to copy to the clipboard.\n"
                   "Long Ton: Enter the Recycling LBS amount to convert to tons (divided by 2240).\n"
                   "LEED: Auto calculates disposal cost plus LEED markup.\n"
                )

    pds_to_tons_label = tk.Label(root, text="Enter Pds or Tons:")
    pds_to_tons_label.grid(column=0, row=1, padx=5, pady=5)
    pds_to_tons_entry = tk.Entry(root, width=15)
    pds_to_tons_entry.grid(column=1, row=1, padx=5, pady=5)

    disposal_cost_label = tk.Label(root, text="Enter Disposal Cost:")
    disposal_cost_label.grid(column=0, row=2, padx=5, pady=5)
    disposal_cost_entry = tk.Entry(root, width=15)
    disposal_cost_entry.grid(column=1, row=2, padx=5, pady=5)

    calculate_button = tk.Button(root, text="Calculate", width= 15,
                                 command=calculate_and_copy)
    calculate_button.grid(column=1, row=3, padx=5, pady=5)

    update_config_button = tk.Button(root, text="Update Config", width=15,
                                     command=open_config_editor)
    update_config_button.grid(column=0, row=3, padx=5, pady=5)


    root.mainloop()
