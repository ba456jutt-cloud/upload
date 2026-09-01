#!/usr/bin/env python3
"""
Dedicated YouTube Manual Video & Description API Auto-Uploader Agent
=====================================================================
Uploads custom user videos with custom titles, descriptions, tags, and thumbnails
directly to YouTube via YouTube Data API v3 using headless OAuth refresh tokens.
"""

import os
import sys
import json
import time
import argparse
from typing import Dict, List, Optional

# Load .env file automatically if present
env_file = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_file):
    with open(env_file, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#") and "=" in line:
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

import re
import requests
import subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

CHUNK_SIZE = 10 * 1024 * 1024  # 10 MB resumable upload chunk size

def download_video_if_url(video_input: str) -> str:
    """If video_input is a Google Drive URL, File ID, or HTTP URL, downloads it to input_videos/cloud_video.mp4."""
    if not video_input:
        return video_input

    # Check if input is a URL or Google Drive link/ID
    is_url = video_input.startswith(("http://", "https://", "drive.google.com"))
    is_drive_id = bool(re.match(r'^[a-zA-Z0-9_-]{28,45}$', video_input))

    if not is_url and not is_drive_id and os.path.exists(video_input):
        return video_input

    out_file = os.path.join("input_videos", "cloud_video.mp4")
    os.makedirs("input_videos", exist_ok=True)

    # Google Drive extraction
    file_id = video_input
    if "drive.google.com" in video_input:
        match = re.search(r'/d/([a-zA-Z0-9_-]+)', video_input) or re.search(r'id=([a-zA-Z0-9_-]+)', video_input)
        if match:
            file_id = match.group(1)
            is_drive_id = True

    if is_drive_id:
        print(f"[*] Cloud Agent: Downloading 1GB+ video directly from Google Drive (ID: {file_id})...")
        # Try gdown CLI
        try:
            cmd = ["gdown", f"https://drive.google.com/uc?id={file_id}", "-O", out_file, "--fuzzy"]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0 and os.path.exists(out_file) and os.path.getsize(out_file) > 10000:
                print(f"[+] Google Drive Cloud Download Successful! ({os.path.getsize(out_file)/(1024*1024):.2f} MB)")
                return out_file
        except Exception:
            pass

        # Fallback to requests confirmation token download for large Google Drive files
        URL = "https://docs.google.com/uc?export=download"
        session = requests.Session()
        response = session.get(URL, params={'id': file_id}, stream=True)
        token = None
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                token = value
                break
        if token:
            response = session.get(URL, params={'id': file_id, 'confirm': token}, stream=True)
        if response.status_code == 200:
            with open(out_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
            if os.path.exists(out_file) and os.path.getsize(out_file) > 10000:
                print(f"[+] Google Drive Direct Download Successful! ({os.path.getsize(out_file)/(1024*1024):.2f} MB)")
                return out_file

    # General HTTP / yt-dlp download fallback
    if is_url:
        print(f"[*] Cloud Agent: Downloading video URL: {video_input}...")
        try:
            cmd = ["yt-dlp", "-o", out_file, "--force-overwrites", video_input]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0 and os.path.exists(out_file) and os.path.getsize(out_file) > 10000:
                print(f"[+] Web Video Download Successful! ({os.path.getsize(out_file)/(1024*1024):.2f} MB)")
                return out_file
        except Exception:
            pass

    return video_input

class YouTubeManualUploaderAgent:
    """Standalone Agent for uploading custom user videos & metadata to YouTube."""

    def __init__(self, refresh_token: Optional[str] = None, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.refresh_token = refresh_token or os.getenv("YOUTUBE_REFRESH_TOKEN")
        self.client_id = client_id or os.getenv("YOUTUBE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("YOUTUBE_CLIENT_SECRET")

        # Fallback to JSON secret string in env
        secret_json_str = os.getenv("YOUTUBE_CLIENT_SECRET_JSON")
        if secret_json_str and (not self.client_id or not self.client_secret):
            try:
                secret_data = json.loads(secret_json_str)
                installed = secret_data.get("installed") or secret_data.get("web") or secret_data
                self.client_id = installed.get("client_id")
                self.client_secret = installed.get("client_secret")
            except Exception as e:
                print(f"[-] Uploader Agent: Error parsing YOUTUBE_CLIENT_SECRET_JSON: {e}")

        if not self.refresh_token or not self.client_id or not self.client_secret:
            print("[!] Uploader Agent Fatal Error: Missing YouTube OAuth Credentials.")
            print("Please ensure YOUTUBE_REFRESH_TOKEN and YOUTUBE_CLIENT_SECRET_JSON (or CLIENT_ID/CLIENT_SECRET) are set.")
            sys.exit(1)

        try:
            creds = Credentials(
                token=None,
                refresh_token=self.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=["https://www.googleapis.com/auth/youtube.upload"]
            )
            self.youtube = build("youtube", "v3", credentials=creds)
            print("[+] Uploader Agent: Connected to YouTube Data API v3 Successfully!")
        except Exception as e:
            print(f"[-] Uploader Agent Connection Error: {e}")
            sys.exit(1)

    def set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """Sets custom thumbnail for uploaded video."""
        if not os.path.exists(thumbnail_path):
            alt_path = os.path.join("thumbnails", os.path.basename(thumbnail_path))
            if os.path.exists(alt_path):
                thumbnail_path = alt_path
            else:
                print(f"[-] Thumbnail File '{thumbnail_path}' not found. Skipping thumbnail upload.")
                return False
        try:
            print(f"[*] Uploading Thumbnail: {thumbnail_path}...")
            media = MediaFileUpload(thumbnail_path, mimetype="image/png")
            self.youtube.thumbnails().set(videoId=video_id, media_body=media).execute()
            print("[+] Custom Thumbnail Set Successfully!")
            return True
        except Exception as e:
            print(f"[-] Thumbnail Upload Error: {e}")
            return False

    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        privacy_status: str = "public",
        category_id: str = "28",
        thumbnail_path: Optional[str] = None
    ) -> Optional[str]:
        """Uploads custom video file and sets description, tags, privacy, and optional thumbnail."""

        if not os.path.exists(video_path):
            print(f"[-] Error: Video file '{video_path}' does not exist.")
            return None

        file_size = os.path.getsize(video_path)
        print("=" * 60)
        print("📹 YOUTUBE MANUAL UPLOADER AGENT INITIATED")
        print("=" * 60)
        print(f"📌 Video File:   {video_path} ({file_size / (1024 * 1024):.2f} MB)")
        print(f"📌 Title:        {title}")
        print(f"📌 Description:  {description[:80]}...")
        print(f"📌 Privacy:      {privacy_status}")
        print(f"📌 Category ID:  {category_id}")
        print("=" * 60)

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or ["Video", "Tutorial", "Automation"],
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False
            }
        }

        media = MediaFileUpload(video_path, chunksize=CHUNK_SIZE, resumable=True, mimetype="video/*")
        request = self.youtube.videos().insert(part="snippet,status", body=body, media_body=media)

        response = None
        start_time = time.time()

        while response is None:
            try:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    elapsed = time.time() - start_time
                    print(f"  -> Upload Progress: {progress}% ({elapsed:.1f}s)")
            except HttpError as e:
                print(f"[-] YouTube API HTTP Error: {e}")
                return None
            except Exception as e:
                print(f"[-] Upload Exception: {e}")
                return None

        video_id = response.get("id")
        video_url = f"https://youtu.be/{video_id}"

        # Set custom thumbnail if provided
        if thumbnail_path:
            self.set_thumbnail(video_id, thumbnail_path)

        print("=" * 60)
        print("🎉 SUCCESS! VIDEO PUBLISHED ON YOUTUBE!")
        print(f"🔗 Video URL: {video_url}")
        print(f"📌 Video ID:  {video_id}")
        print("=" * 60)

        # Log upload in history JSON
        self._log_history(video_id, video_url, title, video_path)
        return video_url

    def _log_history(self, video_id: str, video_url: str, title: str, file_path: str):
        history_file = "upload_history.json"
        history = []
        if os.path.exists(history_file):
            try:
                with open(history_file, "r") as f:
                    history = json.load(f)
            except Exception:
                history = []

        history.append({
            "video_id": video_id,
            "url": video_url,
            "title": title,
            "file": file_path,
            "uploaded_at": time.strftime("%Y-%m-%d %H:%M:%S")
        })

        with open(history_file, "w") as f:
            json.dump(history, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Manual YouTube Video Uploader Agent")
    parser.add_argument("--video", help="Path to video file")
    parser.add_argument("--title", help="Video title")
    parser.add_argument("--description", help="Video description")
    parser.add_argument("--tags", help="Comma-separated tags")
    parser.add_argument("--privacy", default="public", choices=["public", "unlisted", "private"])
    parser.add_argument("--thumbnail", help="Optional path to thumbnail image (PNG/JPG)")
    parser.add_argument("--metadata", default="metadata/video_info.json", help="Path to metadata JSON file")
    args = parser.parse_args()

    agent = YouTubeManualUploaderAgent()

    # Priority 1: Check if metadata JSON exists
    video_file = args.video
    title = args.title
    description = args.description
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
    privacy = args.privacy
    thumbnail = args.thumbnail

    if os.path.exists(args.metadata):
        print(f"[*] Reading Metadata from JSON file: {args.metadata}")
        try:
            with open(args.metadata, "r") as f:
                meta = json.load(f)
                video_file = video_file or meta.get("video_filename") or meta.get("video_url") or meta.get("video_path")
                title = title or meta.get("title")
                description = description or meta.get("description")
                tags = tags or meta.get("tags")
                privacy = privacy or meta.get("privacy_status", "public")
                thumbnail = thumbnail or meta.get("thumbnail_filename") or meta.get("thumbnail_path")
        except Exception as e:
            print(f"[-] Error reading {args.metadata}: {e}")

    # Check if video_file is a Google Drive URL/ID or Web URL and download directly in Cloud
    if video_file:
        video_file = download_video_if_url(video_file)

    # Fallback to searching input_videos/ directory if no video path specified
    if not video_file or not os.path.exists(video_file):
        input_dir = "input_videos"
        if os.path.exists(input_dir):
            for fname in os.listdir(input_dir):
                if fname.lower().endswith((".mp4", ".mkv", ".mov", ".avi")):
                    video_file = os.path.join(input_dir, fname)
                    print(f"[+] Found video file in input_videos/: {video_file}")
                    break

    if not video_file:
        print("[-] Error: No video file specified. Place a video in 'input_videos/' or pass '--video path/to/video.mp4'.")
        sys.exit(1)

    title = title or os.path.splitext(os.path.basename(video_file))[0].replace("_", " ").title()
    description = description or "Uploaded automatically via YouTube Manual Uploader Agent."

    agent.upload_video(
        video_path=video_file,
        title=title,
        description=description,
        tags=tags,
        privacy_status=privacy,
        thumbnail_path=thumbnail
    )

if __name__ == "__main__":
    main()
