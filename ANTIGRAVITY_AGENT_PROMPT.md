# 🤖 Antigravity Agent Master Setup Prompt

> Copy and paste the prompt below directly to your **Antigravity AI Agent** on your Windows/Linux laptop after unzipping the project folder!

---

### 📋 COPY-PASTE PROMPT FOR ANTIGRAVITY AGENT:

```text
Please complete the 1-click error-free setup and launch for this YouTube Auto-Uploader project:

1. Install all dependencies from `requirements.txt` using `--break-system-packages` if needed.
2. Ensure Git LFS is installed and initialized (`git lfs install`).
3. Set Git HTTP postBuffer to 1GB (`git config http.postBuffer 1048576000`, `git config http.maxRequestBuffer 1048576000`, `git config core.compression 0`) to prevent RPC/curl 55 Send failure on large 1.2GB video uploads.
4. Verify and auto-restore `.github/workflows/youtube_manual_upload.yml` if hidden or missing.
5. Check `.env` file for GITHUB_TOKEN and YouTube OAuth credentials.
6. Execute `python start.py` to automatically configure system environment and open the Web App UI at http://localhost:5001.
```

---

## 🛠️ What `start.py` Does Automatically (Zero Commands Required!):

When you run `python start.py` (or double-click `run.bat` on Windows):

1. **Auto UTF-8 Encoding:** Automatically fixes Windows PowerShell encoding issues (`$env:PYTHONIOENCODING="utf-8"`).
2. **Auto Git LFS & 1GB Buffer Config:** Automatically executes `git lfs install` and sets `http.postBuffer=1048576000` so 1.2GB video pushes **never fail with `curl 55 Send failure`**.
3. **Auto-Restore Hidden Files:** Automatically creates `.github/workflows/youtube_manual_upload.yml` if Windows hidden file extraction skipped it.
4. **Auto-Launch Web UI:** Automatically opens `http://localhost:5001` in your default browser!
