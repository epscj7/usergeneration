import requests
from csv import reader as csv_reader, writer as csv_writer
from lxml.html import fromstring
import sys
import os
import time
from settings import *
from pdb import set_trace as st



os.system("")

class Colors:
#ANSI Escape sequences for colors
	RED     = '\x1b[31m'
	GREEN   = '\x1b[32m'
	YELLOW  = '\x1b[33m'
	BLUE    = '\x1b[34m'
	MAGENTA = '\x1b[35m'
	CYAN    = '\x1b[36m'
	RESET   = '\x1b[0m'
	BOLD    = '\x1b[1m'
	WHITE_BACKGROUND = '\x1b[47m'

def ppg(arg):
	print(Colors.BOLD, end="") 
	print(Colors.GREEN, end="") 
	print(arg) 
	print(Colors.RESET, end="") 
	print("") 

def ppr(arg):
	print(Colors.BOLD, end="") 
	print(Colors.RED, end="") 
	print(arg) 
	print(Colors.RESET, end="") 
	print("")

class RequestBase:
	def __init__(self, csv_data):
		self.session = requests.Session()
		self.redirection_index = 0
		self.password = csv_data.get('password',None) if csv_data.get('password',None) else default_password

	def get_page(self, *args, **kwargs):
		response = self.session.get(*args, **kwargs)
		error = None
		if response.status_code >= 400:
			error = f"Request failed with status code {response.status_code}"

		if error:
			self.stop(error, response)
		else:
			return response

	def post_page(self, *args, **kwargs):
		error = None
		response = self.session.post(*args, **kwargs)
		if response.status_code >= 400:
			error = f"Request failed with status code {response.status_code}"
		else:
			if response.status_code == 301 or response.status_code == 302:
				if hasattr(self, 'page_url_search_keys'):
					if self.check_wrong_redirection(response.headers['location']):
						error = "Some error occured! The cookie-messages may have some clue.."
					self.redirection_index += 1
			else: 
				if response.text:
					errors = self.search(response, ".invalid-feedback", get_all_data=True)
					if errors:
						error = errors[0].text.strip()
		

		if error:
			self.stop(error, response)
		else:            
			return response

	def get_csrfmiddlewaretoken(self, path=None, page_content=None):
		if page_content:
			response = page_content
		else:
			response = self.get_page(path)
		csrfmiddlewaretoken = self.search(response, "input[name=csrfmiddlewaretoken]")
		if csrfmiddlewaretoken is None:
			self.stop("No CSRF middleware token found in the page..", response)
		else:
			return csrfmiddlewaretoken

	def search(self, haystack, needle, get_all_data=False):
		tree = fromstring(haystack.text)
		result = tree.cssselect(needle)
		if len(result) == 0:
			return None
		elif get_all_data:
			return result
		else:
			return result[0].value

	def stop(self, message, response=None):
		ppr(message)
		if response:
			if response.history:
				url = response.history[0].request.url
				method = response.history[0].request.method
			else:
				url = response.request.url
				method = response.request.method

			ppr(f"Error with URL: {url}, method: {method}")
			if 'messages' in response.cookies:
				ppr(f"Cookie messages:- {response.cookies['messages']}")            

		raise Exception(message)

	def check_wrong_redirection(self, next_url):
		for i in range(self.redirection_index, len(self.page_url_search_keys)):
			search_key = self.page_url_search_keys[i]
			if next_url.find(search_key) > 0:
				return False
		else:
			ppr(f"Wrong redirection to {next_url}")
			return True

	def login(self, csv_data):
		if csv_data['username'] == admin_user:
			login_path = f"{site_url}/en/admin-login/"
		else:
			login_path = f"{site_url}/en/login/"
		if "password" in csv_data and csv_data["password"]:
			password = csv_data["password"]
		elif hasattr(self,"password"):
			password = self.password
		else:
			password = default_password

		response = self.post_page(login_path,
						data = {
							"csrfmiddlewaretoken" : self.get_csrfmiddlewaretoken(f"{site_url}/en/login/"),
							"username"            : csv_data['username'],
							"password"            : password,
						},
						headers={"Referer" : f"{site_url}/en/login/"},
						allow_redirects=False,
		)

	def get_form(self, path, form_index=0):
		response = self.get_page(path)
		tree = fromstring(response.text)
		form = tree.forms[form_index]        
		return form



def execution_summary(start_time, end_time, processed_count):
	elapsed_time = round(end_time - start_time, 2)
	seconds = elapsed_time
	minutes = 0
	hours = 0

	time_string = f"{seconds} seconds"
	if elapsed_time >= 60:
		minutes = seconds // 60
		seconds = seconds % 60
		time_string = f"{minutes} minutes, {seconds} seconds"
	if minutes >= 60:
		hours = minutes // 60
		minutes = minutes % 60
		time_string = f"{hours} hours, {minutes} minutes, {seconds} seconds" 
	print(f"Processed {processed_count} records in {time_string}.") 
	if processed_count > 0:
		average_time = round(elapsed_time / processed_count, 2)   
		print(f"Average time taken = {average_time} seconds.")

def process_csv_file(process_user_function, input_file, target_count):
	start_time = time.time()
	print(f"Processing the file {input_file}")
	stop_processing = False
	processed_count = 0
	exc = None

	with open(input_file) as file:
		csv_file = csv_reader(file)
		outfile = []
		for i, row in enumerate(csv_file):
			if not stop_processing:
				csv_data = {}
				if i == 0:
					headers = row
					row_identifier = headers[1]
				else:
					for j, column in enumerate(row):
						csv_data[headers[j]] = column.strip()
					if csv_data['processed?'] == 'Y':
						print(f"Skipping processed {row_identifier} {csv_data[row_identifier]}...")
					else:
						try:
							process_user_function(csv_data)
						except Exception as e:
							ppr(f"Skipping further processing of the file {input_file}..")
							exc = e
							stop_processing = True
							outfile.append(row)
							continue
						processed_count += 1    
						ppg(f"{processed_count} - {row_identifier} {csv_data[row_identifier]} successfully processed!")
						row[0] = 'Y'
						if processed_count >= target_count:
							print(f"Target reached. Skipping further processing of the file {input_file}..")
							stop_processing = True                                                                          
			outfile.append(row)

	with open(input_file, 'w', newline='', encoding='utf-8') as file:
		csv_file = csv_writer(file)
		for row in outfile:
			csv_file.writerow(row)

	execution_summary(start_time, time.time(), processed_count)

	if stop_processing:
		raise exc

def main(process_user_function):
	input_file = sys.argv[1] if len(sys.argv) > 1 else default_input_file
	target_count = int(sys.argv[2]) if len(sys.argv) > 2 else 99999
	process_csv_file(process_user_function, input_file, target_count)