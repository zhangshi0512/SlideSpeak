import pdf2final_list
import dictToPpt
import json
import tkinter as tk
import subprocess
import os

# Create the output directory if it doesn't exist
os.makedirs("./output", exist_ok=True)

# 1) Generate the transcript, as you already do:
result = pdf2final_list.process("claude vs gpt")

enriched_outline = result["enriched_outline"]
speech_text = result["speech_text"]

outline_path = "./output/enriched_outline.json"
speech_text_path = "./output/presentation_speech.md"

with open(outline_path, "w", encoding="utf-8") as file:
    json.dump(enriched_outline, file, ensure_ascii=False, indent=4)

with open(speech_text_path, "w", encoding="utf-8") as file:
    file.write(speech_text)

dictToPpt.dictToPpt(enriched_outline, speech_text)
print("*" * 18)
print("Transcript has been generated and saved.")

# 2) Show a small GUI to pick TTS engine:


def open_pyttsx3_gui():
    """
    Launch the pyttsx3-based script in a new process.
    """
    script_path = "text2audio_pyttsx3.py"  # Adjust as needed
    if os.path.exists(script_path):
        subprocess.Popen(["python", script_path])
    else:
        print(f"Could not find {script_path}")


def open_kokoro_gui():
    """
    Launch the Kokoro-based script in a new process.
    """
    script_path = "text2audio_kokoro.py"  # Adjust as needed
    if os.path.exists(script_path):
        subprocess.Popen(["python", script_path])
    else:
        print(f"Could not find {script_path}")


root = tk.Tk()
root.title("Select TTS Engine")

label = tk.Label(root, text="Which TTS engine do you want to use?")
label.pack(padx=10, pady=10)

btn_pyttsx3 = tk.Button(root, text="pyttsx3 GUI", command=open_pyttsx3_gui)
btn_pyttsx3.pack(padx=10, pady=5)

btn_kokoro = tk.Button(root, text="Kokoro GUI", command=open_kokoro_gui)
btn_kokoro.pack(padx=10, pady=5)

root.mainloop()