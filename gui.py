import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import shutil
import os
import sys
import threading
import json
import hashlib
import re
import pdf2final_list
import dictToPpt

class PresentSmartGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PresentSmart - AI Presentation Generator")
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
        
        # Cache status label
        self.cache_status = ttk.Label(main_frame, text="", foreground="green")
        self.cache_status.pack(pady=(0, 10))
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Presentation Topics", padding="10 10 10 10")
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        instruction_label = ttk.Label(input_frame, 
                                     text="Enter topics separated by commas (e.g., 'AI Ethics, Quantum Computing')")
        instruction_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.topics_entry = tk.Text(input_frame, height=3, width=50, font=('Arial', 12))
        self.topics_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Bind events to check cache when user stops typing
        self.topics_entry.bind("<KeyRelease>", lambda e: self.root.after(500, self.check_cache_for_topic))
        
        # Add a button to browse cached presentations
        cache_button = ttk.Button(input_frame, text="Browse Cached Presentations", command=self.browse_cache)
        cache_button.pack(anchor=tk.E, pady=(0, 5))
        
        # Options section
        options_frame = ttk.LabelFrame(main_frame, text="Generation Options", padding="10 10 10 10")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # LLM model selection
        model_frame = ttk.Frame(options_frame)
        model_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(model_frame, text="Content Generation Model:").pack(side=tk.LEFT)
        
        self.model_var = tk.StringVar(value="qwen2.5:7b")
        model_dropdown = ttk.Combobox(model_frame, textvariable=self.model_var, 
                                      values=["qwen2.5:7b", "erwan2/DeepSeek-Janus-Pro-7B"], 
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
    
    def normalize_idea_name(self, idea):
        """Normalize idea name for comparison (lowercase, remove symbols and spaces)"""
        # Convert to lowercase and remove special characters except alphanumeric and basic punctuation
        normalized = re.sub(r'[^\w.,]', '', idea.lower())
        # Remove spaces completely for comparison
        normalized = normalized.replace('_', '')
        return normalized
    
    def check_cache_for_topic(self):
        """Check if the entered topic exists in cache and update the UI accordingly"""
        topic = self.topics_entry.get("1.0", tk.END).strip()
        if not topic:
            self.cache_status.config(text="")
            return
        
        # Parse the first topic if multiple are entered
        if "," in topic:
            main_topic = topic.split(",")[0].strip()
        else:
            main_topic = topic.strip()
        
        cached_result = self.check_idea_cache(main_topic)
        if cached_result:
            self.cache_status.config(text=f"✓ Cached version available for '{main_topic}'", foreground="green")
        else:
            self.cache_status.config(text="")
    
    def get_cache_folder_for_idea(self, idea):
        """Get the cache folder path for a specific idea"""
        # Create a sanitized folder name from the idea for filesystem safety
        # Using a hash ensures unique and safe folder names
        idea_hash = hashlib.md5(idea.encode('utf-8')).hexdigest()[:8]
        sanitized_idea = "".join(c if c.isalnum() or c in "._- " else "_" for c in idea)
        sanitized_idea = sanitized_idea.strip().replace(' ', '_')
        folder_name = f"{sanitized_idea}_{idea_hash}"
        
        # Create the cache folder structure
        cache_dir = os.path.join(os.getcwd(), "cache")
        idea_dir = os.path.join(cache_dir, folder_name)
        
        # Ensure directories exist
        os.makedirs(idea_dir, exist_ok=True)
        
        return idea_dir
    
    def check_idea_cache(self, idea):
        """Check if presentation for this idea already exists in cache (case-insensitive)"""
        cache_dir = os.path.join(os.getcwd(), "cache")
        if not os.path.exists(cache_dir):
            return None
        
        # Normalize the input idea for comparison
        normalized_idea = self.normalize_idea_name(idea)
        
        # Check all folders in the cache directory
        for folder in os.listdir(cache_dir):
            folder_path = os.path.join(cache_dir, folder)
            
            if os.path.isdir(folder_path):
                # Extract the original idea name from the folder (remove the hash part)
                parts = folder.split('_')
                if len(parts) > 1:  # Make sure there's at least one part before the hash
                    # Join everything except the last part (hash)
                    folder_idea = '_'.join(parts[:-1]).replace('_', ' ')
                    
                    # Normalize folder idea name for comparison
                    normalized_folder_idea = self.normalize_idea_name(folder_idea)
                    
                    # Case-insensitive comparison of normalized names (ignoring spaces and symbols)
                    if normalized_folder_idea == normalized_idea:
                        self.log(f"Cache match: '{folder_idea}' ↔ '{idea}'")

                        # Check if required files exist
                        outline_path = os.path.join(folder_path, "enriched_outline.json")
                        speech_path = os.path.join(folder_path, "presentation_speech.md")
                        
                        if os.path.exists(outline_path) and os.path.exists(speech_path):
                            try:
                                # Verify files are valid by reading them
                                with open(outline_path, "r", encoding="utf-8") as file:
                                    enriched_outline = json.load(file)
                                
                                with open(speech_path, "r", encoding="utf-8") as file:
                                    speech_text = file.read()
                                
                                return {
                                    "enriched_outline": enriched_outline,
                                    "speech_text": speech_text,
                                    "outline_path": outline_path,
                                    "speech_path": speech_path,
                                    "folder_path": folder_path
                                }
                            except Exception:
                                # If files are corrupted, continue to next folder
                                continue
        
        return None
    
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
                
            main_topic = topic_list[0]
            self.log(f"Processing topics: {', '.join(topic_list)}")
            
            # Check if we already have this presentation in cache
            self.log("Checking cache for existing presentation...")
            cached_result = self.check_idea_cache(main_topic)
            
            if cached_result:
                self.log("Found presentation in cache! Loading existing files...")
                enriched_outline = cached_result["enriched_outline"]
                speech_text = cached_result["speech_text"]
                
                # Copy outline and speech to output directory for backward compatibility
                os.makedirs("./output", exist_ok=True)
                
                with open("./output/enriched_outline.json", "w", encoding="utf-8") as file:
                    json.dump(enriched_outline, file, ensure_ascii=False, indent=4)
                
                with open("./output/presentation_speech.md", "w", encoding="utf-8") as file:
                    file.write(speech_text)
            else:
                # Generate new presentation content
                try:
                    self.log("No cached version found. Generating content with Ollama...")
                    result = pdf2final_list.process(main_topic)
                    
                    enriched_outline = result["enriched_outline"]
                    speech_text = result["speech_text"]
                    
                    # Save to the specific idea's cache folder
                    idea_dir = self.get_cache_folder_for_idea(main_topic)
                    
                    # Save outline and speech to cache
                    with open(os.path.join(idea_dir, "enriched_outline.json"), "w", encoding="utf-8") as file:
                        json.dump(enriched_outline, file, ensure_ascii=False, indent=4)
                    
                    with open(os.path.join(idea_dir, "presentation_speech.md"), "w", encoding="utf-8") as file:
                        file.write(speech_text)
                    
                    # And also to the standard output directory for backward compatibility
                    os.makedirs("./output", exist_ok=True)
                    
                    with open("./output/enriched_outline.json", "w", encoding="utf-8") as file:
                        json.dump(enriched_outline, file, ensure_ascii=False, indent=4)
                    
                    with open("./output/presentation_speech.md", "w", encoding="utf-8") as file:
                        file.write(speech_text)
                    
                    self.log(f"Saved content to cache: {idea_dir}")
                    
                except Exception as e:
                    self.log(f"Error generating content: {str(e)}")
                    messagebox.showerror("Error", f"An error occurred during content generation: {str(e)}")
                    return
            
            # Create the PowerPoint
            self.log("Creating PowerPoint presentation...")
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
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
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
    
    def is_valid_cache_folder(self, folder_path):
        """Check if a folder is a valid cache folder containing presentation files"""
        outline_path = os.path.join(folder_path, "enriched_outline.json")
        speech_path = os.path.join(folder_path, "presentation_speech.md")
        
        # Check if both required files exist
        if not (os.path.exists(outline_path) and os.path.exists(speech_path)):
            return False
        
        # Try to read the files to verify they're valid
        try:
            with open(outline_path, "r", encoding="utf-8") as file:
                json.load(file)  # Just try to load it
            
            with open(speech_path, "r", encoding="utf-8") as file:
                if len(file.read().strip()) == 0:
                    return False  # Empty speech file
                
            return True
        except Exception:
            return False
    
    def clean_cache_directory(self, cache_dir):
        """Clean cache directory by removing invalid cache folders"""
        if not os.path.exists(cache_dir):
            return
        
        for folder in os.listdir(cache_dir):
            folder_path = os.path.join(cache_dir, folder)
            
            # Skip non-directories and special folders
            if not os.path.isdir(folder_path) or folder.startswith('.'):
                continue
                
            # Check if the folder has the expected structure (hash suffix)
            parts = folder.split('_')
            if len(parts) < 2:  # No hash suffix
                continue
                
            # Check if it's a valid cache folder with required files
            if not self.is_valid_cache_folder(folder_path):
                try:
                    shutil.rmtree(folder_path)
                    print(f"Removed invalid cache folder: {folder}")
                except Exception as e:
                    print(f"Error removing invalid cache folder {folder}: {str(e)}")
    
    def browse_cache(self):
        """Open a dialog to browse and select from cached presentations"""
        cache_dir = os.path.join(os.getcwd(), "cache")
        
        # Ensure cache directory exists
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
        
        # Clean the cache directory first
        self.clean_cache_directory(cache_dir)
        
        # Get list of cached presentations
        cached_ideas = []
        try:
            for folder in os.listdir(cache_dir):
                folder_path = os.path.join(cache_dir, folder)
                
                # Skip non-directories and special folders
                if not os.path.isdir(folder_path) or folder.startswith('.'):
                    continue
                
                # Only include folders with valid cache structure
                if self.is_valid_cache_folder(folder_path):
                    # Extract the original idea name from the folder
                    parts = folder.split('_')
                    if len(parts) > 1:  # Make sure there's at least one part before the hash
                        # The last element should be the hash
                        idea_name = '_'.join(parts[:-1])  # Join everything except the last part
                        idea_name = idea_name.replace('_', ' ')
                        
                        # Use the title from the outline if available
                        try:
                            outline_path = os.path.join(folder_path, "enriched_outline.json")
                            with open(outline_path, "r", encoding="utf-8") as file:
                                outline_data = json.load(file)
                                title = outline_data.get("title", idea_name)
                                
                                cached_ideas.append({
                                    "folder": folder,
                                    "display_name": title,
                                    "folder_path": folder_path
                                })
                        except Exception:
                            # If there's an error reading the JSON, just use the folder name
                            cached_ideas.append({
                                "folder": folder,
                                "display_name": idea_name,
                                "folder_path": folder_path
                            })
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read cache directory: {str(e)}")
            return
        
        if not cached_ideas:
            messagebox.showinfo("Cache Empty", "No cached presentations found.")
            return
        
        # Create a dialog to display and select cached presentations
        cache_window = tk.Toplevel(self.root)
        cache_window.title("Cached Presentations")
        cache_window.geometry("600x400")
        cache_window.transient(self.root)
        cache_window.grab_set()
        
        # Create list frame
        frame = ttk.Frame(cache_window, padding="20 20 20 20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Select a cached presentation:").pack(anchor=tk.W, pady=(0, 10))
        
        # Create a listbox with scrollbar
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create the listbox
        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=('Arial', 12), height=10)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Insert the cached presentations
        for i, item in enumerate(cached_ideas):
            listbox.insert(tk.END, item["display_name"])
            
        # Button frame
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def load_selected_presentation():
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                selected_idea = cached_ideas[idx]
                
                # Load the selected presentation into the GUI
                outline_path = os.path.join(selected_idea["folder_path"], "enriched_outline.json")
                speech_path = os.path.join(selected_idea["folder_path"], "presentation_speech.md")
                
                try:
                    with open(outline_path, "r", encoding="utf-8") as file:
                        enriched_outline = json.load(file)
                    
                    with open(speech_path, "r", encoding="utf-8") as file:
                        speech_text = file.read()
                    
                    # Save to output directory for compatibility
                    os.makedirs("./output", exist_ok=True)
                    
                    with open("./output/enriched_outline.json", "w", encoding="utf-8") as file:
                        json.dump(enriched_outline, file, ensure_ascii=False, indent=4)
                    
                    with open("./output/presentation_speech.md", "w", encoding="utf-8") as file:
                        file.write(speech_text)
                    
                    # Create the PowerPoint
                    dictToPpt.dictToPpt(enriched_outline, speech_text)
                    
                    # Copy to user's desired location if specified
                    target_path = self.save_path_var.get()
                    if target_path != os.path.join(os.getcwd(), "PPT.pptx"):
                        shutil.copy("PPT.pptx", target_path)
                    
                    self.log(f"Loaded cached presentation: {selected_idea['display_name']}")
                    
                    # Update the topics entry with the selected idea name
                    # Extract name from the folder (remove the hash part)
                    parts = selected_idea["folder"].split('_')
                    if len(parts) > 1:
                        idea_name = '_'.join(parts[:-1])
                        idea_name = idea_name.replace('_', ' ')
                        self.topics_entry.delete("1.0", tk.END)
                        self.topics_entry.insert("1.0", idea_name)
                    
                    # Enable TTS button
                    self.tts_button.config(state=tk.NORMAL)
                    
                    # Success message
                    messagebox.showinfo("Success", "Cached presentation loaded successfully!")
                    
                    # Offer to open the presentation
                    if messagebox.askyesno("Open Presentation", "Would you like to open the presentation now?"):
                        os.startfile(target_path)
                    
                    cache_window.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load presentation: {str(e)}")
        
        def delete_selected_presentation():
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                selected_idea = cached_ideas[idx]
                
                if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the cached presentation:\n{selected_idea['display_name']}?"):
                    try:
                        # Delete the folder
                        shutil.rmtree(selected_idea["folder_path"])
                        self.log(f"Deleted cached presentation: {selected_idea['display_name']}")
                        
                        # Remove from list and refresh
                        del cached_ideas[idx]
                        listbox.delete(idx)
                        
                        if not cached_ideas:
                            messagebox.showinfo("Cache Empty", "No more cached presentations available.")
                            cache_window.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to delete presentation: {str(e)}")
        
        # Create buttons
        load_button = ttk.Button(button_frame, text="Load Selected", command=load_selected_presentation)
        load_button.pack(side=tk.LEFT, padx=(0, 5))
        
        delete_button = ttk.Button(button_frame, text="Delete Selected", command=delete_selected_presentation)
        delete_button.pack(side=tk.LEFT)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=cache_window.destroy)
        cancel_button.pack(side=tk.RIGHT)
        
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