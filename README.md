# 🚀 YouTube Auto-Uploader HTML/CSS Web Assistant

A modern, glassmorphism dark-theme web application for uploading videos to YouTube via **YouTube Data API v3** and **GitHub Actions**.

---

## 📂 Project Architecture

```
youtube_manual_uploader/
├── .env                            # Saved OAuth & GitHub Credentials
├── auto_push_web_app.py            # Main Web App Server (runs on http://localhost:5001)
├── youtube_manual_uploader.py      # YouTube API Upload Engine
├── generate_token.py               # OAuth Token Generator
├── templates/
│   ├── auto_push.html              # HTML/CSS Dark Theme Interface
│   └── index.html                  # Backup HTML Template
├── input_videos/                   # Folder for video files (.mp4, .mkv)
├── thumbnails/                     # Folder for thumbnail image files (.png, .jpg)
├── metadata/                       # Auto-generated JSON metadata
├── .gitattributes                  # Git LFS 2GB video file tracking
├── .gitignore                      # Git security rules
├── requirements.txt                # Required Python packages
└── README.md                       # Setup Documentation
```

---

## ⚡ Quick 3-Step Setup on Any Laptop

### Step 1: Install Dependencies
Open terminal inside the extracted project folder and run:
```bash
pip install -r requirements.txt
```

### Step 2: Configure GitHub Credentials in `.env`
Edit `.env` and add your **GitHub Personal Access Token**:
```env
GITHUB_USERNAME=ba456jutt-cloud
GITHUB_TOKEN=YOUR_GITHUB_PERSONAL_ACCESS_TOKEN
GITHUB_REPO=upload
```

### Step 3: Run Web App!
```bash
python3 auto_push_web_app.py
```

Your browser will automatically open **`http://localhost:5001`**. Select your video & thumbnail, add Title/Description, click **AUTO-PUSH**, and let Cloud Actions publish your video to YouTube! 🚀
