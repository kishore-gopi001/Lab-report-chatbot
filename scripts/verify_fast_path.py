import requests
import json
import time

def test_fast_path():
    url = "http://127.0.0.1:8000/chat/stream"
    payload = {
        "question": "Total number of abnormal results for patient 10014354"
    }

    print(f"Testing Fast-Path Optimization...")
    print(f"Question: {payload['question']}\n")

    start_time = time.time()
    try:
        response = requests.post(url, json=payload, stream=True, timeout=30)
        
        if response.status_code != 200:
            print(f"Error: Server returned status code {response.status_code}")
            return

        print("Streaming Response:")
        first_token_time = None
        full_response = ""

        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith("data: "):
                    data = json.loads(line_str[6:])
                    
                    if data['type'] == 'status':
                        print(f"Status: {data['content']}")
                    elif data['type'] == 'token':
                        if first_token_time is None:
                            first_token_time = time.time() - start_time
                        print(data['content'], end='', flush=True)
                        full_response += data['content']
                    elif data['type'] == 'done':
                        print("\n\nStream Finished.")

        end_time = time.time()
        print(f"\nTime to first token: {first_token_time:.2f}s" if first_token_time else "\nFirst token not received")
        print(f"Total time: {end_time - start_time:.2f}s")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the FastAPI server is running.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_fast_path()
