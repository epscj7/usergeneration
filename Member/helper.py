from csv import reader as csv_reader, writer as csv_writer
from lxml.html import fromstring
import sys
import os
import time
from settings import *
from time import sleep


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

class RequestMixin:
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
        # from pdb import set_trace; set_trace()
        error = None
        response = self.session.post(*args, **kwargs)
        if response.status_code >= 400:
            error = f"Request failed with status code {response.status_code}"
        else:
            if response.status_code == 301 or response.status_code == 302:
                if hasattr(self, 'page_url_search_keys'):
                    if self.check_wrong_redirection(response.headers['location']):
                        error = "Some error occured! Check the cookie-messages for some clue.."
                    self.page_number += 1
            else: 
                if response.text:
                    errors = self.search(response, ".invalid-feedback", get_all_data=True)
                    if errors:
                        error = errors[0].text.strip()
        

        if error:
            self.stop(error, response)
        else:            
            return response

    def get_csrfmiddlewaretoken(self, page_response):
        # csrfmiddlewaretoken = None
        # root = fromstring(page_response.text)
        # elements = root.xpath("//*[self::input]")
        # for element in elements:
        #     if element.attrib.get("name") == "csrfmiddlewaretoken":
        #         csrfmiddlewaretoken = element.attrib.get("value")
        csrfmiddlewaretoken = self.search(page_response, "input[name=csrfmiddlewaretoken]")
        if csrfmiddlewaretoken is None:
            self.stop("No CSRF middleware token found in the page..", page_response)
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

    def stop(self, message, response):
        # from pdb import set_trace; set_trace()

        if response.history:
            url = response.history[0].request.url
            method = response.history[0].request.method
        else:
            url = response.request.url
            method = response.request.method

        ppr(f"Error with URL: {url}, method: {method}")
        ppr(message)
        ppr(f"Cookie messages:- {response.cookies['messages']}")
        raise Exception(message)

    def check_wrong_redirection(self, next_url):
        for i in range(self.page_number, len(self.page_url_search_keys)):
            search_key = self.page_url_search_keys[i]
            if next_url.find(search_key) > 0:
                return False
        else:
            ppr(f"Wrong redirection to {next_url}")
            return True

    def login(self, data):
        response = self.get_page(f"{site_url}/en/login/")
        login_csrfmiddlewaretoken = self.get_csrfmiddlewaretoken(response)
        response = self.post_page(f"{site_url}/en/login/",
                        data = {
                            "csrfmiddlewaretoken" : login_csrfmiddlewaretoken,
                            # "username"            : data['username'],
                            # "password"            : self.password,
                            # Please uncomment the below 3 lines if we have enabled the 2 FA
                             "auth-username"            : data['username'],
                             "auth-password"            : self.password,
                             "user_login_view_with_two_factor-current_step" : "auth",
                        },
                        headers={"Referer" : f"{site_url}/en/login/"},
                        allow_redirects=False,          
        )

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

def process_csv_file(process_user_function):
    sleep(1)
    start_time = time.time()
    input_file = sys.argv[1] if len(sys.argv) > 1 else default_input_file
    target_count = int(sys.argv[2]) if len(sys.argv) > 2 else 99999
    print(f"Processing the file {input_file}")  
    stop_processing = False
    processed_count = 0

    with open(input_file) as file:
        csv_file = csv_reader(file)
        outfile = []
        for i, row in enumerate(csv_file):
            if not stop_processing:
                data = {}
                if i == 0:
                    headers = row
                else:
                    for j, column in enumerate(row):
                        data[headers[j]] = column
                    if data['processed?'] == 'Y':
                        print(f"Skipping processed user {data['username']}...")
                    else:
                        try:                      
                            process_user_function(data)
                        except Exception as e:
                            ppr(e)
                            ppr("Skipping further processing of the file...")
                            stop_processing = True
                            outfile.append(row)
                            continue
                        processed_count += 1    
                        ppg(f"{processed_count} - User {data['username']} successfully processed!")
                        row[0] = 'Y'
                        if processed_count >= target_count:
                            print("Target reached. Skipping further processing of the file...")
                            stop_processing = True                                                                          
            outfile.append(row)

    with open(input_file, 'w', newline='', encoding='utf-8') as file:
        csv_file = csv_writer(file)
        for row in outfile:
            csv_file.writerow(row)

    execution_summary(start_time, time.time(), processed_count)     
