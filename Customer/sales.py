import requests
import json
from helper import *


class Sales(RequestMixin):
	def __init__(self, data):
		self.session = requests.Session()
		self.password = data.get('password',None) if data.get('password',None) else default_password
		self.page_number = 1			
		if len(sales_page_urls_search_keys) > 0:
			self.page_url_search_keys = sales_page_urls_search_keys

	def purchase_product(self, data):
		# from pdb import set_trace; set_trace()
		
		# add product to cart
		user = data['username']
		region = data['country'].lower()
		base_url = f"{site_url}/{lang}/{user}/{region}/{prefix}"


		response = self.post_page(f"{base_url}/cart/",
						data = {
							"sku"            : data['product_sku'],
						},
						headers={"Referer" : f"{base_url}/product/list/",
								 "X-Requested-With" : "XMLHttpRequest",
								 "X-CSRFToken" : self.session.cookies['csrftoken'], 
						},
						allow_redirects=False,        	
		)
		if 'success' not in json.loads(response.text):
			ppr(f"Cookie messages:- {response.cookies['messages']}")
			error = "Some error occured! Check the cookie-messages for some clue.."
			self.stop(error, response)

		response = self.get_page(f"{base_url}/cart/")
		checkout_csrfmiddlewaretoken = self.get_csrfmiddlewaretoken(response)
		response = self.post_page(f"{base_url}/checkout/",
						data = {
							"csrfmiddlewaretoken" : checkout_csrfmiddlewaretoken,
						},
						headers={"Referer" : f"{base_url}/cart"},
						allow_redirects=False,
		)

		#billing address
		response = self.get_page(f"{base_url}/billing-address/")
		billing_csrfmiddlewaretoken = self.get_csrfmiddlewaretoken(response)
		billing_id = self.search(response, "#biling_id")

		post_data = {
			"csrfmiddlewaretoken"                   : billing_csrfmiddlewaretoken,
			"checkout"                              : "Checkout",
			"shippingcalculator-shipping_group"     : data['shipping_group'],
			"shippingcalculator-order_id"           : "0"
		}		
		if billing_id:
			shipping_id = self.search(response, "#shipping_id")
			post_data["billing-id"] = billing_id
			post_data["shipping-id"] = shipping_id
			if update_billing_address:
				fill_billing_shipping_address(data, post_data)			
		else:
			billing_uid = self.search(response, "#id_billing-uid")
			if not billing_uid:
				#get user-id
				response = self.get_page(f"{base_url}/billing-address/",
								params = {
									"btn-action" : "billing",
									"ecommerce"  : "True",
									"shipping_eq_billing" : "on",   
								},
								headers = {"X-Requested-With" : "XMLHttpRequest"},
				)
				billing_uid = self.search(response, "#id_billing-uid")

			post_data["first_addr"] = "1"
			post_data["billing-uid"] = billing_uid
			post_data["billing-id"] = ""
			post_data["shipping-id"] = ""						
			fill_billing_shipping_address(data, post_data)
		response = self.post_page(f"{base_url}/billing-address/",
						data = post_data,
						headers={"Referer" : f"{base_url}/billing-address/"},
						allow_redirects=False,
		)

		#order review and checkout
		response = self.get_page(f"{base_url}/review/")
		review_csrfmiddlewaretoken = self.get_csrfmiddlewaretoken(response)
		response = self.post_page(f"{base_url}/review/",
						data = {
							"csrfmiddlewaretoken" : review_csrfmiddlewaretoken,
							"varient"             : "default",
						},
						headers={"Referer" : f"{base_url}/review/"},
						allow_redirects=False,
		)
		self.payment_redirection_url = response.headers['location']

		# payment
		response = self.get_page(f"{site_url}{self.payment_redirection_url}")
		payment_csrfmiddlewaretoken = self.get_csrfmiddlewaretoken(response)


		response = self.post_page(f"{site_url}{self.payment_redirection_url}",
						data = {
							"csrfmiddlewaretoken"   : payment_csrfmiddlewaretoken,
							"fraud_status"          : "accept",
							"gateway_response"      : "3ds-disabled",
							"status"                : "confirmed",
							"verification_result"   : "confirmed"                            
						},
						headers={"Referer" : f"{site_url}{self.payment_redirection_url}"},
		)


def fill_billing_shipping_address(data, post_data):
	post_data["billing-customer_address_type"]	        = "billing"
	post_data["billing-customer_default_address"]	    = "1"
	post_data["billing-customer_address_first_name"]    = data['first_name']
	post_data["billing-customer_address_last_name"]     = data['last_name']
	post_data["billing-customer_address_locality"]      = "Chinatown"
	post_data["billing-customer_address_mail_id"]	    = data['email']
	post_data["billing-customer_address_name_line"]     = "221B"
	post_data["billing-customer_address_premise"]       = "Baker Street"
	post_data["billing-customer_address_phone_number"]	= data['phone']
	post_data["billing-customer_address_postal_code"]   = data['billing_postal_code']
	post_data["billing-customer_address_state"]         = data['billing_state'] 
	post_data["billing-customer_address_country"]       = data['billing_country']


	if data['shipping_eq_billing'] == 'Y' or data['shipping_eq_billing'] == 'y':
		post_data["shipping-eq-billing"] 					= "1"
		post_data["shipping_same_as_billing"] 				= "on"
	else:
		post_data["shipping-eq-billing"] 					= "0"
		post_data["shipping-customer_address_type"] 		= "shipping"
		post_data["shipping-customer_default_address"] 		= "1"
		post_data["shipping-customer_address_first_name"] 	= data['first_name']
		post_data["shipping-customer_address_last_name"] 	= data['last_name']
		post_data["shipping-customer_address_mail_id"] 		= data['email']
		post_data["shipping-customer_address_name_line"]	= "221B"
		post_data["shipping-customer_address_premise"] 		= "Baker Street"
		post_data["shipping-customer_address_locality"] 	= "Chinatown"
		post_data["shipping-customer_address_phone_number"] = data["phone"]
		post_data["shipping-customer_address_postal_code"]	= data["shipping_postal_code"]
		post_data["shipping-customer_address_country"]		= data["shipping_country"]
		post_data["shipping-customer_address_state"]		= data["shipping_state"]
		if "billing-uid" in post_data:
			post_data["shipping-uid"] 						= post_data["billing-uid"]
		if "billing-customer_address_order_id" in post_data:
			post_data["shipping-customer_address_order_id"] 	= post_data["billing-customer_address_order_id"]

def process_user(data):
	print(f"Processing product-purchase for user {data['username']}...")
	s = Sales(data)
	s.login(data)
	s.purchase_product(data)


if __name__ == "__main__":
	process_csv_file(process_user)		
