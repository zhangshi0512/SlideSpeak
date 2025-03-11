import pyttsx3


def text_to_speech(text, output_file="output.wav", rate=150, voice_id=None):
    engine = pyttsx3.init()

    # Adjust the speaking rate
    engine.setProperty('rate', rate)

    # Select a voice (if needed)
    voices = engine.getProperty('voices')
    if voice_id is not None and 0 <= voice_id < len(voices):
        engine.setProperty('voice', voices[voice_id].id)

    # Save to a WAV file
    engine.save_to_file(text, output_file)
    engine.runAndWait()

    print(f"Audio file saved as: {output_file}")


# Example Usage
if __name__ == "__main__":
    text = "Hello! This is a test for text-to-speech conversion using Python."
    text_to_speech(text, "speech_output.wav", rate=160, voice_id=0)
