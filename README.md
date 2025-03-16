# SlideSpeak - Text to PPT &amp; Speech Generator

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://www.python.org)
[![Ollama](https://img.shields.io/badge/Ollama-blue?logo=ollama&logoColor=white)](https://ollama.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-blue?logo=pytorch&logoColor=white)](https://pytorch.org/)

**2025 Qualcomm Technologies x Northeastern University Hackathon**
**March 15th - 16th**

**Team:** NewTeamOne

**Team members:** Yuchen Jiang, Yuchen Li, Quancheng Li, Shi Zhang, Jiangtian Han

## Table of Contents

- [Intro](#intro)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
  - [Using the Graphical User Interface (GUI)](#using-the-graphical-user-interface-gui)
  - [Using the Command Line Interface (CLI)](#using-the-command-line-interface-cli)
- [Notes](#notes)
- [License](#license)

## Intro

SlideSpeak is a Python-based AI tool designed for:

- **Converting text queries into PowerPoint presentations and speech transcripts.**
- **Converting speech transcripts into audio files per slide for presentation rehearsal.**

It utilizes local Large Language Models (LLMs) served by Ollama to generate presentation outlines and slide content. Additionally, it integrates a local Text to Speech (TTS) model to convert speech transcripts into audio files.

![application_interface](/screenshots/main_gui.jpg)

## Architecture

The following diagram illustrates the main components of SlideSpeak and their relationships:

```mermaid
graph LR
    A[main.py] --> B(pdf2final_list.py)
    A --> C(dictToPpt.py)
    A --> D[text2audio_pyttsx3.py]
    A --> E[text2audio_kokoro.py]
    B --> F(gpt.py)
    B --> G(speech_generator.py)
    C --> H[pptx library]
    F --> I[Ollama API]
    D --> J[pyttsx3 library]
    E --> K[kokoro library]

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#ccf,stroke:#333,stroke-width:2px
    style C fill:#ccf,stroke:#333,stroke-width:2px
    style D fill:#ccf,stroke:#333,stroke-width:2px
    style E fill:#ccf,stroke:#333,stroke-width:2px
    style F fill:#aaf,stroke:#333,stroke-width:2px
    style G fill:#aaf,stroke:#333,stroke-width:2px
    style H fill:#eee,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
    style I fill:#eee,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
    style J fill:#eee,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
    style K fill:#eee,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5

    subgraph Application
        A
        B
        C
        D
        E
        F
        G
    end

    subgraph Libraries/APIs
        H
        I
        J
        K
    end
```

- **`main.py`**: Orchestrates the entire process, calling other modules for transcript and outline generation, PowerPoint creation, and TTS engine selection.
- **`pdf2final_list.py`**: Handles transcript and outline generation, utilizing `gpt.py` for LLM interactions and `speech_generator.py` for speech-related functionalities.
- **`dictToPpt.py`**: Responsible for creating PowerPoint presentations using the `pptx` library.
- **`text2audio_pyttsx3.py` &amp; `text2audio_kokoro.py`**: Provide TTS engine options using `pyttsx3` and `kokoro` libraries respectively.
- **`gpt.py`**: Interacts with the Ollama API to leverage LLMs.
- **`speech_generator.py`**: Contains tasks related to speech processing.

## Prerequisites

Before running SlideSpeak, ensure the following prerequisites are met:

1.  **Ollama**:

    - Download and install Ollama from [https://ollama.com/](https://ollama.com/). Follow the installation instructions for your OS.
    - Ensure Ollama is running in the background. Verify by running `ollama list` in your terminal to see installed models.

2.  **Python**:

    - Python 3.10 or higher is required. Download from [https://www.python.org/](https://www.python.org/).

3.  **Python Packages**:

    - Install necessary packages using pip. Virtual environment is recommended.
    - Navigate to the project directory and run:
      ```bash
      pip install python-pptx requests pywin32 kokoro soundfile numpy
      ```

4.  **Ollama Models**:

    - SlideSpeak uses `qwen2.5:7b` Ollama models. Pull these models from Ollama:
      ```bash
      ollama pull qwen2.5:7b
      ```

5.  **Kokoro TTS Models**:
    - Download Kokoro TTS model files and place them in the project root directory.
    - Download `kokoro-v1.0.onnx` from [https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx](https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx)
    - Download `voices-v1.0.bin` from [https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin](https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin)

## Installation

1.  **Clone the repository**:
    ```bash
    git clone [repository_url]
    cd SlideSpeak
    ```

## Running the Application

SlideSpeak can be run in two modes:

### Using the Graphical User Interface (GUI)

1.  Run the `gui.py` script:
    ```bash
    python gui.py
    ```
2.  Enter comma-separated topics in the GUI and press Enter.
3.  Find the generated PPTX presentation as `PPT.pptx` in the project directory.
4.  Presentation outline and speech transcript are saved in the `output` directory.
5.  Choose TTS engine in the GUI:
    - **text2audio_kokoro (Best Result)**: Uses Kokoro TTS for high-quality audio.
    - **text2audio_pyttsx3 (Fastest Result)**: Uses `pyttsx3` for faster audio generation.

### Using the Command Line Interface (CLI)

1.  Run `main.py` to generate PPTX with predefined topics:
    ```bash
    python main.py
    ```
2.  The generated PPTX file (`PPT.pptx`) is saved in the project directory.

## Notes

- **Model Selection**: Modify Ollama models (`qwen2.5:7b`) in `gpt.py` if needed.

- **NPU Option**: Users can also run this application on NPU via AnythingLLM. To do this, replace `gpt.py` with the following code:

```python
import requests, json


def gpt_summarise(system, text):
    print("API calls")

    api_key = "Your api key generated from AnythingLLM Settings under Developer API"
    base_url = "http://localhost:3001/api/v1"
    workspace_slug = "the name of your workspace, all lower case"

    chat_url = f"{base_url}/workspace/{workspace_slug}/chat"

    url = chat_url

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key
    }

    data ={
        "message": system + text,
        "mode": "chat",
        "sessionId": "ppt_generate",
        "attachments": []
    }
    print("start to try!")

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        print(response.json()['textResponse'])
        return response.json()['textResponse']

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama API: {e}")
        return "Error: Could not get summary from Ollama"

```

- **Error Handling**: Basic error handling is implemented; further improvements are possible.
- **Image Generation**: Current version uses Ollama for image prompts. Image prompt functionality is integrated but needs further development for full PPTX image insertion.

## License

SlideSpeak is licensed under the [Apache License 2.0](LICENSE). See the `LICENSE` file for more details.
