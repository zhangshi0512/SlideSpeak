# SlideSpeak - Text to PPT & Speech Generator

This project is a Python-based AI tool that does two things: Converting text query into Powerpoint and speech transcript, and converting speech transcript into audio files per slide for rehearsal.

It leverages local Large Language Models (LLMs) served by Ollama to generate outline and content for each presentation slide, and incorporates Local Text to Speech (TTS) model to convert the generated speech transcript into audio files.

## Prerequisites

Before running SlideSpeak, ensure you have the following installed and set up:

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
    - SlideSpeak uses the `qwen2.5:7b` Ollama models. You need to pull these models from Ollama.
    - Run the following commands in your terminal:
      ```bash
      ollama pull qwen2.5:7b
      ```

## Installation

1.  **Clone the repository** (if you haven't already):

    ```bash
    git clone [repository_url]
    cd SlideSpeak
    ```

2.  **Install Python packages**:

    ```bash
    pip install python-pptx requests pywin32 kokoro soundfile numpy
    ```

3.  **Pull Ollama models**:

    ```bash
    ollama pull qwen2.5:7b
    ```

4.  **Kokoro TTS Models**:
    - Download the Kokoro TTS model files and place them in the root directory of the project.
    - Download `kokoro-v1.0.onnx` from [https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx](https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx) and `voices-v1.0.bin` from [https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin](https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin).

## Running the Application

You can run SlideSpeak in two ways:

1.  **Using the Graphical User Interface (GUI)**:

    - Run the `gui.py` script to launch the GUI application:
      ```bash
      python gui.py
      ```
    - Enter comma-separated topics in the GUI and press Enter to generate the PPTX presentation and speech transcript.
    - After the presentation is generated, you can find it in the project directory as `PPT.pptx`.
    - The presentation outline and speech transcript are saved in the output directory.
    - Then the interface of speech to audio conversion would popup provides user two choices:
      - **text2audio_kokoro (Best Result)**: This option converts the generated speech transcript into a series of audio files (based on the number of slides) using the Kokoro TTS model.
      - **text2audio_pyttsx3 (Fastest Result)**: This option converts the generated speech transcript into a series of audio files (based on the number of slides) using the pyttsx3 library.

2.  **Using the Command Line Interface (CLI)**:
    - Run the `main.py` script to generate a PPTX presentation with a predefined list of topics:
      ```bash
      python main.py
      ```
    - The generated PPTX file (`PPT.pptx`) will be saved in the project directory.

## Notes

- **Model Selection**: The Ollama models used in `gpt.py` (`qwen2.5:7b`) can be modified in these files if you wish to use different models.
- **Error Handling**: Basic error handling is implemented, but further improvements can be added for more robust performance.
- **Image Generation**: The current version uses Ollama to generate image prompts instead of downloading images directly. The image prompt functionality is integrated but may require further development to fully utilize generated prompts for image insertion into the PPTX.

Enjoy using SlideSpeak to quickly create PowerPoint presentations!
