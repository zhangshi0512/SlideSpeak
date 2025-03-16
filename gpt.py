import requests, json

def gpt_summarise(system, text, model="qwen2.5:7b"):
    """
    Process text using the Ollama API.
    
    Args:
        system (str): System message or instructions
        text (str): User text to process
        model (str): Model name to use (defaults to "qwen2.5:7b")
        
    Returns:
        str: Response content from the model
    """
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": model,
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
        return f"Error: Could not get summary from Ollama using model {model}: {str(e)}"