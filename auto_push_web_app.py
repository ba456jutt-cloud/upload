#!/usr/bin/env python3
"""
Glassmorphism Web Assistant: Auto-Git Push & YouTube Uploader
============================================================
Runs a local Flask web server on http://localhost:5001 with a sleek HTML/CSS UI.
Overwrites old video/thumbnail files to save disk space, generates metadata/video_info.json,
and automatically runs 'git add', 'git commit', and 'git push'!
"""

import os
import sys
import json
import shutil
import subprocess
import time
import webbrowser
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_VIDEOS_DIR = os.path.join(PROJECT_DIR, "input_videos")
THUMBNAILS_DIR = os.path.join(PROJECT_DIR, "thumbnails")
METADATA_DIR = os.path.join(PROJECT_DIR, "metadata")

os.makedirs(INPUT_VIDEOS_DIR, exist_ok=True)
os.makedirs(THUMBNAILS_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)

app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    return render_template("auto_push.html")

@app.route("/auto-push", methods=["POST"])
def handle_auto_push():
    try:
        if "video_file" not in request.files:
            return jsonify({"status": "error", "message": "No video file provided"}), 400

        video_file = request.files["video_file"]
        if not video_file or video_file.filename == "":
            return jsonify({"status": "error", "message": "Selected video file is empty"}), 400

        # 1. Cleanup old video files in input_videos/ (save space!)
        for old_f in os.listdir(INPUT_VIDEOS_DIR):
            if old_f != ".gitkeep":
                try:
                    os.remove(os.path.join(INPUT_VIDEOS_DIR, old_f))
                except Exception:
                    pass

        # 2. Cleanup old thumbnail files in thumbnails/ (save space!)
        for old_f in os.listdir(THUMBNAILS_DIR):
            if old_f != ".gitkeep":
                try:
                    os.remove(os.path.join(THUMBNAILS_DIR, old_f))
                except Exception:
                    pass

        # 3. Save new video file (Overwriting active_video.mp4)
        video_filename = secure_filename(video_file.filename)
        video_ext = os.path.splitext(video_filename)[1] or ".mp4"
        dest_video_name = f"active_video{video_ext}"
        saved_video_path = os.path.join(INPUT_VIDEOS_DIR, dest_video_name)
        video_file.save(saved_video_path)

        # 4. Save new thumbnail file if provided
        dest_thumb_name = ""
        if "thumbnail_file" in request.files:
            thumb_file = request.files["thumbnail_file"]
            if thumb_file and thumb_file.filename != "":
                thumb_filename = secure_filename(thumb_file.filename)
                thumb_ext = os.path.splitext(thumb_filename)[1] or ".png"
                dest_thumb_name = f"active_thumbnail{thumb_ext}"
                saved_thumb_path = os.path.join(THUMBNAILS_DIR, dest_thumb_name)
                thumb_file.save(saved_thumb_path)

        # 5. Extract Form Metadata
        title = request.form.get("title", "").strip()
        if not title:
            title = os.path.splitext(video_filename)[0].replace("_", " ").title()

        description = request.form.get("description", "").strip() or f"Uploaded automatically via YouTube Agent on {title}."
        tags_raw = request.form.get("tags", "").strip()
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else ["Video", "Tutorial", "Automation"]
        privacy = request.form.get("privacy", "public")
        category_id = request.form.get("category", "28")

        # 6. Generate metadata/video_info.json
        meta_data = {
            "video_filename": f"input_videos/{dest_video_name}",
            "title": title,
            "description": description,
            "tags": tags,
            "privacy_status": privacy,
            "category_id": category_id,
            "thumbnail_filename": f"thumbnails/{dest_thumb_name}" if dest_thumb_name else ""
        }

        meta_file_path = os.path.join(METADATA_DIR, "video_info.json")
        with open(meta_file_path, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, indent=2)

        print("="*60)
        print("🚀 WEB AGENT: EXECUTING GIT STAGING & AUTOMATED PUSH")
        print(f"📌 Video: {saved_video_path}")
        print(f"📌 Title: {title}")
        print("="*60)

        # 7. Execute Git Commands
        subprocess.run(["git", "add", "."], cwd=PROJECT_DIR, check=True)
        commit_msg = f"Auto-Upload Video: {title}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROJECT_DIR, check=False)

        push_res = subprocess.run(["git", "push"], cwd=PROJECT_DIR, capture_output=True, text=True)

        if push_res.returncode == 0:
            return jsonify({
                "status": "success",
                "message": "Files overwritten, committed, and pushed to GitHub successfully!",
                "commit_msg": commit_msg
            })
        else:
            return jsonify({
                "status": "success",
                "message": f"Files & metadata created! Git output: {push_res.stderr or push_res.stdout or 'Committed locally.'}",
                "commit_msg": commit_msg
            })

    except Exception as e:
        print(f"[-] Web Auto-Push Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def main():
    port = 5001
    url = f"http://localhost:{port}"
    print("======================================================")
    print("🚀 AUTO-GIT PUSH HTML/CSS WEB APP RUNNING")
    print(f"🌐 Web Interface URL: {url}")
    print("======================================================")

    try:
        webbrowser.open(url)
    except Exception:
        pass

    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()
