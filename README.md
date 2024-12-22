# Tricount API to Excel

This script allows you to fetch all transactions and attachments from a shared Tricount and save them in a structured and user-friendly format.

## Features
- Retrieve transactions and attachments from a shared Tricount.
- Save transactions to an Excel file.
- Download all attachments and organize them in a folder.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/MrNachoX/tricount-downloader.git
   cd tricount-downloader
   ```
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Step 1: Obtain Your Tricount Key
1. Open your Tricount.
2. Share the Tricount via a public link.
3. Copy the part after `https://tricount.com/`. For example, if your link is `https://tricount.com/tISWyMCgrIMgFuxudZ`, the key is `tISWyMCgrIMgFuxudZ`.

### Step 2: Run the Script
1. Replace the placeholder `tricount_key` in the script with your actual Tricount key.
2. Execute the script:
   ```bash
   python main.py
   ```

### Step 3: Outputs
1. **Attachments Folder**: Attachments will be saved in a folder named `Attachments {Tricount Title}`.
2. **Excel File**: Transactions will be saved in a file named `Transactions {Tricount Title}.xlsx`.