from register import Registration, process_user as process_user_registration
from sales import Sales, fill_billing_shipping_address, process_user as process_user_sales
from helper import *

def process_user(data):
	process_user_registration(data)
	process_user_sales(data)					

if __name__ == "__main__":
	process_csv_file(process_user)