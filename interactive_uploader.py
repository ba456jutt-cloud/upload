#!/usr/bin/env python3
"""
Interactive CLI YouTube Video Uploader Agent
============================================
Presents interactive prompts for Video File Path/URL, Title, Description, Tags, 
Privacy Status, and Thumbnail, then uploads directly to YouTube via API.
"""

import os
import sys
import json
import requests
import subprocess
from youtube_manual_uploader import YouTubeManualUploaderAgent

def download_video_from_url(url: str, output_dir: str = "downloads") -> str:
    """Downloads a video file from a URL using yt-dlp or requests."""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "downloaded_video.mp4")
    print(f"\n[*] Downloading video from URL: {url}...")
    
    # Try yt-dlp if available
    try:
        cmd = ["yt-dlp", "-o", output_path, "--force-overwrites", url]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and os.path.exists(output_path):
            print(f"[+] Video downloaded successfully via yt-dlp: {output_path}")
            return output_path
    except Exception:
        pass

    # Direct HTTP download fallback
    try:
        r = requests.get(url, stream=True, timeout=30)
        if r.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    f.write(chunk)
            print(f"[+] Video downloaded successfully via HTTP: {output_path}")
            return output_path
    except Exception as e:
        print(f"[-] Error downloading video URL: {e}")

    return ""

def run_interactive_uploader():
    print("======================================================")
    print("🎬 INTERACTIVE YOUTUBE VIDEO UPLOADER AGENT")
    print("======================================================")
    print("Answer the prompts below to upload your video directly to YouTube.\n")

    # 1. Video Path or URL
    while True:
        video_input = input("📹 1. Enter Video File Path or URL (e.g. input_videos/my_video.mp4):\n   > ").strip()
        if not video_input:
            print("   [-] Error: Video path or URL is required!\n")
            continue
            
        if video_input.startswith(("http://", "https://")):
            video_file = download_video_from_url(video_input)
            if video_file and os.path.exists(video_file):
                break
            else:
                print("   [-] Could not download video from provided URL. Try a local file path.\n")
                continue
        elif os.path.exists(video_input):
            video_file = video_input
            break
        else:
            print(f"   [-] File '{video_input}' not found. Check the path and try again.\n")

    # 2. Title
    default_title = os.path.splitext(os.path.basename(video_file))[0].replace("_", " ").title()
    title_input = input(f"\n📌 2. Enter Video Title (Press Enter for default: '{default_title}'):\n   > ").strip()
    title = title_input if title_input else default_title

    # 3. Description
    print("\n📝 3. Enter Video Description (Type your description, then press Enter):")
    desc_input = input("   > ").strip()
    description = desc_input if desc_input else f"Uploaded via Interactive YouTube Uploader Agent on {title}."

    # 4. Tags
    print("\n🏷️  4. Enter Tags (Comma-separated, e.g. Cybersecurity, AI, Python):")
    tags_input = input("   > ").strip()
    tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else ["Video", "Tutorial", "Automation"]

    # 5. Privacy Status
    print("\n🔒 5. Select Privacy Status:")
    print("   [1] Public (Default - visible to everyone)")
    print("   [2] Unlisted (only accessible via direct link)")
    print("   [3] Private (only visible to you)")
    privacy_choice = input("   Select option (1/2/3, default 1): ").strip()
    
    privacy_map = {"1": "public", "2": "unlisted", "3": "private"}
    privacy = privacy_map.get(privacy_choice, "public")

    # 6. Thumbnail (Optional)
    print("\n🖼️  6. Enter Custom Thumbnail Path (Optional - press Enter to skip):")
    thumb_input = input("   > ").strip()
    thumbnail = thumb_input if thumb_input and os.path.exists(thumb_input) else None

    # Summary & Confirmation
    file_size_mb = os.path.getsize(video_file) / (1024 * 1024)
    print("\n======================================================")
    print("📋 UPLOAD CONFIRMATION SUMMARY")
    print("======================================================")
    print(f"📌 Video File:   {video_file} ({file_size_mb:.2f} MB)")
    print(f"📌 Title:        {title}")
    print(f"📌 Description:  {description}")
    print(f"📌 Tags:        {', '.join(tags)}")
    print(f"📌 Privacy:      {privacy}")
    print(f"📌 Thumbnail:    {thumbnail if thumbnail else 'None'}")
    print("======================================================")

    confirm = input("🚀 Proceed with YouTube Upload? (Y/n): ").strip().lower()
    if confirm not in ("", "y", "yes"):
        print("[-] Upload canceled by user.")
        return

    # Execute Upload Agent
    print("\n[*] Initializing YouTube Upload Agent...")
    agent = YouTubeManualUploaderAgent()
    video_url = agent.upload_video(
        video_path=video_file,
        title=title,
        description=description,
        tags=tags,
        privacy_status=privacy,
        thumbnail_path=thumbnail
    )

    if video_url:
        print("\n🎉 ALL DONE! Your video is live on YouTube:")
        print(f"👉 {video_url}")

if __name__ == "__main__":
    try:
        run_interactive_uploader()
    except KeyboardInterrupt:
        print("\n[-] Operation canceled.")
