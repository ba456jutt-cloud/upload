#!/usr/bin/env python3
"""
Glassmorphism Web Assistant: Auto-Git Push & YouTube Uploader
============================================================
Runs a local Flask web server on http://localhost:5001 with a sleek HTML/CSS UI.
Overwrites old video/thumbnail files to save disk space, generates metadata/video_info.json,
increases Git HTTP postBuffer to 1GB to prevent RPC/curl errors on Windows/Linux,
and automatically runs 'git add', 'git commit', and 'git push' with saved GitHub Token!
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

# Load .env file automatically
env_file = os.path.join(PROJECT_DIR, ".env")
if os.path.exists(env_file):
    with open(env_file, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#") and "=" in line:
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    return render_template("auto_push.html")

@app.route("/auto-push", methods=["POST"])
def handle_auto_push():
    try:
        video_url = request.form.get("video_url", "").strip()
        video_file = request.files.get("video_file")

        if not video_url and (not video_file or video_file.filename == ""):
            return jsonify({"status": "error", "message": "Please select a local video file OR paste a Google Drive link!"}), 400

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

        dest_video_name = ""
        saved_video_path = "Google Drive Link"

        # 3. Save new video file if provided (Overwriting active_video.mp4)
        if video_file and video_file.filename != "":
            video_filename = secure_filename(video_file.filename)
            video_ext = os.path.splitext(video_filename)[1] or ".mp4"
            dest_video_name = f"active_video{video_ext}"
            saved_video_path = os.path.join(INPUT_VIDEOS_DIR, dest_video_name)
            video_file.save(saved_video_path)
        else:
            video_filename = "Google_Drive_Video"

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
            "video_filename": f"input_videos/{dest_video_name}" if dest_video_name else "",
            "video_url": video_url,
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

        # 6b. Auto-Restore Safeguard for .github/workflows/youtube_manual_upload.yml (Windows Hidden File Protection)
        workflow_dir = os.path.join(PROJECT_DIR, ".github", "workflows")
        workflow_file = os.path.join(workflow_dir, "youtube_manual_upload.yml")
        os.makedirs(workflow_dir, exist_ok=True)
        if not os.path.exists(workflow_file):
            print("[*] Auto-Restoring missing .github/workflows/youtube_manual_upload.yml workflow file...")
            workflow_content = """name: Autonomous YouTube API Video Uploader Action

on:
  push:
    paths:
      - 'input_videos/**'
      - 'thumbnails/**'
      - 'metadata/**'
  workflow_dispatch:
    inputs:
      video_filename:
        description: 'Video Filename'
        required: false
        default: 'input_videos/my_video.mp4'
      title:
        description: 'YouTube Video Title'
        required: false
        default: ''
      description:
        description: 'YouTube Video Description'
        required: false
        default: ''
      privacy_status:
        description: 'Privacy Status'
        required: false
        default: 'public'
      tags:
        description: 'Tags'
        required: false
        default: 'Cybersecurity,Python,Automation'

jobs:
  upload-to-youtube:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository Code
        uses: actions/checkout@v4
        with:
          lfs: true

      - name: Set up Python 3.10
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install Google YouTube API Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install google-api-python-client google-auth-oauthlib google-auth-httplib2

      - name: Execute Autonomous YouTube Upload Agent
        env:
          YOUTUBE_REFRESH_TOKEN: ${{ secrets.YOUTUBE_REFRESH_TOKEN }}
          YOUTUBE_CLIENT_SECRET_JSON: ${{ secrets.YOUTUBE_CLIENT_SECRET_JSON }}
        run: |
          if [ "${{ github.event_name }}" = "workflow_dispatch" ] && [ -n "${{ github.event.inputs.title }}" ]; then
            python youtube_manual_uploader.py \\
              --video "${{ github.event.inputs.video_filename }}" \\
              --title "${{ github.event.inputs.title }}" \\
              --description "${{ github.event.inputs.description }}" \\
              --privacy "${{ github.event.inputs.privacy_status }}" \\
              --tags "${{ github.event.inputs.tags }}"
          else
            python youtube_manual_uploader.py --metadata metadata/video_info.json
          fi
