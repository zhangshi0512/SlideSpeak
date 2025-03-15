#!/usr/bin/env python3
import os
import re
import argparse
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import soundfile as sf

# Import KPipeline from the official Kokoro TTS package.
from kokoro import KPipeline

# ---------------------------
# Define voice options based on your context.
VOICE_OPTIONS = [
    # American English Voices - Female
    "af_alloy", "af_aoede", "af_bella", "af_jessica", "af_kore", "af_nicole", "af_nova", "af_river", "af_sarah", "af_sky",
    # American English Voices - Male
    "am_adam", "am_echo", "am_eric", "am_fenrir", "am_liam", "am_michael", "am_onyx", "am_puck",
    # British English Voices - Female
    "bf_alice", "bf_emma", "bf_isabella", "bf_lily",
    # British English Voices - Male
    "bm_daniel", "bm_fable", "bm_george", "bm_lewis",
    # Special Voices
    "ff_siwis",  # French Female
    "hf_alpha"   # High-pitched Voice
]


def get_language_code(voice):
    """Infer language code based on the selected voice prefix."""
    if voice.startswith("af_") or voice.startswith("am_") or voice.startswith("hf_"):
        return 'a'  # American English
    elif voice.startswith("bf_") or voice.startswith("bm_"):
        return 'b'  # British English
    elif voice.startswith("ff_"):
        return 'f'  # French
    else:
        return 'a'


def text_to_speech_kokoro(text, pipeline, voice, speed):
    """
    Synthesize speech for the given text using the Kokoro TTS pipeline.
    The pipeline returns a generator yielding tuples (text, metadata, audio_segment).
    This function concatenates all audio segments and returns the full audio as a NumPy array.
    """
    generator = pipeline(
        text,
        voice=voice,
        speed=speed,
        split_pattern=r'\n+'  # Split on one or more newlines.
    )
    full_audio = np.concatenate([audio for _, _, audio in generator])
    return full_audio


def process_slide(slide_text, slide_number, output_dir, pipeline, voice, speed, gain):
    """
    Process a slide's text:
      - Remove any stray "[SLIDE CHANGE]" markers.
      - Split text at each "[PAUSE=1]" marker.
      - Synthesize each segment using the pipeline.
      - Insert 0.7 seconds of silence between segments.
      - Concatenate segments, apply gain, and save as a WAV file.
    """
    slide_text = slide_text.replace("[SLIDE CHANGE]", "")
    segments = re.split(r'\[PAUSE=1\]', slide_text)
    segments = [seg.strip() for seg in segments if seg.strip()]

    segment_audio_list = []
    for seg in segments:
        audio = text_to_speech_kokoro(seg, pipeline, voice, speed)
        segment_audio_list.append(audio)

    # Use the sample rate from pipeline configuration if available; fallback to 22050 Hz.
    sr = pipeline.config.sample_rate if hasattr(pipeline, 'config') and hasattr(
        pipeline.config, 'sample_rate') else 22050
    silence = np.zeros(int(0.7 * sr), dtype=segment_audio_list[0].dtype)

    merged_audio = []
    for i, audio in enumerate(segment_audio_list):
        merged_audio.append(audio)
        if i < len(segment_audio_list) - 1:
            merged_audio.append(silence)
    merged_audio = np.concatenate(merged_audio)

    # Apply gain (volume amplification)
    merged_audio = merged_audio * gain
    merged_audio = np.clip(merged_audio, -1.0, 1.0)

    output_filename = os.path.join(output_dir, f"slide{slide_number}.wav")
    sf.write(output_filename, merged_audio, sr)
    print(f"Saved slide {slide_number} audio to: {output_filename}")


