#!/usr/bin/env python3
import requests
import json
import uuid
import os
from datetime import datetime
import csv
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

class TricountAPI:
    def __init__(self):
        self.base_url = "https://api.tricount.bunq.com"
        self.app_installation_id = str(uuid.uuid4())
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()
        self.rsa_public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
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
        print("authenticating...")
        response = requests.post(auth_url, json=auth_payload, headers=self.headers)
        response.raise_for_status()
        auth_data = response.json()

        response_items = auth_data["Response"]
        self.auth_token = next(item["Token"]["token"] for item in response_items if "Token" in item)
        self.user_id = next(item["UserPerson"]["id"] for item in response_items if "UserPerson" in item)
        self.headers["X-Bunq-Client-Authentication"] = self.auth_token

    def fetch_tricount_data(self, tricount_key):
        tricount_url = f"{self.base_url}/v1/user/{self.user_id}/registry?public_identifier_token={tricount_key}"
        print("fetching data...")
        response = requests.get(tricount_url, headers=self.headers)
        response.raise_for_status()
        return response.json()


def get_tricount_title(data):
    return data["Response"][0]["Registry"]["title"]

def parse_tricount_data(data):
    registry = data["Response"][0]["Registry"]

    transactions = []
    for entry in registry["all_registry_entry"]:
        transaction = entry["RegistryEntry"]
        type_transaction = transaction["type_transaction"]
        who_paid = transaction["membership_owned"]["RegistryMembershipNonUser"]["alias"]["display_name"]
        total = float(transaction["amount"]["value"]) * -1
        currency = transaction["amount"]["currency"]
        description = transaction.get("description", "")
        when = transaction["date"]
        shares = {
            alloc["membership"]["RegistryMembershipNonUser"]["alias"]["display_name"]: abs(float(alloc["amount"]["value"]))
            for alloc in transaction["allocations"]
            }
        category = transaction["category"]
        attachments = transaction.get("attachment", [])

        transactions.append({
            "Type": type_transaction,
            "Who Paid": who_paid,
            "Total": total,
            "Currency": currency,
            "Description": description,
            "When": when,
            "Shares": shares,
            "Category": category,
            "Attachments": attachments
        })

    return transactions



def prepare_transaction_data(transaction):
    """
    Helper method to prepare the data for each transaction.
    Extracts involved people, formatted date, and attachment URLs.
    """
    # List of involved people involved in the transaction
    involved = ", ".join([name for name, amount in transaction["Shares"].items() if amount > 0])

    # Prepare the row data for the transaction
    row_data = [
        transaction["Who Paid"],
        transaction["Total"],
        transaction["Currency"],
        transaction["Description"],
        datetime.strptime(transaction["When"], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d"),
        involved,
        transaction.get("File Names", ""),
        ", ".join([attach["urls"][0]["url"] for attach in transaction["Attachments"] if "urls" in attach and attach["urls"]]),
        transaction["Category"]
    ]

    return row_data



def write_to_csv(transactions, file_name):
    """
    Writes transaction data to a CSV file with the given file name.

    Parameters:
    - transactions (list): A list of transaction data.
    - file_name (str): The name of the CSV file to save the data to (without the .csv extension).

    The CSV file will have the following headers:
    "Who Paid", "Total", "Currency", "Description", "When", "Involved", "File Names", "Attachment URLs", "Category"

    Each transaction will be processed by the `prepare_transaction_data` method and written to the file.
    """
    with open(f"{file_name}.csv", "w") as csvfile:
        headers = ["Who Paid", "Total", "Currency", "Description", "When", "Involved", "File Names", "Attachment URLs", "Category"]
        transaction_writer = csv.writer(csvfile, delimiter=";")
        transaction_writer.writerow(headers)

        # Iterate through each transaction and write its data to the CSV file
        for transaction in transactions:
            row_data = prepare_transaction_data(transaction)
            transaction_writer.writerow(row_data)

        print(f"Transactions have been saved to {file_name}.csv.")


def usage():
    print(f"""USAGE: {sys.argv[0]} key [OPTIONS...]

    where OPTIONS are:

    --raw : store raw data from response
    --help: print this text""", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        usage()

    raw = False
    tricount_key = None

    # Parsing arguments.
    for arg in sys.argv[1:]:
        if arg == "--help":
            usage()
        elif arg == "--raw":
            raw = True
        else:
            if tricount_key is not None:
                print("Multiple keys for tricount key", file=sys.stderr)
                usage()
            tricount_key = arg

    api = TricountAPI()
    api.authenticate()
    data = api.fetch_tricount_data(tricount_key)

    # Save data to local file.
    if raw:
        with open(f'response_data_{tricount_key}.json', 'w') as f:
            json.dump(data, f, indent=2)

    tricount_title = get_tricount_title(data)
    transactions = parse_tricount_data(data)

    write_to_csv(transactions, file_name=f"Transactions {tricount_title}")
