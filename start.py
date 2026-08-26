#!/usr/bin/env python3
"""
1-Click Master Launcher: YouTube Auto-Uploader Agent
====================================================
Just run: python start.py
- Automatically sets UTF-8 encoding
- Automatically runs 'git lfs install' and configures 1GB Git HTTP postBuffer
- Automatically restores .github/workflows/youtube_manual_upload.yml if missing
- Automatically launches the Web App UI in your browser!
"""

import os
import sys
import subprocess
import webbrowser

# Force UTF-8 Encoding
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
os.environ["PYTHONIOENCODING"] = "utf-8"

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

def setup_environment_and_git():
    print("======================================================")
    print("🛠️ EXECUTING 1-CLICK AUTOMATED SYSTEM SETUP")
    print("======================================================")

    # 1. Run Git LFS Setup
    try:
        print("[*] Configuring Git LFS...")
        subprocess.run(["git", "lfs", "install"], cwd=PROJECT_DIR, check=False)
    except Exception as e:
        print(f"[!] Git LFS Warning: {e}")

    # 2. Configure 1GB Git HTTP postBuffer & Remote Destination
    try:
        print("[*] Setting Git HTTP Buffer to 1GB (postBuffer = 1048576000)...")
        subprocess.run(["git", "config", "http.postBuffer", "1048576000"], cwd=PROJECT_DIR, check=False)
        subprocess.run(["git", "config", "http.maxRequestBuffer", "1048576000"], cwd=PROJECT_DIR, check=False)
        subprocess.run(["git", "config", "core.compression", "0"], cwd=PROJECT_DIR, check=False)

        if not os.path.exists(os.path.join(PROJECT_DIR, ".git")):
            subprocess.run(["git", "init"], cwd=PROJECT_DIR, check=False)

        subprocess.run(["git", "branch", "-M", "main"], cwd=PROJECT_DIR, check=False)

        remote_url = "https://github.com/ba456jutt-cloud/upload.git"
        res_r = subprocess.run(["git", "remote", "set-url", "origin", remote_url], cwd=PROJECT_DIR, capture_output=True, text=True)
        if res_r.returncode != 0:
            subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=PROJECT_DIR, check=False)

        print("[+] Git Buffer, LFS & Remote Origin Configured Successfully!")
    except Exception as e:
        print(f"[!] Git Config Warning: {e}")

    # 3. Auto-Restore Missing .github/workflows/youtube_manual_upload.yml (Windows Hidden File Safeguard)
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
        print("[+] GitHub Actions Workflow File Restored Successfully!")

def launch_web_app():
    print("======================================================")
    print("🚀 LAUNCHING YOUTUBE AUTO-UPLOADER WEB APP")
    print("🌐 Opening Browser at: http://localhost:5001")
    print("======================================================")

    web_app_script = os.path.join(PROJECT_DIR, "auto_push_web_app.py")
    subprocess.run([sys.executable, web_app_script], cwd=PROJECT_DIR)

if __name__ == "__main__":
    setup_environment_and_git()
    launch_web_app()
