import requests, json



def gpt_summarise(system, text):
    print("API calls")

    api_key = "SRSNR19-JBZMJTZ-NJ0TSSA-WF6FN4G"
    base_url = "http://localhost:3001/api/v1"
    workspace_slug = "jyc"

    chat_url = f"{base_url}/workspace/{workspace_slug}/chat"

    url = chat_url
    # url = "http://localhost:11434/api/chat"

    # payload = {
    #     "model": "qwen2.5:7b",
    #     "messages": [
    #         {"role": "system", "content": system},
    #         {"role": "user", "content": text}
    #     ],
    #     "stream": False
    # }

    # headers = {'Content-Type': 'application/json'}  

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key
    }

    data ={
        "message": system + text,
        # "message": "hello there!",
        "mode": "chat",
        "sessionId": "ppt_generate",
        "attachments": []
    }
    print("start to try!")

    try:
        response = requests.post(url, headers=headers, json=data)
        # print("posted")
        response.raise_for_status()
        
        # return response.json()['message']['content']
        # print(response.json()['textResponse'])
        return response.json()['textResponse']
            
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
    