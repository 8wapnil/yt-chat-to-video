import tkinter as tk
import customtkinter as ctk
import sys
import subprocess
import threading
import os
import platform
import shutil
import json

# Theme Settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ChatRendererGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YT Chat Render")
        self.geometry("900x700")
        
        # Grid Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Tabview expands
        self.grid_rowconfigure(2, weight=0) # Log section fixed height

        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        ctk.CTkLabel(self.header_frame, text="YouTube Chat to Video Renderer", font=("Roboto", 24, "bold")).pack(side="left")

        # Tab View
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.tab_main = self.tab_view.add("Main")
        self.tab_video = self.tab_view.add("Video Settings")
        self.tab_style = self.tab_view.add("Style & Colors")
        self.tab_advanced = self.tab_view.add("Advanced")

        # Initialize Variables & UI
        self.process = None
        self.init_main_tab()
        self.init_video_tab()
        self.init_style_tab()
        self.init_advanced_tab()
        self.init_log_section()
        
        self.load_settings()

    def get_settings_file(self):
        # Store settings in user home directory to avoid permission issues in Program Files
        home = os.path.expanduser("~")
        config_dir = os.path.join(home, ".yt-chat-renderer")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        return os.path.join(config_dir, "settings.json")

    def load_settings(self):
        try:
            path = self.get_settings_file()
            if not os.path.exists(path):
                return
            
            with open(path, "r") as f:
                settings = json.load(f)
                
            # Helper to safely set fields
            def safe_set(entry, key):
                if key in settings:
                    entry.delete(0, "end")
                    entry.insert(0, str(settings[key]))
            
            # Helper for checkboxes
            def safe_check(checkbox, key):
                if key in settings:
                    checkbox.select() if settings[key] else checkbox.deselect()

            # Main
            safe_set(self.url_entry, "url")
            if "file_path" in settings: self.file_path_var.set(settings["file_path"])
            safe_set(self.output_entry, "output")
            
            # Video
            safe_set(self.width_entry, "width")
            safe_set(self.height_entry, "height")
            safe_set(self.fps_entry, "fps")
            safe_set(self.start_time, "start_time")
            safe_set(self.end_time, "end_time")
            
            if "codec" in settings: self.codec_var.set(settings["codec"])
            if "quality" in settings: self.quality_var.set(settings["quality"])
            safe_check(self.hwaccel_var, "hwaccel")

            # Style
            safe_set(self.color_owner, "color_owner")
            safe_set(self.color_mod, "color_mod")
            safe_set(self.color_member, "color_member")
            safe_set(self.color_normal, "color_normal")
            
            safe_set(self.bg_color, "bg_color")
            safe_set(self.msg_color, "msg_color")
            safe_set(self.outline_color, "outline_color")
            
            safe_check(self.check_transparent, "transparent")
            
            if "outline_width" in settings: self.outline_width.set(settings["outline_width"])
            safe_set(self.padding, "padding")
            safe_set(self.scale, "scale")

            # Advanced
            safe_check(self.use_cache, "use_cache")
            safe_check(self.skip_avatars, "skip_avatars")
            safe_check(self.skip_emojis, "skip_emojis")
            safe_check(self.no_clip, "no_clip")
            
            safe_set(self.proxy_entry, "proxy")
                
            self.log(f"Settings loaded from {path}")
        except Exception as e:
            self.log(f"Error loading settings: {e}")

    def save_settings(self):
        try:
            settings = {
                "url": self.url_entry.get(),
                "file_path": self.file_path_var.get(),
                "output": self.output_entry.get(),
                "width": self.width_entry.get(),
                "height": self.height_entry.get(),
                "fps": self.fps_entry.get(),
                "start_time": self.start_time.get(),
                "end_time": self.end_time.get(),
                "codec": self.codec_var.get(),
                "quality": self.quality_var.get(),
                "hwaccel": bool(self.hwaccel_var.get()),
                "color_owner": self.color_owner.get(),
                "color_mod": self.color_mod.get(),
                "color_member": self.color_member.get(),
                "color_normal": self.color_normal.get(),
                "bg_color": self.bg_color.get(),
                "msg_color": self.msg_color.get(),
                "outline_color": self.outline_color.get(),
                "transparent": bool(self.check_transparent.get()),
                "outline_width": self.outline_width.get(),
                "padding": self.padding.get(),
                "scale": self.scale.get(),
                "use_cache": bool(self.use_cache.get()),
                "skip_avatars": bool(self.skip_avatars.get()),
                "skip_emojis": bool(self.skip_emojis.get()),
                "no_clip": bool(self.no_clip.get()),
                "proxy": self.proxy_entry.get()
            }
            
            path = self.get_settings_file()
            with open(path, "w") as f:
                json.dump(settings, f, indent=4)
            self.log(f"Settings saved to {path}")
        except Exception as e:
            self.log(f"Error saving settings: {e}")

    def init_main_tab(self):
        t = self.tab_main
        t.grid_columnconfigure(1, weight=1)

        # Input Source
        ctk.CTkLabel(t, text="Input Source", font=("Roboto", 16, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # URL Input
        ctk.CTkLabel(t, text="YouTube URL / ID:").grid(row=1, column=0, sticky="w", padx=20, pady=5)
        self.url_entry = ctk.CTkEntry(t, placeholder_text="https://www.youtube.com/watch?v=...")
        self.url_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=20, pady=5)

        # File Input
        ctk.CTkLabel(t, text="OR Local JSON File:").grid(row=2, column=0, sticky="w", padx=20, pady=5)
        self.file_path_var = tk.StringVar()
        self.file_entry = ctk.CTkEntry(t, textvariable=self.file_path_var, placeholder_text="Select .live_chat.json file")
        self.file_entry.grid(row=2, column=1, sticky="ew", padx=(20, 10), pady=5)
        ctk.CTkButton(t, text="Browse", width=80, command=self.browse_file).grid(row=2, column=2, padx=(0, 20), pady=5)

        ctk.CTkFrame(t, height=2, fg_color="gray30").grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=20)

        # Output
        ctk.CTkLabel(t, text="Output", font=("Roboto", 16, "bold")).grid(row=4, column=0, sticky="w", padx=10, pady=(5, 5))
        
        ctk.CTkLabel(t, text="Output Filename (Opt):").grid(row=5, column=0, sticky="w", padx=20, pady=5)
        self.output_entry = ctk.CTkEntry(t, placeholder_text="e.g. chat_overlay.mov")
        self.output_entry.grid(row=5, column=1, columnspan=2, sticky="ew", padx=20, pady=5)

        # Actions
        self.action_frame = ctk.CTkFrame(t, fg_color="transparent")
        self.action_frame.grid(row=6, column=0, columnspan=3, pady=30)
        
        self.render_btn = ctk.CTkButton(self.action_frame, text="START RENDER", command=self.start_render, 
                                      fg_color="#2ba640", hover_color="#218c32", width=200, height=50, font=("Roboto", 16, "bold"))
        self.render_btn.pack(side="left", padx=10)

        self.stop_btn = ctk.CTkButton(self.action_frame, text="STOP", command=self.stop_render,
                                    fg_color="#d32f2f", hover_color="#b71c1c", width=100, height=50, state="disabled", font=("Roboto", 16, "bold"))
        self.stop_btn.pack(side="left", padx=10)

        # Reveal Button (Hidden by default)
        self.reveal_btn = ctk.CTkButton(t, text="📂 Reveal Output File", command=self.reveal_file, fg_color="#1565c0", hover_color="#0d47a1")
        self.reveal_btn.grid(row=7, column=0, columnspan=3, pady=10)
        self.reveal_btn.grid_remove() # Hide initially

    def init_video_tab(self):
        t = self.tab_video
        t.grid_columnconfigure((0, 1), weight=1)

        # Resolution
        res_frame = ctk.CTkFrame(t)
        res_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        res_frame.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(res_frame, text="Width:").grid(row=0, column=0, padx=10, pady=10)
        self.width_entry = ctk.CTkEntry(res_frame, width=80)
        self.width_entry.insert(0, "400")
        self.width_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(res_frame, text="Height:").grid(row=0, column=2, padx=10, pady=10)
        self.height_entry = ctk.CTkEntry(res_frame, width=80)
        self.height_entry.insert(0, "540")
        self.height_entry.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        # Framerate
        ctk.CTkLabel(res_frame, text="FPS:").grid(row=0, column=4, padx=10, pady=10)
        self.fps_entry = ctk.CTkEntry(res_frame, width=60)
        self.fps_entry.insert(0, "60")
        self.fps_entry.grid(row=0, column=5, padx=10, pady=10, sticky="w")

        # Time Range
        time_frame = ctk.CTkFrame(t)
        time_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(time_frame, text="Start Time (s):").grid(row=0, column=0, padx=10, pady=10)
        self.start_time = ctk.CTkEntry(time_frame, width=80)
        self.start_time.insert(0, "0")
        self.start_time.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(time_frame, text="End Time (s):").grid(row=0, column=2, padx=10, pady=10)
        self.end_time = ctk.CTkEntry(time_frame, width=80)
        self.end_time.insert(0, "0")
        self.end_time.grid(row=0, column=3, padx=10, pady=10)
        ctk.CTkLabel(time_frame, text="(0 = Full Duration)").grid(row=0, column=4, padx=5)

        # Codec & Quality
        settings_frame = ctk.CTkFrame(t)
        settings_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=10)

        ctk.CTkLabel(settings_frame, text="Codec:").grid(row=0, column=0, padx=10, pady=10)
        self.codec_var = ctk.CTkOptionMenu(settings_frame, values=["prores", "hevc", "h264", "av1"])
        self.codec_var.set("prores")
        self.codec_var.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(settings_frame, text="Quality:").grid(row=0, column=2, padx=10, pady=10)
        self.quality_var = ctk.CTkOptionMenu(settings_frame, values=["standard", "high", "lossless"])
        self.quality_var.set("high")
        self.quality_var.grid(row=0, column=3, padx=10, pady=10)

        self.hwaccel_var = ctk.CTkCheckBox(settings_frame, text="Use Hardware Acceleration")
        self.hwaccel_var.select()
        self.hwaccel_var.grid(row=1, column=0, columnspan=4, pady=10)

    def init_style_tab(self):
        t = self.tab_style
        t.grid_columnconfigure((0, 1), weight=1)

        # Role Colors
        role_frame = ctk.CTkFrame(t)
        role_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        role_frame.grid_columnconfigure((1, 3), weight=1)

        def create_color_entry(parent, row, col, label, default):
            ctk.CTkLabel(parent, text=label).grid(row=row, column=col, padx=4, pady=10, sticky="e")
            entry = ctk.CTkEntry(parent, width=100)
            entry.insert(0, default)
            entry.grid(row=row, column=col+1, padx=10, pady=10, sticky="w")
            return entry

        self.color_owner = create_color_entry(role_frame, 0, 0, "Owner:", "#ffd600")
        self.color_mod = create_color_entry(role_frame, 0, 2, "Moderator:", "#5e84f1")
        self.color_member = create_color_entry(role_frame, 1, 0, "Member:", "#2ba640")
        self.color_normal = create_color_entry(role_frame, 1, 2, "Normal:", "#ffffff")
        
        # General Colors
        gen_color_frame = ctk.CTkFrame(t)
        gen_color_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        gen_color_frame.grid_columnconfigure((1, 3), weight=1)

        self.bg_color = create_color_entry(gen_color_frame, 0, 0, "Background:", "#0f0f0f")
        self.msg_color = create_color_entry(gen_color_frame, 0, 2, "Message Text:", "#ffffff")
        self.outline_color = create_color_entry(gen_color_frame, 1, 0, "Outline Color:", "#000000")

        self.check_transparent = ctk.CTkCheckBox(gen_color_frame, text="Transparent Background")
        self.check_transparent.select()
        self.check_transparent.grid(row=1, column=2, columnspan=2, pady=10)

        # Dimensions
        dim_frame = ctk.CTkFrame(t)
        dim_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(dim_frame, text="Outline Width:").grid(row=0, column=0, padx=10, pady=10)
        self.outline_width = ctk.CTkSlider(dim_frame, from_=0, to=5, number_of_steps=5)
        self.outline_width.set(1)
        self.outline_width.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(dim_frame, text="Padding:").grid(row=0, column=2, padx=10, pady=10)
        self.padding = ctk.CTkEntry(dim_frame, width=60)
        self.padding.insert(0, "24")
        self.padding.grid(row=0, column=3, padx=10, pady=10)

        ctk.CTkLabel(dim_frame, text="Scale:").grid(row=0, column=4, padx=10, pady=10)
        self.scale = ctk.CTkEntry(dim_frame, width=60)
        self.scale.insert(0, "1")
        self.scale.grid(row=0, column=5, padx=10, pady=10)

    def init_advanced_tab(self):
        t = self.tab_advanced
        t.grid_columnconfigure(0, weight=1)

        # Flags
        opt_frame = ctk.CTkFrame(t)
        opt_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)

        self.use_cache = ctk.CTkCheckBox(opt_frame, text="Cache Images to Disk")
        self.use_cache.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.skip_avatars = ctk.CTkCheckBox(opt_frame, text="Skip Avatars")
        self.skip_avatars.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        self.skip_emojis = ctk.CTkCheckBox(opt_frame, text="Skip Emojis")
        self.skip_emojis.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        self.no_clip = ctk.CTkCheckBox(opt_frame, text="No Clip (Don't hide top messages)")
        self.no_clip.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        # Cache clear
        ctk.CTkButton(opt_frame, text="Clear Cache Folder", command=self.clear_cache, fg_color="gray", hover_color="gray30").grid(row=0, column=1, padx=20, pady=10)

        # Proxy
        proxy_frame = ctk.CTkFrame(t)
        proxy_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        ctk.CTkLabel(proxy_frame, text="Proxy URL (http/socks):").pack(side="left", padx=10, pady=10)
        self.proxy_entry = ctk.CTkEntry(proxy_frame, width=300, placeholder_text="http://127.0.0.1:8080")
        self.proxy_entry.pack(side="left", padx=10, pady=10)

    def init_log_section(self):
        self.log_frame = ctk.CTkFrame(self, height=150)
        self.log_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.log_frame.grid_propagate(False)

        self.log_box = ctk.CTkTextbox(self.log_frame)
        self.log_box.pack(fill="both", expand=True, padx=5, pady=5)
        self.log_box.insert("0.0", "Ready.\n")
        self.log_box.configure(state="disabled")

    # --- Actions ---

    def browse_file(self):
        file_path = tk.filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if file_path:
            self.file_path_var.set(file_path)

    def log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", str(msg) + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def clear_cache(self):
        cache_dir = "yt-chat-to-video_cache"
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                self.log(f"Cache directory '{cache_dir}' deleted.")
            except Exception as e:
                self.log(f"Error deleting cache: {e}")
        else:
            self.log("Cache directory not found.")

    def reveal_file(self):
        # Determine current output file
        output_file = self.last_output_file
        if not output_file or not os.path.exists(output_file):
            self.log("Output file not found.")
            return

        self.log(f"Revealing: {output_file}")
        
        system_platform = platform.system()
        try:
            if system_platform == "Windows":
                subprocess.run(["explorer", "/select,", os.path.normpath(output_file)])
            elif system_platform == "Darwin": # macOS
                subprocess.run(["open", "-R", output_file])
            else: # Linux
                subprocess.run(["xdg-open", os.path.dirname(output_file)])
        except Exception as e:
            self.log(f"Error revealing file: {e}")

    def stop_render(self):
        if self.process:
            self.log("Stopping render...")
            self.process.terminate()
            self.stop_btn.configure(state="disabled")

    def start_render(self):
        self.save_settings()
        self.reveal_btn.grid_remove() 
        url = self.url_entry.get().strip()
        file_path = self.file_path_var.get().strip()
        
        target = file_path if file_path else url
        if not target:
            self.log("Error: Please provide a YouTube URL or select a JSON file.")
            self.tab_view.set("Main")
            return

        self.render_btn.configure(state="disabled", text="Rendering...")
        self.stop_btn.configure(state="normal")
        self.log(f"-"*30)
        self.log(f"Starting render for: {target}")

        # Construct Command
        script_path = os.path.join(os.path.dirname(__file__), "yt-chat-to-video.py")
        cmd = [sys.executable, script_path, target]

        # Output
        out_file = self.output_entry.get().strip()
        if out_file:
            cmd.extend(["--output", out_file])
        
        # Dimensions & Time
        cmd.extend(["--width", self.width_entry.get()])
        cmd.extend(["--height", self.height_entry.get()])
        cmd.extend(["--frame-rate", self.fps_entry.get()])
        
        if float(self.start_time.get()) > 0:
            cmd.extend(["--from", self.start_time.get()])
        if float(self.end_time.get()) > 0:
            cmd.extend(["--to", self.end_time.get()])

        # Codec/Quality
        cmd.extend(["--codec", self.codec_var.get()])
        cmd.extend(["--quality", self.quality_var.get()])
        if self.hwaccel_var.get(): cmd.append("--hwaccel")

        # Style
        cmd.extend(["--color-owner", self.color_owner.get()])
        cmd.extend(["--color-moderator", self.color_mod.get()])
        cmd.extend(["--color-member", self.color_member.get()])
        cmd.extend(["--color-normal", self.color_normal.get()])
        
        cmd.extend(["--background", self.bg_color.get()])
        cmd.extend(["--message-color", self.msg_color.get()])
        cmd.extend(["--outline-color", self.outline_color.get()])
        cmd.extend(["--outline-width", str(int(self.outline_width.get()))])
        cmd.extend(["--padding", self.padding.get()])
        cmd.extend(["--scale", self.scale.get()])

        if self.check_transparent.get(): cmd.append("--transparent")

        # Advanced
        if self.use_cache.get(): cmd.append("--use-cache")
        if self.skip_avatars.get(): cmd.append("--skip-avatars")
        if self.skip_emojis.get(): cmd.append("--skip-emojis")
        if not self.no_clip.get(): cmd.append("--no-clip")
        if self.no_clip.get():
             cmd.append("--no-clip")

        if self.proxy_entry.get().strip():
             cmd.extend(["--proxy", self.proxy_entry.get().strip()])

        # Run Thread
        threading.Thread(target=self.run_subprocess, args=(cmd,), daemon=True).start()

    def run_subprocess(self, cmd):
        # We need to capture the output file name for the reveal button
        # If user didn't specify one, we need to guess or parse logged output
        # Easiest is to see what the python script prints as "Output: ..." if available, or just use what we passed if available.
        # If user didn't pass output, script defaults.
        
        self.last_output_file = None
        user_specified_output = self.output_entry.get().strip()
        if user_specified_output:
             self.last_output_file = os.path.abspath(user_specified_output)
        
        try:
            # On Windows, we need creatingflags to hide console if we are using pyinstaller --noconsole, 
            # but here we are running python script directly.
            startupinfo = None
            if platform.system() == "Windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                startupinfo=startupinfo
            )
            
            for line in self.process.stdout:
                line = line.strip()
                if line:
                    self.after(0, self.log, line)
                    # Try to capture output filename if not manually specified
                    # Script doesn't explicitly print "Output file: X", but we can try to infer or just rely on user input for now.
                    # Or we updatescript to print "Output: ..."
                    
            self.process.wait()
            return_code = self.process.returncode
            self.process = None

            if return_code == 0:
                self.after(0, lambda: self.finish_render(True))
            else:
                self.after(0, lambda: self.finish_render(False))
                
        except Exception as e:
            self.after(0, self.log, f"Error launching process: {e}")
            self.after(0, lambda: self.finish_render(False))

    def finish_render(self, success):
        self.render_btn.configure(state="normal", text="START RENDER")
        self.stop_btn.configure(state="disabled")
        
        if success:
            self.log("✅ Render Complete!")
            # Use user specified output if available, otherwise we might fail to reveal if default was used.
            # But we can try to look for input_filename.mov if input was file.
            
            if not self.last_output_file:
                # Try to guess default output name
                # Logic from script: input.json -> input.mp4/mov
                try:
                    inp = self.file_path_var.get().strip()
                    if inp and inp.endswith(".json"):
                         base = os.path.splitext(inp)[0]
                         # Check possible extensions
                         for ext in [".mov", ".mp4", ".webm"]:
                             if os.path.exists(base + ext):
                                 self.last_output_file = base + ext
                                 break
                    # If Url was used, it defaults to output.mp4/mov
                    if not self.last_output_file:
                        for default in ["output.mov", "output.mp4"]:
                            if os.path.exists(default):
                                self.last_output_file = os.path.abspath(default)
                                break
                except: pass

            if self.last_output_file and os.path.exists(self.last_output_file):
                 self.reveal_btn.configure(text=f"📂 Reveal: {os.path.basename(self.last_output_file)}")
                 self.reveal_btn.grid()
        else:
             self.log("❌ Render Failed or Cancelled.")

if __name__ == "__main__":
    app = ChatRendererGUI()
    app.mainloop()
