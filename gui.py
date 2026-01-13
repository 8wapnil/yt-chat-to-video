import tkinter as tk
import customtkinter as ctk
import sys
import subprocess
import threading
import os
import queue

# Valid Themes
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ChatRendererGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YT Chat Renderer - Enhanced")
        self.geometry("800x650")

        # Layout Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Build UI Components
        self.create_input_section()
        self.create_settings_section()
        self.create_export_section()
        self.create_log_section()
        
    def create_input_section(self):
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.input_frame, text="YouTube URL / ID:").grid(row=0, column=0, padx=10, pady=10)
        self.url_entry = ctk.CTkEntry(self.input_frame, placeholder_text="https://www.youtube.com/watch?v=...")
        self.url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Or File Picker
        ctk.CTkLabel(self.input_frame, text="Or Select JSON:").grid(row=1, column=0, padx=10, pady=10)
        self.file_path_var = tk.StringVar()
        self.file_entry = ctk.CTkEntry(self.input_frame, textvariable=self.file_path_var, placeholder_text="Select a .live_chat.json file")
        self.file_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        ctk.CTkButton(self.input_frame, text="Browse", width=100, command=self.browse_file).grid(row=1, column=2, padx=10, pady=10)

    def create_settings_section(self):
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Grid layout for settings
        self.settings_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Role Colors
        ctk.CTkLabel(self.settings_frame, text="Owner Color").grid(row=0, column=0, padx=5, pady=5)
        self.color_owner = ctk.CTkEntry(self.settings_frame)
        self.color_owner.insert(0, "#ffd600")
        self.color_owner.grid(row=1, column=0, padx=5, pady=5)

        ctk.CTkLabel(self.settings_frame, text="Mod Color").grid(row=0, column=1, padx=5, pady=5)
        self.color_mod = ctk.CTkEntry(self.settings_frame)
        self.color_mod.insert(0, "#5e84f1")
        self.color_mod.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(self.settings_frame, text="Member Color").grid(row=0, column=2, padx=5, pady=5)
        self.color_member = ctk.CTkEntry(self.settings_frame)
        self.color_member.insert(0, "#2ba640")
        self.color_member.grid(row=1, column=2, padx=5, pady=5)

        ctk.CTkLabel(self.settings_frame, text="Normal Color").grid(row=0, column=3, padx=5, pady=5)
        self.color_normal = ctk.CTkEntry(self.settings_frame)
        self.color_normal.insert(0, "#ffffff")
        self.color_normal.grid(row=1, column=3, padx=5, pady=5)

        # Advanced Settings
        ctk.CTkLabel(self.settings_frame, text="Outline Width").grid(row=2, column=0, padx=5, pady=5)
        self.outline_width = ctk.CTkSlider(self.settings_frame, from_=0, to=5, number_of_steps=5)
        self.outline_width.set(1)
        self.outline_width.grid(row=3, column=0, padx=5, pady=5)

        self.check_transparent = ctk.CTkCheckBox(self.settings_frame, text="Transparent Background")
        self.check_transparent.select()
        self.check_transparent.grid(row=3, column=1, padx=5, pady=5)

        self.check_hwaccel = ctk.CTkCheckBox(self.settings_frame, text="Hardware Acceleration")
        self.check_hwaccel.select()
        self.check_hwaccel.grid(row=3, column=2, padx=5, pady=5)
        
    def create_export_section(self):
        self.export_frame = ctk.CTkFrame(self)
        self.export_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.export_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Codec Selection
        ctk.CTkLabel(self.export_frame, text="Codec").grid(row=0, column=0, padx=5, pady=5)
        self.codec_var = ctk.CTkOptionMenu(self.export_frame, values=["prores", "hevc", "h264", "av1"])
        self.codec_var.set("prores")
        self.codec_var.grid(row=1, column=0, padx=5, pady=5)

        # Output Filename
        ctk.CTkLabel(self.export_frame, text="Output Filename (Optional)").grid(row=0, column=1, padx=5, pady=5)
        self.output_entry = ctk.CTkEntry(self.export_frame, placeholder_text="overlay.mov")
        self.output_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Render Button
        self.render_btn = ctk.CTkButton(self.export_frame, text="START RENDER", command=self.start_render, fg_color="green", height=40)
        self.render_btn.grid(row=1, column=2, padx=20, pady=20, sticky="ew")

    def create_log_section(self):
        self.log_textbox = ctk.CTkTextbox(self, height=150)
        self.log_textbox.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="nsew")
        self.log_textbox.insert("0.0", "Ready to render...\n")
        self.log_textbox.configure(state="disabled")

    def browse_file(self):
        file_path = tk.filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if file_path:
            self.file_path_var.set(file_path)

    def log(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def start_render(self):
        url = self.url_entry.get().strip()
        file_path = self.file_path_var.get().strip()
        
        target = file_path if file_path else url
        if not target:
            self.log("Error: Please provide a YouTube URL or select a JSON file.")
            return

        self.render_btn.configure(state="disabled", text="Rendering...")
        self.log(f"Starting render for: {target}")
        
        # Build Command
        script_path = os.path.join(os.path.dirname(__file__), "yt-chat-to-video.py")
        
        cmd = [sys.executable, script_path, target]
        
        # Add Arguments
        if self.output_entry.get().strip():
            cmd.extend(["--output", self.output_entry.get().strip()])
            
        cmd.extend(["--codec", self.codec_var.get()])
        
        if self.check_transparent.get():
            cmd.append("--transparent")
            
        if self.check_hwaccel.get():
            cmd.append("--hwaccel")
            
        # Colors
        cmd.extend(["--color-owner", self.color_owner.get()])
        cmd.extend(["--color-moderator", self.color_mod.get()])
        cmd.extend(["--color-member", self.color_member.get()])
        cmd.extend(["--color-normal", self.color_normal.get()])
        
        cmd.extend(["--outline-width", str(int(self.outline_width.get()))])

        # Run process in thread
        threading.Thread(target=self.run_process, args=(cmd,), daemon=True).start()

    def run_process(self, cmd):
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            for line in process.stdout:
                self.after(0, self.log, line.strip())
                
            process.wait()
            
            if process.returncode == 0:
                self.after(0, self.log, "✅ Render Complete!")
            else:
                self.after(0, self.log, "❌ Render Failed.")
                
        except Exception as e:
            self.after(0, self.log, f"Error: {e}")
            
        self.after(0, lambda: self.render_btn.configure(state="normal", text="START RENDER"))

if __name__ == "__main__":
    app = ChatRendererGUI()
    app.mainloop()
