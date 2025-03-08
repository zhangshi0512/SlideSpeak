import requests
import json


def gpt_summarise(system, text):
    url = "http://localhost:11434/api/chat"
    data = {
        "model": "qwen2.5:7b",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": text}
        ],
        "stream": False  # Disable streaming for simplicity
    }
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()['message']['content']
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama API: {e}")
        return "Error: Could not get summary from Ollama"
    return response['message']['content']
