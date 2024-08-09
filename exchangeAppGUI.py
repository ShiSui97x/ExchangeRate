"""
    Author: Thomas Ciserane
    Date: 2024-08-09
    A simple GUI application to convert currency, get exchange rates, and check the API quota using the ExchangeRate API.
    The website for the API is: https://www.exchangerate-api.com/
 """

import ttkbootstrap as ttk
from ttkbootstrap import Label, Entry, Button, Frame, Menu, Toplevel, IntVar, Checkbutton, PhotoImage, Style
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.icons import Icon
from ttkbootstrap.constants import BOTH, YES
from dotenv import load_dotenv
import requests
import os
import re

load_dotenv("path/to/.env")

API_KEY = os.getenv("API_KEY")
ADMIN = os.getenv("ADMIN")
PASSWORD = os.getenv("PASSWORD")


class UsageInstructionsDialog(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Usage Instructions")
        self.geometry("540x500")
        self.resizable(0, 0)
        self.help_icon = PhotoImage(data=Icon.question)
        self.iconphoto(False, self.help_icon)

        instructions = """ 
        ** Exchange Currency **
        You can convert the given amount from one currency to another.
        - Enter the source currency code in the 'Source currency' field.
        - Enter the target currency code in the 'Target currency' field.
        - Enter the amount to convert in the 'Amount' field.
        - Click on the 'Convert' button to get the result.
        
        ** Get Exchange Rate **
        You can get the exchange rate of the given currency.
        - Enter the currency code in the 'Source currency' field.
        - Enter the target currency code in the 'Target currency' field (Optional)
          to directly get the exchange rate between the two currencies.
        If not indicated, the exchange rate for all currencies will be displayed.
        - Click on the 'Get exchange rate' button to get the result.
        
        ** Check API Quota **
        You can check the API quota using the admin credentials.
        - Enter the admin username in the 'Admin' field.
        - Enter the admin password in the 'Password' field.
        - Click on the 'Check API Quota' button to get the result.
        
        Note: The currency code should be in the ISO 4217 format. Ex: USD, EUR, JPY, etc.
        """

        label = Label(self, text=instructions, justify="left", wraplength=500)
        label.pack(padx=10)


class ExchangeRatesDialog(Toplevel):
    def __init__(self, parent, from_currency):
        super().__init__(parent)
        self.title("Exchange Rates")
        self.resizable(0, 0)
        self.iconbitmap("icon/exchange_rate.ico")

        # Get the exchange rates
        exchange_rate = requests.get(
            f"https://v6.exchangerate-api.com/v6/{
                API_KEY}/latest/{from_currency}"
        )
        exchange_rate = exchange_rate.json()

        # Stringify the exchange rates
        text_rates = str(exchange_rate["conversion_rates"])
        text_rates = re.sub(r"[{}']", "", text_rates)
        text_rates = re.sub(r",", "\n", text_rates)

        # Display the exchange rates in a ScrolledText widget
        stext = ScrolledText(self, autohide=True, height=20,
                             width=50, font=("Helvetica", 10))
        stext.pack(fill=BOTH, expand=YES)
        stext.insert("1.0", text_rates.strip())
        stext.config(state="disabled")


# Check the quota of the API
def get_api_quota():
    """
    Retrieves the API quota information from the ExchangeRate API and saves it to a JSON file.

    Returns:
        None
    """

    if not check_admin():
        quota_label.config(text="Invalid admin credentials!")
        quota_label.after(3000, lambda: quota_label.config(text=""))
        return

    quota = requests.get(f"https://v6.exchangerate-api.com/v6/{API_KEY}/quota")
    quota = quota.json()

    # Display the quota information for 5 seconds
    quota_label.config(
        text=f"Quota: {quota['requests_remaining']} requests remaining"
    )
    admin_entry.delete(0, ttk.END)
    admin_password_entry.delete(0, ttk.END)
    quota_label.after(3000, lambda: quota_label.config(text=""))


# Get the latest exchange rate of the given currency
def get_exchange_rate():
    """Get the latest exchange rate of the given currency and save it to a JSON file.

    Args:
        currency (str): The currency code to get the exchange rate for.

    Note:
    -
    The currency code should be in the ISO 4217 format. Ex: USD, EUR, JPY, etc.
    """

    from_currency = from_currency_entry.get(
    ).upper() if from_currency_entry.get() else None

    to_currency = to_currency_entry.get().upper() if to_currency_entry.get() else None

    if not from_currency:
        exchange_rate_label.config(text="Please enter the source currency!")
        exchange_rate_label.after(
            3000, lambda: exchange_rate_label.config(text=""))
        return

    if to_currency:
        response = requests.get(
            f"https://v6.exchangerate-api.com/v6/{
                API_KEY}/latest/{from_currency}"
        )
        response_json = response.json()
        exchange_rate = response_json["conversion_rates"][to_currency]

        exchange_rate_label.config(text=f"Exchange rate for {from_currency} to {
                                   to_currency}: {exchange_rate}")
        exchange_rate_label.after(
            10000, lambda: exchange_rate_label.config(text=""))
        from_currency_entry.delete(0, ttk.END)
        to_currency_entry.delete(0, ttk.END)

    else:
        # Open another window to display the exchange rate
        rates_dialog = ExchangeRatesDialog(window, from_currency)
        rates_dialog.grab_set()


