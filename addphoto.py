import requests
import json
import os
import glob

# function to generate image prompts using Ollama via HTTP API


def get_images(query, n):
    prompts = []
    url = "http://localhost:11434/api/chat"
    headers = {'Content-Type': 'application/json'}

    for _ in range(n):
        try:
            data = {
                "model": "erwan2/DeepSeek-Janus-Pro-7B",
                "messages": [
                    {'role': 'user', 'content': f"Generate a creative and descriptive image prompt for the topic: {query}"}
                ],
                "stream": False  # Disable streaming for simplicity
            }
            response = requests.post(
                url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            prompts.append(response.json()['message']['content'])
        except requests.exceptions.RequestException as e:
            print(f"Error generating image prompt from Ollama API: {e}")
            prompts.append(f"Error generating prompt for: {query}")
    return prompts

# function to empty the images folder (now a placeholder)


def empty_images():
    print("empty_images() function is now a placeholder.")
    pass
