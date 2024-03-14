#------------------------------ SITE SETTINGS --------------------------------------
# site_url = "https://demo-binary.epixelcommerce.com"
# site_url = "https://wellness.epixel.link"
# site_url = "https://master-binary.epixel.link"
site_url = "https://demo-unilevel-commerce.epixel.link/"

admin_user = "mpfp-base-business-admin"
admin_password = "Bu@Admin123"

lang = "en"
prefix = "v13"
default_region = "us"
default_password = "As@12345"

default_input_file = "payout.csv"

#------------------------------ REGISTRATION SETTINGS --------------------------------------

# If a customer has to be registered. Setting this to False will register a normal user
customer_registration = False

if customer_registration:
	registration_path = "customer-register"
else:
	registration_path = "register"

# If the registration flow includes purchasing a package 
registration_with_package = True

# If a package is to be purchased as part of this script
package_purchase = True

# If an add-on product has to be purchased along with the main package
package_addon = False

# ----------------------------- SALES SETTINGS ----------------------------------------------
anonymous_purchase = False
update_billing_address = False


registration_redirection_search_keys = []
if registration_with_package:
	package_get_path = "registration-enrollment-products/"
	package_post_path = "create-enrollment-order/"
	order_review_path = "review"
else:
	package_get_path = "package-purchase"
	package_post_path = "upgrade-package"
	order_review_path = "order-review"
	registration_redirection_search_keys.extend(["login","dashboard"])
registration_redirection_search_keys.append(package_get_path)
if package_addon:
	addon_get_path = "addons-purchase"
	addon_post_path = "addons-purchase"
	registration_redirection_search_keys.append(addon_get_path)
registration_redirection_search_keys.extend(["billing", "review", "payment"])

sales_redirection_search_keys = []
if not anonymous_purchase:
	sales_redirection_search_keys.append("dashboard")
sales_redirection_search_keys.extend(["cart", "billing-address", "review", "payment"])