# Convert the given amount from one currency to another
def convert_currency():
    """Converts the given amount from one currency to another and saves the result to a JSON file.

    Args:
        amount (float): The amount to convert.
        from_currency (str): The currency code to convert from.
        to_currency (str): The currency code to convert to.

    Note:
    -
    The currency code should be in the ISO 4217 format. Ex: USD, EUR, JPY, etc.
    """

    from_currency = source_currency_entry.get().upper()
    to_currency = target_currency_entry.get().upper()
    amount = amount_entry.get()

    conversion = requests.get(
        f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{from_currency}/{to_currency}/{amount}")

    conversion = conversion.json()

    # Display the conversion result
    display_result.config(
        text=f"{from_currency} to {to_currency}: {
            conversion['conversion_result']}"
    )
    display_result.after(10000, lambda: display_result.config(text=""))
    source_currency_entry.delete(0, ttk.END)
    target_currency_entry.delete(0, ttk.END)
    amount_entry.delete(0, ttk.END)


# Check admin credentials
def check_admin():
    """
    Check if the admin credentials are correct.

    Returns:
        bool: True if the admin credentials are correct, False otherwise.
    """
    admin_username = admin_entry.get()
    admin_password = admin_password_entry.get()

    if admin_username == ADMIN and admin_password == PASSWORD:
        return True


# Define the main window
window = ttk.Window(themename="simplex")
window.title("Exchange Rate App")
window.geometry("800x400")
window.iconbitmap("icon/exchange_rate.ico")

# Style
style = Style()

# Configure styles
style.configure('TButton', font=('Helvetica', 10), padding=10)
style.configure('TFrames', font=('Helvetica', 10))

# Frame for the exchange currency
exchange_frame = Frame(window)
exchange_frame.pack(side="left", padx=10, expand=True, fill="both")

# Exchange currency label
exchange_label = Label(
    exchange_frame, text="Exchange Currency", bootstyle="primary", font=("Helvetica", 10, "bold")).pack(pady=10)

# Source currency
source_currency_label = Label(
    exchange_frame, text="Source currency:").pack()
source_currency_entry = Entry(exchange_frame)
source_currency_entry.pack()

# Target currency
target_currency_label = Label(
    exchange_frame, text="Target Currency:").pack()
target_currency_entry = Entry(exchange_frame)
target_currency_entry.pack()

# Amount
amount_label = Label(exchange_frame, text="Amount:").pack()
amount_entry = Entry(exchange_frame)
amount_entry.pack()

# Button to convert the currency
convert_button = Button(exchange_frame, text="Convert",
                        command=convert_currency, style="TButton")
convert_button.pack(pady=10)

# Result label
result_label = Label(exchange_frame, text="Result:").pack()
display_result = Label(exchange_frame, text="")
display_result.pack()

# Admin frame
admin_frame = Frame(window)
admin_frame.pack(side="left", padx=10, expand=True, fill="both")

# Admin label
admin_label = Label(admin_frame, text="Admin Only !", bootstyle="primary", font=(
    "Helvetica", 10, "bold")).pack(pady=10)

# Admin credentials
admin_user_label = Label(admin_frame, text="Admin:").pack()
admin_entry = Entry(admin_frame)
admin_entry.pack()

admin_password_label = Label(admin_frame, text="Password:").pack()
admin_password_entry = Entry(admin_frame, show="*")
admin_password_entry.pack()

# Button to check the API quota
check_quota_button = Button(
    admin_frame, text="Check API Quota (admin)", command=get_api_quota, style="TButton")
check_quota_button.pack(pady=10)

quota_label = Label(admin_frame, text="Quota:")
quota_label.pack()

# Exchange rate frame
exchange_rate_frame = Frame(window)
exchange_rate_frame.pack(side="left", padx=10, expand=True, fill="both")

# Exchange rate top label
exchange_rate_top_label = Label(
    exchange_rate_frame, text="Exchange Rate", bootstyle="primary", font=("Helvetica", 10, "bold")).pack(pady=10)

# Currency label for the exchange rate
currency_label = Label(exchange_rate_frame, text="Source currency:")
currency_label.pack()

from_currency_entry = Entry(exchange_rate_frame)
from_currency_entry.pack()

# Put the currency label under the source currency label
to_currency_label = Label(
    exchange_rate_frame, text="Target currency (Optional):"
)
to_currency_label.pack()

to_currency_entry = Entry(exchange_rate_frame)
to_currency_entry.pack()

# Button to get the exchange rate
get_rate_button = Button(
    exchange_rate_frame, text="Get exchange rate", command=get_exchange_rate, style="TButton")
get_rate_button.pack(pady=10)

# Label to display the exchange rate
exchange_rate_label = Label(exchange_rate_frame, text="Exchange rate:")
exchange_rate_label.pack()


def show_usage_instructions_dialog():
    dialog = UsageInstructionsDialog(window)
    dialog.grab_set()


# Main menu
main_menu = Menu(window)

# Help menu
help_menu = Menu(main_menu, tearoff=0)
help_menu.add_command(label="How to use the app",
                      command=show_usage_instructions_dialog)

main_menu.add_cascade(label="Help", menu=help_menu)
window.config(menu=main_menu)


def change_theme():
    num = var.get()
    if num % 2 == 0:
        style.theme_use("simplex")
    else:
        style.theme_use("superhero")
        style.configure('TButton', font=('Helvetica', 10), padding=10)
        style.configure('TFrames', font=('Helvetica', 10))


# Round Toggle button for Day/Night mode
var = IntVar()
round_toggle = Checkbutton(
    admin_frame, bootstyle="primary, round-toggle", text="Day/Night Toggle", variable=var, onvalue=1, offvalue=0,
    command=change_theme)
round_toggle.pack(side="bottom", pady=50)

# Run the GUI
window.mainloop()
