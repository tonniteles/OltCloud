import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

class OltCloudAPI:
    def __init__(self):
        self.url = os.environ.get("API_URL").split()[0] if os.environ.get("API_URL") is not None else ""
        self.username = os.environ.get("API_USER").split()[0] if os.environ.get("API_USER") is not None else ""
        self.password = os.environ.get("API_PASS").split()[0] if os.environ.get("API_PASS") is not None else ""
        self.access_token = None
        self.refresh_token = None
        self.authenticate()
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        self.onts = self.get_ontslist()
    
    def authenticate(self):
        endpoint = '/api/token'
        url = f"{self.url}{endpoint}"

        payload = {
            "username": self.username,
            "password": self.password
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()

        data = response.json()

        self.access_token = data['access']
        self.refresh_token = data['refresh']   
    
    def refresh_access_token(self):
        endpoint = '/api/token/refresh'
        url = f"{self.url}{endpoint}"

        payload = {
            "refresh": self.refresh_token
        }

        response = requests.post(url, json=payload)

        if response.status_code != 200:
            # Refresh token expired --> re-authenticate
            self.authenticate()
            return

        data = response.json()
        self.access_token = data['access']
    
    def request(self, method, endpoint, **kwargs):
        url = f"{self.url}{endpoint}"

        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        headers["Content-Type"] = "application/json"

        kwargs["headers"] = headers

        response = requests.request(method, url, **kwargs)

        # If refresh also fails (e.g., refresh token expired), it will re-authenticate in the refresh_access_token method
        if response.status_code == 401:
            print("🔄 Token expirado, renovando...")

            self.refresh_access_token()

            headers["Authorization"] = f"Bearer {self.access_token}"
            response = requests.request(method, url, **kwargs)

        response.raise_for_status()
        return response.json()     

    def get_ont(self, ont_id):
        endpoint = f'/api/v2/ftth/equipment/{ont_id}'
        return self.request('GET', endpoint)
    
    def get_all_onts(self):
        endpoint = '/api/v2/ftth/equipment/list'
        onts = []
        response = self.request('GET', endpoint)
        
        onts.extend([
            {
                "id": item.get("id"),
                "device_alias": item.get("device_alias"),
                "serial_number": item.get("serial_number"),
                "macs": item.get("macs", [])
            }
            for item in response.get("results", [])
        ])
        
        while response['next']:
            endpoint = response['next'].replace(self.url, '')
            response = self.request('GET', endpoint)
            onts.extend([
                {
                    "id": item.get("id"),
                    "device_alias": item.get("device_alias"),
                    "serial_number": item.get("serial_number"),
                    "macs": item.get("macs", [])
                }
            for item in response.get("results", [])
            ])

        return onts
    
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
