import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

class OltCloudAPI:
    def __init__(self):
        self.url = os.environ.get("API_URL")
        self.username = os.environ.get("API_USER")
        self.password = os.environ.get("API_PASS")
        self.token = self.get_token()
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        self.onts = self.get_ontslist()

    def get_token(self):
        endpoint = '/api/token'
        request_url = f"{self.url}{endpoint}"
        user_api = {
            'username': self.username,
            'password': self.password
        }
        response = requests.post(request_url, json=user_api)
        print("STATUS:", response.status_code)
        print("BODY:", response.text)
        response.raise_for_status()
        return response.json()['access']

    def get_ontslist(self):
        try:
            with open('onts.json', 'r') as infile:
                return json.load(infile)
        except FileNotFoundError:
            return []

    def get_ontID(self, input_value, search_type):
        match search_type:
            case 'device_alias':
                for ont in self.onts:
                    device_alias = ont.get('device_alias')
                    if device_alias and device_alias.split('-')[0] == input_value:
                        return ont.get('id')
            case 'serial':
                for ont in self.onts:
                    if ont.get('serial_number') == input_value:
                        return ont.get('id')
            case 'mac':
                for ont in self.onts:
                    if input_value in ont.get('macs', []):
                        return ont.get('id')
        return None

    def get_ont(self, ont_id):
        endpoint = '/api/v2/ftth/equipment/{id}'.format(id=ont_id)
        resquest_url = f"{self.url}{endpoint}"
        #print(resquest_url)
        try:
            response = requests.get(resquest_url, headers=self.headers)
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")  # Python 3.6+
            print(f"Response content: {response.text}")
        except Exception as err:
            print(f"Other error occurred: {err}")
    
    def get_all_onts(self):
        endpoint = '/api/v2/ftth/equipment/list'
        resquest_url = f"{self.url}{endpoint}"
        onts = []
        try:
            response = requests.get(resquest_url, headers=self.headers)
            onts.extend(response.json()['results'])
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response content: {response.text}")
        except Exception as err:
            print(f"Other error occurred: {err}")
        #count = 1
        # Nexts Pages
        while response.json()['next']:
            resquest_url = f"{response.json()['next']}"
            print(resquest_url)
            response = requests.get(resquest_url, headers=self.headers)
            onts.extend(response.json()['results'])
            # Limit to 3 pages for testing
            #count += 1
            #if count >= 3:
            #    break
        return onts