import os
import json
import requests

def load_env_api_key():
    # Attempt to load NVIDIA_API_KEY from local .env file
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("NVIDIA_API_KEY="):
                    return line.split("=", 1)[1].strip("'\"")
    return os.environ.get("NVIDIA_API_KEY")

def main():
    api_key = load_env_api_key()
    if not api_key:
        print("Error: NVIDIA_API_KEY is not set.")
        print("Please set it in your environment or append it to your .env file:")
        print("NVIDIA_API_KEY=your_api_key_here")
        return

    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "nvidia/nemotron-3-ultra-550b-a55b",
        "messages": [
            {"role": "user", "content": "Explain the advantages of hybrid Mamba-Transformer architectures."}
        ],
        "temperature": 1,
        "top_p": 0.95,
        "max_tokens": 4096,
        "stream": True
    }
    
    print("Sending request to NVIDIA Nemotron-3 Ultra 550B API...")
    try:
        response = requests.post(url, headers=headers, json=payload, stream=True)
        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            return
            
        print("\nResponse:")
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8').strip()
                if decoded_line.startswith("data:"):
                    data_str = decoded_line[5:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        data_json = json.loads(data_str)
                        choices = data_json.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {})
                            
                            # Nemotron models support reasoning/thinking
                            reasoning = delta.get("reasoning_content")
                            if reasoning:
                                print(reasoning, end="", flush=True)
                                
                            content = delta.get("content")
                            if content:
                                print(content, end="", flush=True)
                    except json.JSONDecodeError:
                        pass
        print()
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    main()
