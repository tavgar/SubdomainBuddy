import requests
import argparse
import concurrent.futures
import dns.resolver
import threading
import time

import subprocess

def nslookup(subdomain):
    # Call the nslookup command to perform a DNS lookup for the subdomain
    process = subprocess.Popen(['nslookup', subdomain], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    # Check if the nslookup command returned an error
    if error:
        print(f"Error running nslookup for {subdomain}: {error.decode()}")
        return []

    # Parse the output of the nslookup command to get the DNS records
    lines = output.decode().split('\n')
    records = []
    for line in lines:
        if line.startswith('Name:'):
            records.append(line.strip().replace('Name:', ''))
        elif line.startswith('Address:'):
            records.append(line.strip().replace('Address:', ''))

    # Return the DNS records
    return records

def check_subdomain(subdomain, thread=True):
    subdomain = subdomain.strip()

    # Determine whether the URL should be http or https
    url = f"http://{subdomain}"
    try:
        response = requests.head(url)
        if response.status_code == 405:
            url = f"https://{subdomain}"
    except:
        url = f"https://{subdomain}"

    # Perform a DNS lookup for the subdomain
    try:
        answers = dns.resolver.resolve(subdomain)
        for rdata in answers:
            if isinstance(rdata, dns.rdtypes.ANY.CNAME):
                print(f"CNAME record found for {subdomain}: {rdata.target}")
            else:
                print(f"DNS resolution for {subdomain}: {rdata}")
    except:
        print(f"No DNS resolution found for {subdomain}")
        answers = nslookup(subdomain)
        if len(answers) > 0:
            for record in answers:
                print(f"NS lookup for {subdomain}: {record}")
        else:
            print(f"No NS lookup found for {subdomain}")

    # Make the request to the determined URL
    try:
        response = requests.get(url)
        if response.status_code == 404:
            print(f"404 error found for {subdomain}")
            answers = nslookup(subdomain)
            if len(answers) > 0:
                for record in answers:
                    print(f"NS lookup for {subdomain}: {record}")
            else:
                print(f"No NS lookup found for {subdomain}")
        else:
            print(f"Response code for {subdomain}: {response.status_code}")
    except:
        print(f"Unable to connect to {url}")

    if not thread:
        print("_" * 50)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check for subdomain takeover')
    parser.add_argument('--file', dest='file', help='The file containing a list of subdomains', required=False)
    parser.add_argument('--thready', dest='thready', help='Use threading instead of multiprocessing', action='store_true', required=False)
    args = parser.parse_args()

    # Read the file of subdomains
    subdomains_file = args.file
    with open(subdomains_file, "r") as file:
        subdomains = file.readlines()
        print("_"*50)

    if args.thready:
        # Define a function to process each batch of subdomains with a thread
        def threaded_check_subdomains(subdomains):
            for subdomain in subdomains:
                check_subdomain(subdomain.strip(), thread=True)

        # Divide subdomains into batches of 10 and process each batch with a thread
        with concurrent.futures.ThreadPoolExecutor() as executor:
            batch_size = 10
            batches = [subdomains[i:i + batch_size] for i in range(0, len(subdomains), batch_size)]
            results = executor.map(threaded_check_subdomains, batches)
     else:
            for subdomain in subdomains:
                check_subdomain(subdomain)
