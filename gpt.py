import requests
import json


def gpt_summarise(system, text, device_type="CPU"):
    if device_type == "NPU":
        print("Using NPU API")
        # need to be configurable later
        api_key = "Your api key generated from AnythingLLM Settings under Developer API"
        base_url = "http://localhost:3001/api/v1"  # need to be configurable later
        # need to be configurable later
        workspace_slug = "the name of your workspace, all lower case"

        chat_url = f"{base_url}/workspace/{workspace_slug}/chat"
        url = chat_url
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key
        }
        data = {
            "message": system + text,
            "mode": "chat",
            "sessionId": "ppt_generate",
            "attachments": []
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()['textResponse']
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with NPU API: {e}")
            return "Error: Could not get summary from NPU API"

    else:  # default to CPU
        print("Using CPU API")
        url = "http://localhost:11434/api/chat"
        payload = {
            "model": "qwen2.5:7b",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": text}
            ],
            "stream": False
        }
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()['message']['content']
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Ollama API: {e}")
            return "Error: Could not get summary from Ollama"
