import json
import logging
import os
import tempfile

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 30
ONT_LIST_FILE = "onts.json"


def _env(name: str) -> str:
    value = os.environ.get(name)
    return value.strip() if value else ""


def _normalize_mac(mac: str) -> str:
    return mac.upper().replace(":", "").replace("-", "")


def write_onts_list(onts: list, path: str = ONT_LIST_FILE) -> None:
    directory = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as outfile:
            json.dump(onts, outfile)
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


class OltCloudAPI:
    def __init__(self):
        self.url = _env("API_URL")
        self.username = _env("API_USER")
        self.password = _env("API_PASS")
        self.access_token = None
        self.refresh_token = None
        self.authenticate()
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        self.onts = self.get_ontslist()

    def authenticate(self):
        endpoint = "/api/token"
        url = f"{self.url}{endpoint}"

        payload = {
            "username": self.username,
            "password": self.password,
        }

        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        data = response.json()

        self.access_token = data["access"]
        self.refresh_token = data["refresh"]

    def refresh_access_token(self):
        endpoint = "/api/token/refresh"
        url = f"{self.url}{endpoint}"

        payload = {
            "refresh": self.refresh_token,
        }

        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)

        if response.status_code != 200:
            self.authenticate()
            return

        data = response.json()
        self.access_token = data["access"]
        self.headers["Authorization"] = f"Bearer {self.access_token}"

    def request(self, method, endpoint, **kwargs):
        url = f"{self.url}{endpoint}"

        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        headers["Content-Type"] = "application/json"

        kwargs["headers"] = headers
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)

        response = requests.request(method, url, **kwargs)

        if response.status_code == 401:
            logger.info("Token expirado, renovando...")
            self.refresh_access_token()
            headers["Authorization"] = f"Bearer {self.access_token}"
            response = requests.request(method, url, **kwargs)

        response.raise_for_status()
        return response.json()

    def get_ont(self, ont_id):
        endpoint = f"/api/v2/ftth/equipment/{ont_id}"
        return self.request("GET", endpoint)

    def get_all_onts(self):
        endpoint = "/api/v2/ftth/equipment/list"
        onts = []
        response = self.request("GET", endpoint)

        def extract_items(data):
            return [
                {
                    "id": item.get("id"),
                    "device_alias": item.get("device_alias"),
                    "serial_number": item.get("serial_number"),
                    "macs": item.get("macs", []),
                }
                for item in data.get("results", [])
            ]

        onts.extend(extract_items(response))

        while response.get("next"):
            endpoint = response["next"].replace(self.url, "")
            response = self.request("GET", endpoint)
            onts.extend(extract_items(response))

        return onts

    def get_ontslist(self):
        try:
            with open(ONT_LIST_FILE, encoding="utf-8") as infile:
                return json.load(infile)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            logger.warning("Ficheiro %s inválido, a usar lista vazia", ONT_LIST_FILE)
            return []

    def get_ontID(self, input_value, search_type):
        if not input_value or not search_type:
            return None

        input_value = input_value.strip()

        match search_type:
            case "device_alias":
                for ont in self.onts:
                    device_alias = ont.get("device_alias")
                    if device_alias and device_alias.split("-")[0] == input_value:
                        return ont.get("id")
            case "serial":
                for ont in self.onts:
                    if ont.get("serial_number") == input_value:
                        return ont.get("id")
            case "mac":
                normalized_input = _normalize_mac(input_value)
                for ont in self.onts:
                    for mac in ont.get("macs", []):
                        if _normalize_mac(mac) == normalized_input:
                            return ont.get("id")
        return None
