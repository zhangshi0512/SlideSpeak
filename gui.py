import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import shutil
import os
import sys
import threading
import json
import pdf2final_list
import dictToPpt

class PresentSmartGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SlideSpeak - AI Presentation Generator")
        self.root.configure(bg='#f5f5f5')
        self.root.geometry('800x600')
        
        # Create themed widgets
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', font=('Arial', 12), pady=5)
        self.style.configure('TLabel', font=('Arial', 12), background='#f5f5f5')
        self.style.configure('Header.TLabel', font=('Arial', 16, 'bold'), background='#f5f5f5')
        self.style.configure('TFrame', background='#f5f5f5')
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = ttk.Label(main_frame, text="PresentSmart - AI PowerPoint Generator", style='Header.TLabel')
        header_label.pack(pady=(0, 20))
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Presentation Topics", padding="10 10 10 10")
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        instruction_label = ttk.Label(input_frame, 
                                     text="Enter topics separated by commas (e.g., 'AI Ethics, Quantum Computing')")
        instruction_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.topics_entry = tk.Text(input_frame, height=3, width=50, font=('Arial', 12))
        self.topics_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Options section
        options_frame = ttk.LabelFrame(main_frame, text="Generation Options", padding="10 10 10 10")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # LLM model selection
        model_frame = ttk.Frame(options_frame)
        model_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(model_frame, text="Content Generation Model:").pack(side=tk.LEFT)
        
        self.model_var = tk.StringVar(value="qwen2.5:3b")
        model_dropdown = ttk.Combobox(model_frame, textvariable=self.model_var, 
                                      values=["qwen2.5:3b", "erwan2/DeepSeek-Janus-Pro-7B"], 
                                      state="readonly", width=25)
        model_dropdown.pack(side=tk.LEFT, padx=(10, 0))
        
        # Save location
        save_frame = ttk.Frame(options_frame)
        save_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(save_frame, text="Save presentation to:").pack(side=tk.LEFT)
        
        self.save_path_var = tk.StringVar(value=os.path.join(os.getcwd(), "PPT.pptx"))
        save_entry = ttk.Entry(save_frame, textvariable=self.save_path_var, width=50)
        save_entry.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        
        browse_button = ttk.Button(save_frame, text="Browse", command=self.browse_save_location)
        browse_button.pack(side=tk.LEFT)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.generate_button = ttk.Button(button_frame, text="Generate Presentation", 
                                         command=self.generate_presentation)
        self.generate_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.tts_button = ttk.Button(button_frame, text="Generate TTS Audio", 
                                    command=self.open_tts_selector, state=tk.DISABLED)
        self.tts_button.pack(side=tk.LEFT)
        
        # Log and status area
        log_frame = ttk.LabelFrame(main_frame, text="Status Log", padding="10 10 10 10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD, 
                                                font=('Consolas', 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
        
    def browse_save_location(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension='.pptx',
            filetypes=[('PowerPoint files', '*.pptx'), ('All files', '*.*')],
            title="Save Presentation As"
        )
        if file_path:
            self.save_path_var.set(file_path)
            
    def generate_presentation(self):
        topics = self.topics_entry.get("1.0", tk.END).strip()
        if not topics:
            messagebox.showerror("Error", "Please enter at least one topic.")
            return
            
        # Disable UI elements during processing
        self.generate_button.config(state=tk.DISABLED)
        self.status_var.set("Generating presentation...")
        
        # Start processing in a separate thread to keep UI responsive
        threading.Thread(target=self._generate_presentation_thread, args=(topics,), daemon=True).start()
    
    def _generate_presentation_thread(self, topics):
        try:
            self.log("Starting presentation generation...")
            
            # Parse topics
            if "," in topics:
                topic_list = [t.strip() for t in topics.split(",")]
            else:
                topic_list = [topics.strip()]
                
            self.log(f"Processing topics: {', '.join(topic_list)}")
            
            # Check if Ollama is running
            try:
                # Call the process function
                self.log("Generating content with Ollama...")
                result = pdf2final_list.process(topic_list[0])
                
                self.log("Creating PowerPoint presentation...")
                enriched_outline = result["enriched_outline"]
                speech_text = result["speech_text"]
                
                # Create output directory if it doesn't exist
                os.makedirs("./output", exist_ok=True)
                
                # Save outline and speech to files
                with open("./output/enriched_outline.json", "w", encoding="utf-8") as file:
                    json.dump(enriched_outline, file, ensure_ascii=False, indent=4)
                
                with open("./output/presentation_speech.md", "w", encoding="utf-8") as file:
                    file.write(speech_text)
                
                # Create the PowerPoint
                dictToPpt.dictToPpt(enriched_outline, speech_text)
                
                # Copy to user's desired location if different from default
                target_path = self.save_path_var.get()
                if target_path != os.path.join(os.getcwd(), "PPT.pptx"):
                    shutil.copy("PPT.pptx", target_path)
                
                self.log(f"Presentation saved to: {target_path}")
                
                # Enable TTS button now that we have a speech script
                self.root.after(0, lambda: self.tts_button.config(state=tk.NORMAL))
                
                # Show success message
                messagebox.showinfo("Success", "Presentation generated successfully!")
                
                # Offer to open the presentation
                if messagebox.askyesno("Open Presentation", "Would you like to open the presentation now?"):
                    os.startfile(target_path)
                
            except Exception as e:
                self.log(f"Error: {str(e)}")
                messagebox.showerror("Error", f"An error occurred during generation: {str(e)}")
        
        finally:
            # Re-enable UI elements
            self.root.after(0, lambda: self.generate_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.status_var.set("Ready"))
    
    def open_tts_selector(self):
        """Open the TTS selector dialog to choose between pyttsx3 and Kokoro TTS engines"""
        tts_window = tk.Toplevel(self.root)
        tts_window.title("Select TTS Engine")
        tts_window.geometry("300x150")
        tts_window.transient(self.root)
        tts_window.grab_set()
        
        # Center frame with options
        frame = ttk.Frame(tts_window, padding="20 20 20 20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        label = ttk.Label(frame, text="Which TTS engine do you want to use?")
        label.pack(padx=10, pady=10)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        btn_pyttsx3 = ttk.Button(button_frame, text="pyttsx3 (Local TTS)", 
                                 command=lambda: self.launch_tts_engine("pyttsx3"))
        btn_pyttsx3.pack(side=tk.LEFT, padx=(0, 5), pady=5, expand=True, fill=tk.X)
        
        btn_kokoro = ttk.Button(button_frame, text="Kokoro (Neural TTS)", 
                               command=lambda: self.launch_tts_engine("kokoro"))
        btn_kokoro.pack(side=tk.LEFT, padx=(5, 0), pady=5, expand=True, fill=tk.X)
    
    def launch_tts_engine(self, engine_type):
        """Launch the selected TTS engine"""
        try:
            if engine_type == "pyttsx3":
                script_path = "text2audio_pyttsx3.py"
            else:
                script_path = "text2audio_kokoro.py"
                
            if os.path.exists(script_path):
                self.log(f"Launching {engine_type} TTS engine...")
                os.system(f"python {script_path}")
            else:
                messagebox.showerror("Error", f"Could not find {script_path}")
                self.log(f"Error: Could not find {script_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch TTS engine: {str(e)}")
            self.log(f"Error launching TTS engine: {str(e)}")

def main():
    root = tk.Tk()
    app = PresentSmartGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()