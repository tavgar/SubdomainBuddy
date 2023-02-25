# Subdomain Buddy

Subdomain Buddy is a Python script that checks a list of subdomains for potential subdomain takeover. It performs a GET request on each subdomain and checks if it returns a 404 error. If a 404 error is found, it performs an nslookup on the subdomain to check if it is pointing to a valid IP address. 

## Usage

Subdomain Buddy requires a file containing a list of subdomains to check. You can provide the path to the file using the `--file` parameter. If the parameter is not provided, the script will prompt you to enter the path to the file.
You can use `--thready` to make it faster otherwise with a medium scope take a nap.
To run Subdomain Buddy, use the following command:

python subdomainBuddy.py --file subdomains.txt --thready


Replace `subdomains.txt` with the path to your file containing the list of subdomains.

## Requirements

Subdomain Buddy requires the following packages:

- requests
- argparse

You can install these packages using pip:

pip install requests argparse