"""
            with open(workflow_file, "w", encoding="utf-8") as wf:
                wf.write(workflow_content)

        print("="*60)
        print("🚀 WEB AGENT: EXECUTING GIT CONFIG, STAGING & AUTOMATED PUSH")
        print(f"📌 Video: {saved_video_path}")
        print(f"📌 Title: {title}")
        print("="*60)

        # 7. Auto-configure Git Buffer Size to 1GB to prevent RPC/curl 55 Send failure errors
        subprocess.run(["git", "config", "http.postBuffer", "1048576000"], cwd=PROJECT_DIR, check=False)
        subprocess.run(["git", "config", "http.maxRequestBuffer", "1048576000"], cwd=PROJECT_DIR, check=False)
        subprocess.run(["git", "config", "core.compression", "0"], cwd=PROJECT_DIR, check=False)

        # 8. Ensure Git Repository and Remote Destination are configured
        if not os.path.exists(os.path.join(PROJECT_DIR, ".git")):
            subprocess.run(["git", "init"], cwd=PROJECT_DIR, check=False)
        
        # Always rename current branch to 'main' on both Windows & Linux
        subprocess.run(["git", "branch", "-M", "main"], cwd=PROJECT_DIR, check=False)

        gh_user = os.getenv("GITHUB_USERNAME", "ba456jutt-cloud").strip()
        gh_token = os.getenv("GITHUB_TOKEN", "").strip()
        gh_repo = os.getenv("GITHUB_REPO", "upload").strip()

        if gh_user and gh_token and gh_token != "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN":
            auth_remote_url = f"https://{gh_user}:{gh_token}@github.com/{gh_user}/{gh_repo}.git"
        else:
            auth_remote_url = f"https://github.com/{gh_user}/{gh_repo}.git"

        # Add or update git remote origin
        res_remote = subprocess.run(["git", "remote", "set-url", "origin", auth_remote_url], cwd=PROJECT_DIR, capture_output=True, text=True)
        if res_remote.returncode != 0:
            subprocess.run(["git", "remote", "add", "origin", auth_remote_url], cwd=PROJECT_DIR, check=False)

        # 9. Execute Git Commands
        subprocess.run(["git", "add", "."], cwd=PROJECT_DIR, check=True)
        commit_msg = f"Auto-Upload Video: {title}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROJECT_DIR, check=False)

        # Explicitly push with upstream tracking
        push_res = subprocess.run(["git", "push", "-u", "origin", "main"], cwd=PROJECT_DIR, capture_output=True, text=True)
        if push_res.returncode != 0:
            # Fallback for force update
            push_res = subprocess.run(["git", "push", "--force", "-u", "origin", "main"], cwd=PROJECT_DIR, capture_output=True, text=True)

        if push_res.returncode == 0:
            return jsonify({
                "status": "success",
                "message": "Files overwritten, committed, and pushed to GitHub successfully!",
                "commit_msg": commit_msg
            })
        else:
            stderr_out = push_res.stderr or push_res.stdout or "Unknown git error"
            print(f"[-] Git Push Error Output: {stderr_out}")
            return jsonify({
                "status": "error",
                "message": f"Git Push Failed: {stderr_out}"
            }), 500

    except Exception as e:
        print(f"[-] Web Auto-Push Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def main():
    port = 5001
    url = f"http://localhost:{port}"
    print("="*60)
    print("🚀 AUTO-GIT PUSH HTML/CSS WEB APP RUNNING")
    print(f"🌐 Web Interface URL: {url}")
    print("="*60)

    try:
        webbrowser.open(url)
    except Exception:
        pass

    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()
