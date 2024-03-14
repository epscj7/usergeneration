from helper import *
import json

class PayoutMethod(RequestBase):
	payout_payment_methods = [
		"bitcoin",
		"bank",
		"payquicker",
		"paypal",
		"hyperwallet",
		"gpg",	
	]
	dev_token = "422602"

	def __init__(self, csv_data):
		super().__init__(csv_data)

	def set_payout_method(self, csv_data):
		if csv_data['subdomain']: 
			subdomain = csv_data['subdomain']
		else:
			subdomain = csv_data['username']
		region = csv_data['country_code'].lower()
		base_url = f"{site_url}/{lang}/{subdomain}/{region}/{prefix}"
		
		payout_method = csv_data['payout_method']
		if payout_method not in self.payout_payment_methods:
			self.stop("Incorrect payment method specified..")

		# setting the preferred payment method
		response = self.post_page(f"{base_url}/payout-payment-methods",
						data = {
							"csrfmiddlewaretoken" : self.get_csrfmiddlewaretoken(f"{base_url}/payout-payment-methods"),
							f"{payout_method}-status" : "on",
							"submit" : "Reset",
						},
						headers={"Referer" : f"{base_url}/payout-payment-methods"},
						allow_redirects=False,
		)
		# to get the token
		response = self.post_page(f"{site_url}/{lang}/{subdomain}/{region}/user/token-generator/",
						headers={"Referer" : f"{base_url}/payout-payment-methods",
								 "X-Requested-With" : "XMLHttpRequest",
								 "X-CSRFToken" : self.session.cookies['csrftoken'],
								 "X-METHODOVERRIDE" : "PUT", 
						},
						allow_redirects=False,
		)
		response_json = json.loads(response.text)
		if response.text and 'success' in response_json:
			token_checksum = response_json['token_checksum']
		else:
			ppr(f"Cookie messages:- {response.cookies['messages']}")
			error = "Error fetching token checksum! The cookie-messages may have some clue.."
			self.stop(error, response)

		payment_details = {
			"token_checksum_field" : token_checksum,
			"token_field" : self.dev_token,
			"token_submit" : "true",
		}
		if payout_method == "bitcoin":
			payment_details.update({
				'wallet_address' : csv_data['wallet_address'],
			})
		elif payout_method == "bank":
			payment_details.update({
				'first_name'   : csv_data['first_name'],
				'lastname'	   : csv_data['last_name'],
				'countryobj'   : csv_data['country_id'],
				'bank_address' : "HSBC Bank",
				'account_number' : "1234567890",
				'account_type' : "Savings",
				'ifsc_code_routing_number' : csv_data['ifsc_code'],
				'iban' : csv_data['iban'],
				'swift_code' : csv_data['swift_code'],
			})
		elif payout_method == "paypal":
			payment_details.update({
				'first_name' : csv_data['first_name'],
				'surname'	 : csv_data['last_name'],
				'paypal_email' : csv_data['paypal_email'],
			})
		elif payout_method == "payquicker":
			payment_details.update({
				'first_name' : csv_data['first_name'],
				'surname'	 : csv_data['last_name'],
				'payquicker_id' : csv_data['payquicker_id'],
			})
		elif payout_method == "hyperwallet":
			payment_details.update({
				'HyperWallet_id' : csv_data['hyperWallet_id'],
			})
		elif payout_method == "gpg":
			payment_details.update({
				'gpg_id' : csv_data['gpg_id'],
				'first_name' : csv_data['first_name'],
				'surname'	 : csv_data['last_name'],
			})

		# saving payment details
		payment_details['csrfmiddlewaretoken'] = self.get_csrfmiddlewaretoken(f"{base_url}/payment-methods/{payout_method}/setting")
		response = self.post_page(f"{base_url}/payment-methods/{payout_method}/setting",
						data = payment_details,
						headers={"Referer" : f"{base_url}/payout-payment-methods"},
						allow_redirects=False,
		)


def process_user(csv_data):
	print(f"Setting payout method for user {csv_data['username']}...")
	obj = PayoutMethod(csv_data)
	obj.login(csv_data)
	obj.set_payout_method(csv_data)

if __name__ == "__main__":
	main(process_user)

