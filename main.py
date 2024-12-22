import requests
import json
import uuid
import os
from datetime import datetime
import rsa
import openpyxl
from tqdm import tqdm

class TricountAPI:
    def __init__(self):
        self.base_url = "https://api.tricount.bunq.com"
        self.app_installation_id = str(uuid.uuid4())
        self.public_key, self.private_key = rsa.newkeys(2048)
        self.rsa_public_key_pem = self.public_key.save_pkcs1(format="PEM").decode()
        self.headers = {
            "User-Agent": "com.bunq.tricount.android:RELEASE:7.0.7:3174:ANDROID:13:C",
            "app-id": self.app_installation_id,
            "X-Bunq-Client-Request-Id": "049bfcdf-6ae4-4cee-af7b-45da31ea85d0"
        }
        self.auth_token = None
        self.user_id = None

    def authenticate(self):
        auth_url = f"{self.base_url}/v1/session-registry-installation"
        auth_payload = {
            "app_installation_uuid": self.app_installation_id,
            "client_public_key": self.rsa_public_key_pem,
            "device_description": "Android"
        }
        response = requests.post(auth_url, json=auth_payload, headers=self.headers)
        response.raise_for_status()
        auth_data = response.json()

        response_items = auth_data["Response"]
        self.auth_token = next(item["Token"]["token"] for item in response_items if "Token" in item)
        self.user_id = next(item["UserPerson"]["id"] for item in response_items if "UserPerson" in item)
        self.headers["X-Bunq-Client-Authentication"] = self.auth_token

    def fetch_tricount_data(self, tricount_key):
        tricount_url = f"{self.base_url}/v1/user/{self.user_id}/registry?public_identifier_token={tricount_key}"
        response = requests.get(tricount_url, headers=self.headers)
        response.raise_for_status()
        return response.json()

class TricountHandler:
    @staticmethod
    def get_tricount_title(data):
        return data["Response"][0]["Registry"]["title"]

    @staticmethod
    def parse_tricount_data(data):
        registry = data["Response"][0]["Registry"]
        memberships = [
            {
                "Name": m["RegistryMembershipNonUser"]["alias"]["display_name"],
                "Balance": m["RegistryMembershipNonUser"]["balance"]["value"],
                "Currency": m["RegistryMembershipNonUser"]["balance"]["currency"]
            }
            for m in registry["memberships"]
        ]

        transactions = []
        for entry in registry["all_registry_entry"]:
            transaction = entry["RegistryEntry"]
            who_paid = transaction["membership_owned"]["RegistryMembershipNonUser"]["alias"]["display_name"]
            how_much = float(transaction["amount"]["value"]) * -1
            currency = transaction["amount"]["currency"]
            description = transaction.get("description", "")
            when = transaction["date"]
            involved = [
                alloc["membership"]["RegistryMembershipNonUser"]["alias"]["display_name"]
                for alloc in transaction["allocations"]
                if abs(float(alloc["amount"]["value"])) > 0
            ]
            attachments = transaction.get("attachment", [])

            transactions.append({
                "Who Paid": who_paid,
                "How Much": how_much,
                "Currency": currency,
                "Description": description,
                "When": when,
                "Involved": ", ".join(involved),
                "Attachments": attachments
            })

        return memberships, transactions

    @staticmethod
    def download_attachments(transactions, download_folder):
        os.makedirs(download_folder, exist_ok=True)
        file_counter = 1
        total_files = sum(len(transaction["Attachments"]) for transaction in transactions)

        with tqdm(total=total_files, desc="Downloading attachments") as progress_bar:
            for transaction in transactions:
                attachment_files = []
                for attach in transaction["Attachments"]:
                    if "urls" in attach and attach["urls"]:
                        url = attach["urls"][0]["url"]
                        extension = os.path.splitext(url.split("?")[0])[1] or ".file"
                        file_name = f"receipt_{file_counter}{extension}"
                        file_path = os.path.join(download_folder, file_name)
                        TricountHandler.download_file(url, file_path)
                        attachment_files.append(file_name)
                        file_counter += 1
                        progress_bar.update(1)
                transaction["File Names"] = ", ".join(attachment_files)

    @staticmethod
    def download_file(url, file_path):
        response = requests.get(url)
        response.raise_for_status()
        with open(file_path, "wb") as file:
            file.write(response.content)

    @staticmethod
    def write_to_excel(transactions, file_name):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Tricount Transactions"

        headers = ["Who Paid", "How Much", "Currency", "Description", "When", "Involved", "File Names", "Attachment URLs"]
        sheet.append(headers)

        for transaction in transactions:
            sheet.append([
                transaction["Who Paid"],
                transaction["How Much"],
                transaction["Currency"],
                transaction["Description"],
                datetime.strptime(transaction["When"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d"),
                transaction["Involved"],
                transaction.get("File Names", ""),
                ", ".join([attach["urls"][0]["url"] for attach in transaction["Attachments"] if "urls" in attach and attach["urls"]])
            ])

        workbook.save(file_name)
        print(f"Transactions have been saved to {file_name}.")

if __name__ == "__main__":
    tricount_key = "tISWyMCgrIMgFuxudZ"

    api = TricountAPI()
    api.authenticate()
    data = api.fetch_tricount_data(tricount_key)

    handler = TricountHandler()
    tricount_title = handler.get_tricount_title(data)

    memberships, transactions = handler.parse_tricount_data(data)

    handler.download_attachments(transactions, download_folder=f"Attachments {tricount_title}")
    handler.write_to_excel(transactions, file_name=f"Transactions {tricount_title}.xlsx")
