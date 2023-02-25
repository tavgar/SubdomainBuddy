import requests
import argparse
import concurrent.futures
import dns.resolver
import threading
import time

def check_subdomain(subdomain, Thread=True):
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
    try:
        response = requests.get(url)
        if response.status_code == 404:
            print(f"404 error found for {subdomain}")
            # Perform a DNS lookup for the subdomain
            try:
                answers = dns.resolver.resolve(subdomain)
                for rdata in answers:
                    if isinstance(rdata, dns.rdtypes.ANY.CNAME):
                        print(f"CNAME record found for {subdomain}: {rdata.target}")
                    else:
                        print(f"DNS resolution for {subdomain}: {rdata}")
            except:
                print(f"Unable to perform DNS resolution for {subdomain}")
        else:
            print(f"Response code for {subdomain}: {response.status_code}")
    except:
        print(f"Unable to connect to {url}")

    if(Thread == False):
       print("_"*50)
def threaded_check_subdomains(subdomains):
    threads = []
    for subdomain in subdomains:
        t = threading.Thread(target=check_subdomain, args=(subdomain,))
        t.start()
        threads.append(t)
        time.sleep(1) # Add a 1-second delay between requests to avoid overwhelming the server

    for t in threads:
        t.join()

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
        # Divide subdomains into batches of 10 and process each batch with a thread
        with concurrent.futures.ThreadPoolExecutor() as executor:
            batch_size = 10
            batches = [subdomains[i:i + batch_size] for i in range(0, len(subdomains), batch_size)]
            results = executor.map(threaded_check_subdomains, batches)
    else:
        for subdomain in subdomains:
            check_subdomain(subdomain)
