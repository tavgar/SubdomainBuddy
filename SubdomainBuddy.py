import requests
import subprocess
import argparse
import concurrent.futures

def check_subdomain(subdomain):
    subdomain = subdomain.strip()  # Remove any trailing whitespace

    # Determine whether the URL should be http or https
    url = f"http://{subdomain}"
    try:
        response = requests.head(url)
        if response.status_code == 405:  # Method Not Allowed error
            url = f"https://{subdomain}"
    except:
        url = f"https://{subdomain}"

    # Make the request to the determined URL
    output = subprocess.check_output(["nslookup", subdomain])
    try:
        response = requests.get(url)
        if response.status_code == 404:
            print(f"404 error found for {subdomain}")
            try:
                output = subprocess.check_output(["nslookup", subdomain])
                print(f"nslookup for {subdomain}: {output.decode('utf-8').strip()}")
            except subprocess.CalledProcessError:
                print(f"Unable to perform nslookup for {subdomain}")
        else:
            print(f"Response code for {subdomain}: {response.status_code}")
    except:
            print(f"nslookup for {subdomain}: {output.decode('utf-8').strip()}")

    print("-" * 50)  # Print a line between each subdomain

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check for subdomain takeover')
    parser.add_argument('--file', dest='file', help='The file containing a list of subdomains', required=False)
    parser.add_argument('--thready', dest='thready', help='Use threading instead of multiprocessing', action='store_true', required=False)
    args = parser.parse_args()

    # Read the file of subdomains
    subdomains_file = args.file
    with open(subdomains_file, "r") as file:
        subdomains = file.readlines()

    # Create a concurrent executor to execute the subdomain checks in parallel
    if args.thready:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(check_subdomain, subdomains)
    else:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(check_subdomain, subdomains)
