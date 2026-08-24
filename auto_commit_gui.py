#!/usr/bin/env python3
"""
GUI Assistant: Select Video & Thumbnail, Create JSON Metadata, and Auto-Git Push
================================================================================
1. Opens File Picker dialogs to select Video & Thumbnail from laptop.
2. Copies files into input_videos/ and thumbnails/ folders.
3. Automatically generates valid metadata/video_info.json (No JSON syntax errors!).
4. Automatically runs 'git add', 'git commit', and 'git push' so you NEVER type git commands.
5. GitHub Actions triggers automatically in the cloud to publish video on YouTube!
"""

import os
import sys
import json
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_VIDEOS_DIR = os.path.join(PROJECT_DIR, "input_videos")
THUMBNAILS_DIR = os.path.join(PROJECT_DIR, "thumbnails")
METADATA_DIR = os.path.join(PROJECT_DIR, "metadata")

os.makedirs(INPUT_VIDEOS_DIR, exist_ok=True)
os.makedirs(THUMBNAILS_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)

class AutoGitPushGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video & Thumbnail Auto-Git Push Assistant 🚀")
        self.root.geometry("740x820")
        self.root.configure(bg="#090d16")
        self.root.resizable(True, True)

        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background="#090d16", foreground="#f8fafc", font=("Segoe UI", 10))
        self.style.configure("TLabel", background="#090d16", foreground="#cbd5e1", font=("Segoe UI", 10, "bold"))
        self.style.configure("Header.TLabel", background="#090d16", foreground="#38bdf8", font=("Segoe UI", 16, "bold"))
        self.style.configure("SubHeader.TLabel", background="#090d16", foreground="#94a3b8", font=("Segoe UI", 9))
        self.style.configure("Browse.TButton", background="#1e293b", foreground="#ffffff", font=("Segoe UI", 9))
        self.style.map("Browse.TButton", background=[("active", "#334155")])
        self.style.configure("Push.TButton", background="#16a34a", foreground="#ffffff", font=("Segoe UI", 12, "bold"))
        self.style.map("Push.TButton", background=[("active", "#15803d")])

        # State Variables
        self.source_video_path = ""
        self.source_thumbnail_path = ""
        self.privacy_var = tk.StringVar(value="public")
        self.category_var = tk.StringVar(value="28 (Science & Tech)")

        self._build_ui()

    def _build_ui(self):
        # Header
        header_frame = ttk.Frame(self.root, padding="20 15 20 10")
        header_frame.pack(fill="x")

        title_lbl = ttk.Label(header_frame, text="🎬 YouTube Video & Thumbnail Auto-Git Push", style="Header.TLabel")
        title_lbl.pack(anchor="w")

        sub_lbl = ttk.Label(header_frame, text="Select files, type details, click Auto-Push. GitHub Actions uploads to YouTube automatically!", style="SubHeader.TLabel")
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # Main Form Frame
        form_frame = ttk.Frame(self.root, padding="20 10 20 10")
        form_frame.pack(fill="both", expand=True)

        # 1. Video Picker
        ttk.Label(form_frame, text="📹 1. Select Video File (.mp4, .mkv, .mov):").pack(anchor="w", pady=(10, 4))
        vid_box = ttk.Frame(form_frame)
        vid_box.pack(fill="x")

        self.vid_entry = tk.Entry(vid_box, bg="#1e293b", fg="#38bdf8", insertbackground="#ffffff", relief="flat", font=("Consolas", 9, "bold"))
        self.vid_entry.pack(side="left", fill="x", expand=True, ipady=6, ipadx=6)

        btn_browse_vid = ttk.Button(vid_box, text="📁 Browse Video...", style="Browse.TButton", command=self.browse_video)
        btn_browse_vid.pack(side="right", padx=(8, 0))

        # 2. Thumbnail Picker
        ttk.Label(form_frame, text="🖼️ 2. Select Thumbnail Image (.png, .jpg):").pack(anchor="w", pady=(12, 4))
        thumb_box = ttk.Frame(form_frame)
        thumb_box.pack(fill="x")

        self.thumb_entry = tk.Entry(thumb_box, bg="#1e293b", fg="#38bdf8", insertbackground="#ffffff", relief="flat", font=("Consolas", 9, "bold"))
        self.thumb_entry.pack(side="left", fill="x", expand=True, ipady=6, ipadx=6)

        btn_browse_thumb = ttk.Button(thumb_box, text="🖼️ Browse Image...", style="Browse.TButton", command=self.browse_thumbnail)
        btn_browse_thumb.pack(side="right", padx=(8, 0))

        # 3. Title Entry
        ttk.Label(form_frame, text="📌 3. Video Title:").pack(anchor="w", pady=(12, 4))
        self.title_entry = tk.Entry(form_frame, bg="#1e293b", fg="#f8fafc", insertbackground="#ffffff", relief="flat", font=("Segoe UI", 10))
        self.title_entry.pack(fill="x", ipady=6, ipadx=6)

        # 4. Description Box
        ttk.Label(form_frame, text="📝 4. Video Description:").pack(anchor="w", pady=(12, 4))
        self.desc_text = tk.Text(form_frame, height=4, bg="#1e293b", fg="#f8fafc", insertbackground="#ffffff", relief="flat", font=("Segoe UI", 9.5), wrap="word")
        self.desc_text.pack(fill="x", ipady=4, ipadx=6)

        # 5. Tags Entry
        ttk.Label(form_frame, text="🏷️ 5. Tags (Comma separated):").pack(anchor="w", pady=(12, 4))
        self.tags_entry = tk.Entry(form_frame, bg="#1e293b", fg="#f8fafc", insertbackground="#ffffff", relief="flat", font=("Segoe UI", 10))
        self.tags_entry.insert(0, "Cybersecurity, AI, Python, Automation")
        self.tags_entry.pack(fill="x", ipady=6, ipadx=6)

        # 6. Options Row (Privacy & Category)
        opts_frame = ttk.Frame(form_frame)
        opts_frame.pack(fill="x", pady=(12, 4))

        # Privacy
        priv_box = ttk.Frame(opts_frame)
        priv_box.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Label(priv_box, text="🔒 Privacy Status:").pack(anchor="w", pady=(0, 4))
        priv_combo = ttk.Combobox(priv_box, textvariable=self.privacy_var, values=["public", "unlisted", "private"], state="readonly")
        priv_combo.pack(fill="x", ipady=4)

        # Category
        cat_box = ttk.Frame(opts_frame)
        cat_box.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ttk.Label(cat_box, text="📂 Category:").pack(anchor="w", pady=(0, 4))
        cat_combo = ttk.Combobox(cat_box, textvariable=self.category_var, values=["28 (Science & Tech)", "27 (Education)", "24 (Entertainment)"], state="readonly")
        cat_combo.pack(fill="x", ipady=4)

        # Output Log Window
        ttk.Label(form_frame, text="📊 Git Push & Action Progress Log:").pack(anchor="w", pady=(12, 4))
        self.log_text = tk.Text(form_frame, height=5, bg="#020617", fg="#38bdf8", relief="flat", font=("Consolas", 8.5), wrap="word")
        self.log_text.pack(fill="both", expand=True)

        # Big Action Button
        btn_frame = ttk.Frame(self.root, padding="20 10 20 20")
        btn_frame.pack(fill="x")

        self.btn_push = ttk.Button(btn_frame, text="🚀 AUTO-PUSH TO GITHUB (TRIGGER YOUTUBE UPLOAD)", style="Push.TButton", command=self.start_push_thread)
        self.btn_push.pack(fill="x", ipady=12)

    def browse_video(self):
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.mkv *.mov *.avi"), ("All Files", "*.*")]
        )
        if filename:
            self.source_video_path = filename
            self.vid_entry.delete(0, "end")
            self.vid_entry.insert(0, filename)

            # Auto fill title if empty
            if not self.title_entry.get().strip():
                default_title = os.path.splitext(os.path.basename(filename))[0].replace("_", " ").title()
                self.title_entry.insert(0, default_title)

    def browse_thumbnail(self):
        filename = filedialog.askopenfilename(
            title="Select Thumbnail Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg"), ("All Files", "*.*")]
        )
        if filename:
            self.source_thumbnail_path = filename
            self.thumb_entry.delete(0, "end")
            self.thumb_entry.insert(0, filename)

    def log(self, text: str):
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")

    def start_push_thread(self):
        video_src = self.vid_entry.get().strip()
        title = self.title_entry.get().strip()

        if not video_src or not os.path.exists(video_src):
            messagebox.showerror("Error", "Please select a valid Video File before pushing!")
            return

        if not title:
            messagebox.showerror("Error", "Please enter a Video Title!")
            return

        self.btn_push.configure(state="disabled")
        self.log_text.delete("1.0", "end")
        self.log("======================================================")
        self.log("🚀 PREPARING FILES AND EXECUTING AUTOMATED GIT PUSH")
        self.log("======================================================")

        t = threading.Thread(target=self._push_task, args=(video_src, title), daemon=True)
        t.start()

    def _push_task(self, video_src: str, title: str):
        try:
            # 1. Copy Video file into input_videos/
            video_basename = os.path.basename(video_src)
            dest_video_path = os.path.join(INPUT_VIDEOS_DIR, video_basename)
            self.log(f"[*] Copying video file to input_videos/{video_basename}...")
            shutil.copy2(video_src, dest_video_path)

            # 2. Copy Thumbnail file into thumbnails/ if selected
            thumb_src = self.thumb_entry.get().strip()
            thumb_basename = ""
            if thumb_src and os.path.exists(thumb_src):
                thumb_basename = os.path.basename(thumb_src)
                dest_thumb_path = os.path.join(THUMBNAILS_DIR, thumb_basename)
                self.log(f"[*] Copying thumbnail image to thumbnails/{thumb_basename}...")
                shutil.copy2(thumb_src, dest_thumb_path)

            # 3. Create metadata/video_info.json
            description = self.desc_text.get("1.0", "end").strip() or f"Uploaded automatically via YouTube Agent on {title}."
            tags_raw = self.tags_entry.get().strip()
            tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else ["Video", "Tutorial"]
            privacy = self.privacy_var.get()
            category_id = self.category_var.get().split()[0]

            meta_data = {
                "video_filename": f"input_videos/{video_basename}",
                "title": title,
                "description": description,
                "tags": tags,
                "privacy_status": privacy,
                "category_id": category_id,
                "thumbnail_filename": f"thumbnails/{thumb_basename}" if thumb_basename else ""
            }

            meta_file_path = os.path.join(METADATA_DIR, "video_info.json")
            with open(meta_file_path, "w", encoding="utf-8") as f:
                json.dump(meta_data, f, indent=2)

            self.log("[+] Generated metadata/video_info.json successfully!")

            # 4. Execute Automated Git Add, Commit, Push
            self.log("[*] Running 'git add .'...")
            subprocess.run(["git", "add", "."], cwd=PROJECT_DIR, check=True)

            commit_msg = f"Auto-Upload Video: {title}"
            self.log(f"[*] Running 'git commit -m \"{commit_msg}\"'...")
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROJECT_DIR, check=False)

            self.log("[*] Running 'git push' to GitHub...")
            push_res = subprocess.run(["git", "push"], cwd=PROJECT_DIR, capture_output=True, text=True)

            if push_res.returncode == 0:
                self.log("======================================================")
                self.log("🎉 SUCCESS! FILES COMMITTED & PUSHED TO GITHUB!")
                self.log("🤖 GitHub Actions is now automatically uploading your video to YouTube!")
                self.log("======================================================")
                messagebox.showinfo(
                    "Success",
                    "Files Committed & Pushed to GitHub Successfully!\n\nGitHub Actions is now automatically uploading your video to YouTube in the cloud!"
                )
            else:
                self.log(f"[-] Git Push Output/Error: {push_res.stderr or push_res.stdout}")
                self.log("[!] Note: Make sure your git remote origin is configured.")
                messagebox.showwarning("Git Warning", "Metadata & files prepared, but Git Push encountered output. Check log window.")

        except Exception as e:
            self.log(f"[-] Exception: {e}")
            messagebox.showerror("Error", f"Error: {e}")
        finally:
            self.root.after(0, lambda: self.btn_push.configure(state="normal"))

def main():
    root = tk.Tk()
    app = AutoGitPushGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
