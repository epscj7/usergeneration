import requests
from helper import *


class Registration(RequestMixin):
	def __init__(self, data):
		self.session = requests.Session()
		self.password = data.get('password',None) if data.get('password',None) else default_password	
		self.page_number = 1
		if len(registration_page_urls_search_keys) > 0:
			self.page_url_search_keys = registration_page_urls_search_keys
		
	def register(self, data):
		# from pdb import set_trace; set_trace()
		
		# registration_page    	
		response = self.get_page(f"{site_url}/{lang}/{registration_path}/")
		register_csrfmiddlewaretoken = self.get_csrfmiddlewaretoken(response)

		subdomain = data.get('subdomain',None) if data.get('subdomain',None) else data['username']

		if customer_registration:
			cookies = {'u_name': data['sponsor']}
		else:
			cookies = None

		response = self.post_page(f"{site_url}/{lang}/{registration_path}/",
						data = {
							"csrfmiddlewaretoken"   : register_csrfmiddlewaretoken,
							"sponsor"               : data['sponsor'],
							"first_name"            : data['first_name'],
							"last_name"             : data['last_name'],
							"username"              : data['username'],
							"email"                 : data['email'],
							"subdomain"				: subdomain,
							"country"               : data['country'],
							"phone_number"          : data['phone'],
							"date_of_birth"         : data['DOB'],
							"gender"		 		: data['gender'],
							"password1"             : self.password,
							"password2"             : self.password,
							"agree_terms"           : 1,
						},
						headers={"Referer" : f"{site_url}/{registration_path}/", },
						cookies=cookies,
						allow_redirects=False
		)
		# print(response.status_code)
		# print(response.text)
		# print("end of registration_page...")

	def purchase_package(self,data):
		# from pdb import set_trace; set_trace() 
		user = "user" if registration_with_package else data['username']
		region = data['country'].lower()		
		base_url = f"{site_url}/{lang}/{user}/{region}/{prefix}"
		
		# package selection
		response = self.get_page(f"{base_url}/{package_get_path}")
		package_csrfmiddlewaretoken = self.get_csrfmiddlewaretoken(response)
		response = self.post_page(f"{base_url}/{package_post_path}/",
						data = {
							"csrfmiddlewaretoken" : package_csrfmiddlewaretoken,
							"product_id"          : data['package_id'],
						},
						headers={"Referer" : f"{base_url}/{package_get_path}"},
						allow_redirects=False,
		)        
		
		#package add-on
		if package_addon:
			response = self.get_page(f"{base_url}/{addon_get_path}")
			print(response.status_code)
			addon_csrfmiddlewaretoken = self.get_csrfmiddlewaretoken(response)
			response = self.post_page(f"{base_url}/{addon_post_path}/",
							data = {
								"csrfmiddlewaretoken" : addon_csrfmiddlewaretoken,
								"product_id"          : data['addon_id'],
							},
							headers={"Referer" : f"{base_url}/{addon_get_path}"},
							allow_redirects=False,
			)        

		# billing address
		response = self.get_page(f"{base_url}/billing-address/")
		billing_csrfmiddlewaretoken = self.get_csrfmiddlewaretoken(response)
		billing_order_id = self.search(response, "#id_billing-customer_address_order_id")
		billing_uid = self.search(response, "#id_billing-uid")
		
		response = self.post_page(f"{base_url}/billing-address/",
					data = {
							"csrfmiddlewaretoken"                   : billing_csrfmiddlewaretoken,	
							"first_addr"	                        : "1",
							"billing-customer_default_address"	    : "1",
							"billing-customer_address_order_id"	    : billing_order_id,
							"billing-uid"	                        : billing_uid,
							"billing-customer_address_country"      : data['billing_country'],
							"billing-customer_address_first_name"   : data['first_name'],
							"billing-customer_address_last_name"    : data['last_name'],
							"billing-customer_address_locality"     : "Chinatown",
							"billing-customer_address_mail_id"	    : data['email'],
							"billing-customer_address_name_line"    : "221B",
							"billing-customer_address_phone_number"	: data['phone'],
							"billing-customer_address_postal_code"  : data['billing_postal_code'],
							"billing-customer_address_premise"      : "Baker Street",
							"billing-customer_address_state"        : data['billing_state'], 
							"billing-customer_address_type"	        : "billing",
							"billing-id"	                        : "",
							"checkout"                              : "Checkout",							

						},
		
	
						headers={"Referer" : f"{base_url}/billing-address/"},
						allow_redirects=False,
		)

		#order review and checkout
		response = self.get_page(f"{base_url}/{order_review_path}/")
		checkout_csrfmiddlewaretoken = self.get_csrfmiddlewaretoken(response)
		response = self.post_page(f"{base_url}/{order_review_path}/",
						data = {
							"csrfmiddlewaretoken" : checkout_csrfmiddlewaretoken,
							"varient"             : "default",
						},
						headers={"Referer" : f"{base_url}/{order_review_path}/"},
						allow_redirects=False,
		)
		# print(response.headers['location'])        
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

		# print(response.url)
		# print(response.status_code)


def process_user(data):
	print(f"Processing registration for user {data['username']}...")
	u = Registration(data)
	u.register(data)
	if package_purchase:
		if registration_with_package:
			# If the registration flow includes purchasing a package
			u.purchase_package(data)
		else: 
			# registration has been completed without a package. Now login and purchase a package
			u.login(data)
			u.purchase_package(data)
					

if __name__ == "__main__":
    while True:
        process_csv_file(process_user)
