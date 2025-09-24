import requests
import time
import concurrent.futures

# --- Configuration ---
# The URL of the API endpoint you want to test
URL = "http://gus:6767/analyze"

# The number of concurrent workers (simulated users)
NUM_WORKERS = 200

# The total number of requests to send
TOTAL_REQUESTS = 10000

# The payload to send with each POST request
PAYLOAD = {
    "text": "An old silent pond...\nA frog jumps into the pond—\nsplash! Silence again."
}

# --- Load Test Logic ---

def send_request(session, url):
    """Sends a single POST request and returns the status code."""
    try:
        with session.post(url, json=PAYLOAD, timeout=10) as response:
            return response.status_code
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def run_load_test():
    """Runs the load test and prints the results."""
    print(f"Starting load test...")
    print(f"Target URL: {URL}")
    print(f"Total Requests: {TOTAL_REQUESTS}")
    print(f"Concurrent Workers: {NUM_WORKERS}\n")

    successful_requests = 0
    failed_requests = 0
    start_time = time.time()

    # Use a session object for connection pooling
    with requests.Session() as session:
        # Use ThreadPoolExecutor to send requests concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            # Create a future for each request
            futures = [executor.submit(send_request, session, URL) for _ in range(TOTAL_REQUESTS)]

            # Process results as they complete
            for future in concurrent.futures.as_completed(futures):
                status_code = future.result()
                if status_code == 200:
                    successful_requests += 1
                else:
                    failed_requests += 1

    end_time = time.time()
    duration = end_time - start_time

    print("\n--- Test Results ---")
    print(f"Total time taken: {duration:.2f} seconds")
    print(f"Successful requests: {successful_requests} (Status 200)")
    print(f"Failed requests: {failed_requests}")

    if duration > 0:
        requests_per_second = successful_requests / duration
        print(f"Requests per second: {requests_per_second:.2f}")
    else:
        print("Test completed too quickly to measure requests per second.")

if __name__ == "__main__": 
    run_load_test()