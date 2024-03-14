
site_url = "https://realnf.epixel.link"
# site_url = "https://demo-binary.epixelcommerce.com"
# site_url = "https://master-matrix.epixel.link"
# site_url = "https://master-binary.epixel.link"

lang = "en"
prefix = "rnf"
default_country = "IN"
default_password = "As@12345"

default_input_file = "customers.csv"

#------------------------------ REGISTRATION SETTINGS --------------------------------------

# If a customer has to be registered. Setting this to False will register a normal user
customer_registration = True

if customer_registration:
	registration_path = "customer-register"
else:
	registration_path = "register"

# If the registration flow includes purchasing a package 
registration_with_package = False

# If a package is to be purchased as part of this script
package_purchase = False

# If an add-on product has to be purchased along with the main package
package_addon = False

registration_page_urls_search_keys = [
	"register",
]

if registration_with_package:
	package_get_path = "registration-enrollment-products/"
	package_post_path = "create-enrollment-order/"
	order_review_path = "review"
else:
	package_get_path = "package-purchase"
	package_post_path = "upgrade-package"
	order_review_path = "order-review"
	registration_page_urls_search_keys.append("login")
registration_page_urls_search_keys.append(package_get_path)

if package_addon:
	addon_get_path = "addons-purchase"
	addon_post_path = "addons-purchase"
	registration_page_urls_search_keys.append(addon_get_path)

registration_page_urls_search_keys += ["billing", "review", "payment"]

# ----------------------------- SALES SETTINGS ----------------------------------------------
update_billing_address = False

sales_page_urls_search_keys = [
	# "login", "dashboard", "cart", "billing-address", "review", "payment"
]




