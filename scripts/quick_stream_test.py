"""
Quick test script to verify the /chat/stream endpoint is producing output
"""
import requests
import json
import time

STREAM_ENDPOINT = "http://127.0.0.1:8000/chat/stream"

def test_stream():
    payload = {"question": "What is glucose?"}
    
    print("Testing /chat/stream endpoint...")
    print(f"Question: {payload['question']}")
    print("-" * 60)
    
    try:
        start = time.time()
        response = requests.post(
            STREAM_ENDPOINT,
            json=payload,
            stream=True,
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"ERROR: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        print("Connected! Waiting for events...\n")
        
        events_count = 0
        tokens_count = 0
        first_token_time = None
        output_text = []
        
        for line in response.iter_lines():
            if not line:
                continue
            
            line_str = line.decode('utf-8')
            
            if line_str.startswith("data: "):
                data_str = line_str[6:]
                
                try:
                    event = json.loads(data_str)
                    events_count += 1
                    
                    event_type = event.get("type")
                    content = event.get("content", "")
                    
                    if event_type == "status":
                        elapsed = time.time() - start
                        print(f"[{elapsed:.1f}s] STATUS: {content}")
                    
                    elif event_type == "token":
                        if first_token_time is None:
                            first_token_time = time.time() - start
                            print(f"\n[{first_token_time:.1f}s] FIRST TOKEN RECEIVED!")
                            print("-" * 60)
                            print("OUTPUT: ", end="", flush=True)
                        
                        print(content, end="", flush=True)
                        output_text.append(content)
                        tokens_count += 1
                    
                    elif event_type == "done":
                        elapsed = time.time() - start
                        print(f"\n\n[{elapsed:.1f}s] STREAM COMPLETED")
                        break
                        
                except json.JSONDecodeError as e:
                    print(f"Warning: Could not parse: {data_str[:50]}...")
        
        elapsed = time.time() - start
        full_output = "".join(output_text)
        
        print("\n" + "=" * 60)
        print("RESULTS:")
        print("=" * 60)
        print(f"Total time: {elapsed:.1f}s")
        print(f"Events received: {events_count}")
        print(f"Tokens received: {tokens_count}")
        print(f"Time to first token: {first_token_time:.1f}s" if first_token_time else "No tokens received")
        print(f"Output length: {len(full_output)} characters")
        
        if tokens_count == 0:
            print("\n❌ PROBLEM: No tokens were received!")
            print("The endpoint is still not producing output.")
            return False
        else:
            print("\n✅ SUCCESS: Output is being produced!")
            return True
        
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out after 120s")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_stream()
    exit(0 if success else 1)
