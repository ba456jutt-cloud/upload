# 🎥 Dedicated YouTube Manual Video & Description API Uploader Agent

This dedicated project folder contains a standalone, specialized agent for uploading custom user-provided videos, custom titles, custom descriptions, custom tags, and custom thumbnails directly to YouTube via **YouTube Data API v3** and **GitHub Actions**.

---

## 📂 Project Architecture

```
youtube_manual_uploader/
├── .github/workflows/
│   └── youtube_manual_upload.yml   # GitHub Actions Automation Workflow
├── input_videos/
│   └── .gitkeep                    # Put your video files here (e.g. input_videos/my_video.mp4)
├── metadata/
│   └── video_info.json             # JSON file to set Title, Description, Tags, Privacy, Thumbnail
├── youtube_manual_uploader.py      # Standalone YouTube API Upload Agent
├── generate_token.py               # 1-Time OAuth Refresh Token Generator
├── upload_history.json             # Upload Log History
└── README.md                       # Documentation
```

---

## 🚀 How to Use (2 Flexible Ways)

### Method 1: Local Terminal Execution
1. Place your video inside `input_videos/my_video.mp4`.
2. Edit `metadata/video_info.json` with your desired **Title**, **Description**, and **Tags**.
3. Run the script:
   ```bash
   python3 youtube_manual_uploader.py
   ```
   *Or via command line arguments:*
   ```bash
   python3 youtube_manual_uploader.py --video input_videos/my_video.mp4 --title "My Great Video" --description "Full video description" --privacy public
   ```

---

### Method 2: GitHub Actions Automated Cloud Execution
1. Push this folder to your GitHub repository.
2. In GitHub Repository **Settings > Secrets and variables > Actions**, add your 2 secrets:
   - `YOUTUBE_REFRESH_TOKEN`
   - `YOUTUBE_CLIENT_SECRET_JSON`
3. Put your video in `input_videos/` and push to GitHub.
4. Go to **Actions** tab in GitHub, select **Manual Video & Metadata YouTube API Uploader**, click **Run workflow**, type your Title & Description, and hit **Run**!

The agent will execute in the cloud, upload your video, set the description & thumbnail, and output the published link (`https://youtu.be/...`).