def process_transcript(transcript_file, output_dir, pipeline, voice, speed, gain):
    """
    Read a transcript file, split it into slides using "[SLIDE CHANGE]",
    and process each slide into a separate WAV audio file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(transcript_file, "r", encoding="utf-8") as f:
        transcript = f.read()

    slides = re.split(r'\[SLIDE CHANGE\]', transcript)
    for i, slide in enumerate(slides, start=1):
        slide = slide.strip()
        if slide:
            process_slide(slide, i, output_dir, pipeline, voice, speed, gain)

# ---------------------------
# Build the GUI using Tkinter.


class TTSApp:
    def __init__(self, master):
        self.master = master
        master.title("Kokoro TTS GUI")

        # Transcript file selection
        self.label_transcript = tk.Label(master, text="Transcript File:")
        self.label_transcript.grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_transcript = tk.Entry(master, width=50)
        self.entry_transcript.grid(row=0, column=1, padx=5, pady=5)
        self.button_browse_transcript = tk.Button(
            master, text="Browse", command=self.browse_transcript)
        self.button_browse_transcript.grid(row=0, column=2, padx=5, pady=5)

        # Output directory selection
        self.label_output = tk.Label(master, text="Output Directory:")
        self.label_output.grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_output = tk.Entry(master, width=50)
        self.entry_output.grid(row=1, column=1, padx=5, pady=5)
        self.button_browse_output = tk.Button(
            master, text="Browse", command=self.browse_output)
        self.button_browse_output.grid(row=1, column=2, padx=5, pady=5)

        # Voice selection dropdown
        self.label_voice = tk.Label(master, text="Voice:")
        self.label_voice.grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.voice_var = tk.StringVar(master)
        self.voice_var.set(VOICE_OPTIONS[0])  # default voice
        self.dropdown_voice = ttk.Combobox(
            master, textvariable=self.voice_var, values=VOICE_OPTIONS, state="readonly")
        self.dropdown_voice.grid(row=2, column=1, padx=5, pady=5)

        # Speed entry
        self.label_speed = tk.Label(master, text="Speed (e.g., 1.25):")
        self.label_speed.grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_speed = tk.Entry(master)
        self.entry_speed.insert(0, "1.0")
        self.entry_speed.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Gain (Volume) entry
        self.label_gain = tk.Label(master, text="Gain (e.g., 2.0):")
        self.label_gain.grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.entry_gain = tk.Entry(master)
        self.entry_gain.insert(0, "1.0")
        self.entry_gain.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Run button
        self.button_run = tk.Button(
            master, text="Run TTS", command=self.run_tts)
        self.button_run.grid(row=5, column=1, pady=10)

        # Status output
        self.status_text = tk.StringVar()
        self.label_status = tk.Label(
            master, textvariable=self.status_text, fg="blue")
        self.label_status.grid(row=6, column=0, columnspan=3, pady=5)

    def browse_transcript(self):
        filename = filedialog.askopenfilename(title="Select Transcript File", filetypes=[(
            "Markdown Files", "*.md"), ("Text Files", "*.txt"), ("All Files", "*.*")])
        if filename:
            self.entry_transcript.delete(0, tk.END)
            self.entry_transcript.insert(0, filename)

    def browse_output(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.entry_output.delete(0, tk.END)
            self.entry_output.insert(0, directory)

    def run_tts(self):
        transcript_file = self.entry_transcript.get().strip()
        output_dir = self.entry_output.get().strip()
        voice = self.voice_var.get().strip()
        try:
            speed = float(self.entry_speed.get().strip())
            gain = float(self.entry_gain.get().strip())
        except ValueError:
            messagebox.showerror(
                "Input Error", "Speed and Gain must be numeric values.")
            return

        if not transcript_file or not os.path.isfile(transcript_file):
            messagebox.showerror(
                "File Error", "Please select a valid transcript file.")
            return
        if not output_dir:
            messagebox.showerror(
                "Directory Error", "Please select a valid output directory.")
            return

        # Infer language code based on selected voice.
        lang_code = get_language_code(voice)
        self.status_text.set("Initializing pipeline...")
        self.master.update()
        try:
            pipeline = KPipeline(lang_code=lang_code)
        except Exception as e:
            messagebox.showerror(
                "Pipeline Error", f"Error initializing pipeline: {e}")
            return

        self.status_text.set("Processing transcript...")
        self.master.update()
        try:
            process_transcript(transcript_file, output_dir,
                               pipeline, voice, speed, gain)
            self.status_text.set("TTS processing completed successfully!")
        except Exception as e:
            messagebox.showerror("Processing Error",
                                 f"Error during TTS processing: {e}")
            self.status_text.set("Error during processing.")


# ---------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = TTSApp(root)
    root.mainloop()
