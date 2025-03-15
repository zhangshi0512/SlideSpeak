# PresentSmart - PDF to PPT Generator

This project is a Python-based tool that automatically generates PowerPoint presentations from a list of topics. It leverages local Large Language Models (LLMs) served by Ollama to generate summaries and code snippets for each topic and incorporates these into a PPTX presentation.

## Prerequisites

Before running PresentSmart, ensure you have the following installed and set up:

1.  **Ollama**:

    - Download and install Ollama from [https://ollama.com/](https://ollama.com/). Follow the installation instructions for your operating system.
    - Make sure Ollama is running in the background. You can verify this by running `ollama list` in your terminal, which should list the models you have installed.

2.  **Python**:

    - Python 3.10 or higher is required. You can download Python from [https://www.python.org/](https://www.python.org/).

3.  **Python Packages**:

    - Install the necessary Python packages using pip. It is recommended to create a virtual environment for this project.
    - Navigate to the project directory in your terminal and run:
      ```bash
      pip install python-pptx requests
      ```

4.  **Ollama Models**:
    - PresentSmart uses the `qwen2.5:7b` and `erwan2/DeepSeek-Janus-Pro-7B` Ollama models. You need to pull these models from Ollama.
    - Run the following commands in your terminal:
      ```bash
      ollama pull qwen2.5:7b
      ollama pull erwan2/DeepSeek-Janus-Pro-7B
      ```

## Installation

1.  **Clone the repository** (if you haven't already):

    ```bash
    git clone [repository_url]
    cd PresentSmart
    ```

2.  **Install Python packages**:

    ```bash
    pip install python-pptx requests
    ```

3.  **Pull Ollama models**:

    ```bash
    ollama pull qwen2.5:7b
    ollama pull erwan2/DeepSeek-Janus-Pro-7B
    ```

4.  **Kokoro TTS Models**:
    - Download the Kokoro TTS model files and place them in the root directory of the project.
    - Download `kokoro-v1.0.onnx` from [https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx](https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx) and `voices-v1.0.bin` from [https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin](https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin).

## Running the Application

You can run PresentSmart in two ways:

1.  **Using the Graphical User Interface (GUI)**:

    - Run the `gui.py` script to launch the GUI application:
      ```bash
      python gui.py
      ```
    - Enter comma-separated topics in the GUI and press Enter to generate the PPTX presentation.

2.  **Using the Command Line Interface (CLI)**:
    - Run the `main.py` script to generate a PPTX presentation with a predefined list of topics:
      ```bash
      python main.py
      ```
    - The generated PPTX file (`PPT.pptx`) will be saved in the project directory.

## Notes

- **Model Selection**: The Ollama models used in `gpt.py` (`qwen2.5:7b`) and `addphoto.py` (`erwan2/DeepSeek-Janus-Pro-7B`) can be modified in these files if you wish to use different models.
- **Error Handling**: Basic error handling is implemented, but further improvements can be added for more robust performance.
- **Image Generation**: The current version uses Ollama to generate image prompts instead of downloading images directly. The image prompt functionality is integrated but may require further development to fully utilize generated prompts for image insertion into the PPTX.

Enjoy using PresentSmart to quickly create PowerPoint presentations!
