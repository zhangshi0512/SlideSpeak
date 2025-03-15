#!/usr/bin/env python3
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pyttsx3
import wave


def text_to_speech(text, output_file="output.wav", rate=150, voice_id=None, volume=1.0):
    """
    Convert the provided text to speech using pyttsx3 and save as a WAV file.
    """
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)
    engine.setProperty('volume', volume)  # Set volume (0.0 to 1.0)
    voices = engine.getProperty('voices')
    if voice_id is not None and 0 <= voice_id < len(voices):
        engine.setProperty('voice', voices[voice_id].id)
    engine.save_to_file(text, output_file)
    engine.runAndWait()
    print(f"Audio file saved as: {output_file}")


def process_slide(slide_text, slide_number, output_dir, rate=150, voice_id=None, volume=1.0):
    """
    Process a slide by:
      - Removing stray [SLIDE CHANGE] markers.
      - Splitting text at each [PAUSE=1] marker.
      - Generating a temporary WAV file for each segment via text_to_speech().
      - Reading the WAV data using the wave module.
      - Generating a 0.7-second silence based on the audio parameters.
      - Concatenating segments (with inserted silence) and saving the final WAV file.
    """
    slide_text = slide_text.replace("[SLIDE CHANGE]", "")
    segments = re.split(r'\[PAUSE=1\]', slide_text)
    segments = [seg.strip() for seg in segments if seg.strip()]
    segment_data_list = []
    params = None
    for i, seg in enumerate(segments):
        temp_filename = os.path.join(
            output_dir, f"temp_slide{slide_number}_seg{i}.wav")
        text_to_speech(seg, output_file=temp_filename,
                       rate=rate, voice_id=voice_id, volume=volume)
        with wave.open(temp_filename, 'rb') as wav_in:
            if params is None:
                params = wav_in.getparams()
            data = wav_in.readframes(wav_in.getnframes())
            segment_data_list.append(data)
        os.remove(temp_filename)
    silence_frames = int(params.framerate * 0.7)
    silence_data = b'\x00' * \
        (silence_frames * params.sampwidth * params.nchannels)
    merged_data = b""
    for j, data in enumerate(segment_data_list):
        merged_data += data
        if j < len(segment_data_list) - 1:
            merged_data += silence_data
    output_filename = os.path.join(output_dir, f"slide{slide_number}.wav")
    with wave.open(output_filename, 'wb') as wav_out:
        wav_out.setparams(params)
        wav_out.writeframes(merged_data)
    print(f"Saved slide {slide_number} audio to: {output_filename}")


def process_transcript(transcript_file, output_dir, rate=150, voice_id=None, volume=1.0):
    """
    Reads a transcript file, splits it into slides based on the [SLIDE CHANGE] marker,
    and processes each slide into a separate audio file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(transcript_file, "r", encoding="utf-8") as f:
        transcript = f.read()
    slides = re.split(r'\[SLIDE CHANGE\]', transcript)
    for i, slide in enumerate(slides, start=1):
        slide = slide.strip()
        if slide:
            process_slide(slide, i, output_dir, rate=rate,
                          voice_id=voice_id, volume=volume)


class TTSApp:
    def __init__(self, master):
        self.master = master
        master.title("pyttsx3 TTS GUI")

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

        # Voice selection dropdown: retrieve available voices from pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        self.voice_options = []
        for idx, voice in enumerate(voices):
            option = f"{idx}: {voice.name}"
            self.voice_options.append(option)
        engine.stop()
        self.label_voice = tk.Label(master, text="Voice:")
        self.label_voice.grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.voice_var = tk.StringVar(master)
        if self.voice_options:
            self.voice_var.set(self.voice_options[0])
        self.dropdown_voice = ttk.Combobox(
            master, textvariable=self.voice_var, values=self.voice_options, state="readonly", width=50)
        self.dropdown_voice.grid(row=2, column=1, padx=5, pady=5)

        # Rate (speed) entry
        self.label_rate = tk.Label(master, text="Rate (words per minute):")
        self.label_rate.grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_rate = tk.Entry(master)
        self.entry_rate.insert(0, "150")
        self.entry_rate.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Volume entry
        self.label_volume = tk.Label(master, text="Volume (0.0 to 1.0):")
        self.label_volume.grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.entry_volume = tk.Entry(master)
        self.entry_volume.insert(0, "1.0")
        self.entry_volume.grid(row=4, column=1, padx=5, pady=5, sticky="w")

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
        try:
            rate = int(self.entry_rate.get().strip())
            volume = float(self.entry_volume.get().strip())
        except ValueError:
            messagebox.showerror(
                "Input Error", "Rate must be an integer and Volume must be a float.")
            return

        if not transcript_file or not os.path.isfile(transcript_file):
            messagebox.showerror(
                "File Error", "Please select a valid transcript file.")
            return
        if not output_dir:
            messagebox.showerror(
                "Directory Error", "Please select a valid output directory.")
            return

        # Get voice_id from selected option
        selected_voice = self.voice_var.get()
        try:
            voice_id = int(selected_voice.split(":")[0])
        except Exception as e:
            messagebox.showerror(
                "Voice Error", f"Error parsing selected voice: {e}")
            return

        self.status_text.set("Processing transcript...")
        self.master.update()
        try:
            process_transcript(transcript_file, output_dir,
                               rate=rate, voice_id=voice_id, volume=volume)
            self.status_text.set("TTS processing completed successfully!")
        except Exception as e:
            messagebox.showerror("Processing Error",
                                 f"Error during TTS processing: {e}")
            self.status_text.set("Error during processing.")


if __name__ == "__main__":
    root = tk.Tk()
    app = TTSApp(root)
    root.mainloop()
