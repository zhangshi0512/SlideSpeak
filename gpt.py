import requests
import json


def gpt_summarise(system, text):
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "qwen2.5:3b",
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

        # for line in response.iter_lines(decode_unicode=True):
        #     if line:
        #         try:
        #             json_data = json.loads(line)
        #             if "message" in json_data and "content" in json_data["message"]:
        #                 print(json_data["message"]["content"], end="")
        #         except json.JSONDecodeError:
        #             print(f"\nFailed to parse line: {line}")
        # print()

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama API: {e}")
        return "Error: Could not get summary from Ollama"
