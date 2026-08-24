#!/usr/bin/env python3
"""
Modern Glassmorphism Web App for YouTube Video API Auto-Uploader Agent
=======================================================================
Runs a local Flask web server on http://localhost:5000 with a sleek, 
responsive HTML/CSS/JS interface. Automatically opens your web browser!
"""

import os
import sys
import json
import time
import webbrowser
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from youtube_manual_uploader import YouTubeManualUploaderAgent

app = Flask(__name__, template_folder="templates")
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def handle_upload():
    try:
        if "video_file" not in request.files:
            return jsonify({"status": "error", "message": "No video file provided"}), 400

        video_file = request.files["video_file"]
        if not video_file or video_file.filename == "":
            return jsonify({"status": "error", "message": "Selected video file is empty"}), 400

        video_filename = secure_filename(video_file.filename)
        saved_video_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{int(time.time())}_{video_filename}")
        video_file.save(saved_video_path)

        title = request.form.get("title", "").strip()
        if not title:
            title = os.path.splitext(video_filename)[0].replace("_", " ").title()

        description = request.form.get("description", "").strip() or f"Uploaded via Web Agent on {title}."
        tags_raw = request.form.get("tags", "").strip()
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else ["Video", "Automation"]
        privacy = request.form.get("privacy", "public")
        category_id = request.form.get("category", "28")

        # Thumbnail handling
        thumbnail_path = None
        if "thumbnail_file" in request.files:
            thumb_file = request.files["thumbnail_file"]
            if thumb_file and thumb_file.filename != "":
                thumb_filename = secure_filename(thumb_file.filename)
                thumbnail_path = os.path.join(app.config["UPLOAD_FOLDER"], f"thumb_{int(time.time())}_{thumb_filename}")
                thumb_file.save(thumbnail_path)

        print("="*60)
        print("🚀 WEB AGENT: PROCESSING VIDEO UPLOAD")
        print(f"📌 File: {saved_video_path}")
        print(f"📌 Title: {title}")
        print("="*60)

        agent = YouTubeManualUploaderAgent()
        video_url = agent.upload_video(
            video_path=saved_video_path,
            title=title,
            description=description,
            tags=tags,
            privacy_status=privacy,
            category_id=category_id,
            thumbnail_path=thumbnail_path
        )

        if video_url:
            video_id = video_url.split("/")[-1]
            return jsonify({
                "status": "success",
                "video_url": video_url,
                "video_id": video_id,
                "title": title
            })
        else:
            return jsonify({"status": "error", "message": "YouTube Upload failed. Check server logs or OAuth credentials."}), 500

    except Exception as e:
        print(f"[-] Web Upload Handler Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def main():
    port = 5000
    url = f"http://localhost:{port}"
    print("======================================================")
    print("🚀 YOUTUBE AUTO-UPLOADER WEB AGENT RUNNING")
    print(f"🌐 Web Interface URL: {url}")
    print("======================================================")
    
    # Automatically open web browser
    try:
        webbrowser.open(url)
    except Exception:
        pass

    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()
