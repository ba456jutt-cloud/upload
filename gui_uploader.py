#!/usr/bin/env python3
"""
Modern Desktop GUI Application for YouTube Video & Metadata Uploader
=====================================================================
Built using Tkinter + Modern Dark Theme UI styling.
Allows selecting video files & thumbnails via system File Explorer dialogs,
entering Title, Description, Tags, Privacy, and tracking upload progress.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from youtube_manual_uploader import YouTubeManualUploaderAgent

class ModernYouTubeUploaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube API Auto-Uploader Agent 🚀")
        self.root.geometry("720x780")
        self.root.configure(bg="#0f172a") # Slate Dark Theme
        self.root.resizable(True, True)

        # Style Config
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configure Custom Colors
        self.style.configure(".", background="#0f172a", foreground="#f8fafc", font=("Segoe UI", 10))
        self.style.configure("TLabel", background="#0f172a", foreground="#cbd5e1", font=("Segoe UI", 10, "bold"))
        self.style.configure("Header.TLabel", background="#0f172a", foreground="#38bdf8", font=("Segoe UI", 16, "bold"))
        self.style.configure("SubHeader.TLabel", background="#0f172a", foreground="#94a3b8", font=("Segoe UI", 9))
        self.style.configure("TButton", background="#2563eb", foreground="#ffffff", font=("Segoe UI", 10, "bold"), borderwidth=0)
        self.style.map("TButton", background=[("active", "#1d4ed8")])
        self.style.configure("Browse.TButton", background="#334155", foreground="#ffffff", font=("Segoe UI", 9))
        self.style.map("Browse.TButton", background=[("active", "#475569")])
        self.style.configure("Upload.TButton", background="#16a34a", foreground="#ffffff", font=("Segoe UI", 12, "bold"))
        self.style.map("Upload.TButton", background=[("active", "#15803d")])

        # State Variables
        self.video_path_var = tk.StringVar()
        self.thumbnail_path_var = tk.StringVar()
        self.privacy_var = tk.StringVar(value="public")
        self.category_var = tk.StringVar(value="28 (Science & Tech)")

        self._build_ui()

    def _build_ui(self):
        # Header Container
        header_frame = ttk.Frame(self.root, padding="20 15 20 10")
        header_frame.pack(fill="x")

        title_lbl = ttk.Label(header_frame, text="🚀 YouTube Video API Uploader", style="Header.TLabel")
        title_lbl.pack(anchor="w")

        subtitle_lbl = ttk.Label(header_frame, text="Select your video, add metadata, and publish directly to YouTube.", style="SubHeader.TLabel")
        subtitle_lbl.pack(anchor="w", pady=(2, 0))

        # Main Form Container
        form_frame = ttk.Frame(self.root, padding="20 10 20 10")
        form_frame.pack(fill="both", expand=True)

        # 1. Select Video File Button + Display Path
        ttk.Label(form_frame, text="📹 1. Select Video File (.mp4, .mkv, .mov):").pack(anchor="w", pady=(10, 4))
        vid_box = ttk.Frame(form_frame)
        vid_box.pack(fill="x")

        self.vid_entry = tk.Entry(vid_box, textvariable=self.video_path_var, bg="#1e293b", fg="#f8fafc", insertbackground="#ffffff", relief="flat", font=("Consolas", 9))
        self.vid_entry.pack(side="left", fill="x", expand=True, ipady=6, ipadx=6)

        btn_browse_vid = ttk.Button(vid_box, text="📁 Browse Video...", style="Browse.TButton", command=self.browse_video)
        btn_browse_vid.pack(side="right", padx=(8, 0))

        # 2. Title Entry
        ttk.Label(form_frame, text="📌 2. Video Title:").pack(anchor="w", pady=(12, 4))
        self.title_entry = tk.Entry(form_frame, bg="#1e293b", fg="#f8fafc", insertbackground="#ffffff", relief="flat", font=("Segoe UI", 10))
        self.title_entry.pack(fill="x", ipady=6, ipadx=6)

        # 3. Description Text Box
        ttk.Label(form_frame, text="📝 3. Video Description:").pack(anchor="w", pady=(12, 4))
        self.desc_text = tk.Text(form_frame, height=5, bg="#1e293b", fg="#f8fafc", insertbackground="#ffffff", relief="flat", font=("Segoe UI", 95), wrap="word")
        self.desc_text.pack(fill="x", ipady=4, ipadx=6)

        # 4. Tags Entry
        ttk.Label(form_frame, text="🏷️ 4. Tags (Comma separated):").pack(anchor="w", pady=(12, 4))
        self.tags_entry = tk.Entry(form_frame, bg="#1e293b", fg="#f8fafc", insertbackground="#ffffff", relief="flat", font=("Segoe UI", 10))
        self.tags_entry.insert(0, "Cybersecurity, AI, Python, Automation")
        self.tags_entry.pack(fill="x", ipady=6, ipadx=6)

        # 5. Options Row (Privacy & Category)
        opts_frame = ttk.Frame(form_frame)
        opts_frame.pack(fill="x", pady=(12, 4))

        # Privacy Combo
        priv_box = ttk.Frame(opts_frame)
        priv_box.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Label(priv_box, text="🔒 Privacy Status:").pack(anchor="w", pady=(0, 4))
        priv_combo = ttk.Combobox(priv_box, textvariable=self.privacy_var, values=["public", "unlisted", "private"], state="readonly")
        priv_combo.pack(fill="x", ipady=4)

        # Category Combo
        cat_box = ttk.Frame(opts_frame)
        cat_box.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ttk.Label(cat_box, text="📂 Category:").pack(anchor="w", pady=(0, 4))
        cat_combo = ttk.Combobox(cat_box, textvariable=self.category_var, values=["28 (Science & Tech)", "27 (Education)", "24 (Entertainment)"], state="readonly")
        cat_combo.pack(fill="x", ipady=4)

        # 6. Thumbnail Selection Row
        ttk.Label(form_frame, text="🖼️ 6. Custom Thumbnail Image (Optional):").pack(anchor="w", pady=(12, 4))
        thumb_box = ttk.Frame(form_frame)
        thumb_box.pack(fill="x")

        self.thumb_entry = tk.Entry(thumb_box, textvariable=self.thumbnail_path_var, bg="#1e293b", fg="#f8fafc", insertbackground="#ffffff", relief="flat", font=("Consolas", 9))
        self.thumb_entry.pack(side="left", fill="x", expand=True, ipady=6, ipadx=6)

        btn_browse_thumb = ttk.Button(thumb_box, text="🖼️ Browse Image...", style="Browse.TButton", command=self.browse_thumbnail)
        btn_browse_thumb.pack(side="right", padx=(8, 0))

        # Progress Log Box
        ttk.Label(form_frame, text="📊 Live Upload Log Output:").pack(anchor="w", pady=(14, 4))
        self.log_text = tk.Text(form_frame, height=6, bg="#020617", fg="#38bdf8", relief="flat", font=("Consolas", 85), wrap="word")
        self.log_text.pack(fill="both", expand=True)

        # Bottom Upload Button
        btn_frame = ttk.Frame(self.root, padding="20 10 20 20")
        btn_frame.pack(fill="x")

        self.btn_upload = ttk.Button(btn_frame, text="🚀 UPLOAD VIDEO TO YOUTUBE", style="Upload.TButton", command=self.start_upload_thread)
        self.btn_upload.pack(fill="x", ipady=10)

    def browse_video(self):
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.mkv *.mov *.avi"), ("All Files", "*.*")]
        )
        if filename:
            self.video_path_var.set(filename)
            # Auto populate title if empty
            if not self.title_entry.get().strip():
                default_title = os.path.splitext(os.path.basename(filename))[0].replace("_", " ").title()
                self.title_entry.insert(0, default_title)

    def browse_thumbnail(self):
        filename = filedialog.askopenfilename(
            title="Select Thumbnail Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg"), ("All Files", "*.*")]
        )
        if filename:
            self.thumbnail_path_var.set(filename)

    def log(self, text: str):
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")

    def start_upload_thread(self):
        video_path = self.video_path_var.get().strip()
        title = self.title_entry.get().strip()
        description = self.desc_text.get("1.0", "end").strip()

        if not video_path or not os.path.exists(video_path):
            messagebox.showerror("Error", "Please select a valid Video File before uploading!")
            return

        if not title:
            messagebox.showerror("Error", "Please enter a Video Title!")
            return

        self.btn_upload.configure(state="disabled")
        self.log_text.delete("1.0", "end")
        self.log("======================================================")
        self.log("🚀 STARTING YOUTUBE VIDEO UPLOAD PIPELINE")
        self.log(f"📌 File: {video_path}")
        self.log(f"📌 Title: {title}")
        self.log("======================================================")

        # Run upload in background thread to prevent UI freezing
        t = threading.Thread(target=self._upload_task, args=(video_path, title, description), daemon=True)
        t.start()

    def _upload_task(self, video_path: str, title: str, description: str):
        try:
            tags_raw = self.tags_entry.get().strip()
            tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else ["Video", "Tutorial"]
            privacy = self.privacy_var.get()
            category_str = self.category_var.get().split()[0] # e.g. "28"
            thumbnail = self.thumbnail_path_var.get().strip() or None

            self.log("[*] Authenticating with YouTube Data API v3...")
            agent = YouTubeManualUploaderAgent()

            self.log("[*] Uploading video file in 10MB chunks...")
            video_url = agent.upload_video(
                video_path=video_path,
                title=title,
                description=description,
                tags=tags,
                privacy_status=privacy,
                category_id=category_str,
                thumbnail_path=thumbnail
            )

            if video_url:
                self.log("======================================================")
                self.log(f"🎉 SUCCESS! VIDEO PUBLISHED: {video_url}")
                self.log("======================================================")
                messagebox.showinfo("Success", f"Video Uploaded Successfully!\n\nLink: {video_url}")
            else:
                self.log("[-] Upload Failed. Check credentials or logs.")
                messagebox.showerror("Failed", "Upload failed. See log window for details.")

        except Exception as e:
            self.log(f"[-] Exception during upload: {e}")
            messagebox.showerror("Error", f"Upload Error: {e}")
        finally:
            self.root.after(0, lambda: self.btn_upload.configure(state="normal"))

def main():
    root = tk.Tk()
    app = ModernYouTubeUploaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
