import requests
import argparse
import concurrent.futures
import dns.resolver

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

    # Perform a DNS lookup for the subdomain
    try:
        answers = dns.resolver.resolve(subdomain)
        print(f"DNS resolution for {subdomain}: {[str(rdata) for rdata in answers]}")
    except:
        print(f"Unable to perform DNS resolution for {subdomain}")

    # Make the request to the determined URL
    try:
        response = requests.get(url)
        if response.status_code == 404:
            print(f"404 error found for {subdomain}")
        else:
            print(f"Response code for {subdomain}: {response.status_code}")
    except:
        print(f"Unable to connect to {url}")

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
