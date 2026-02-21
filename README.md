# Insight Nexus — Setup Guide for Termux

## One-Time Setup

```bash
# 1. Install Python & pip
pkg update && pkg install python

# 2. Navigate into the project folder
cd insight-nexus

# 3. Install Flask
pip install flask werkzeug

# 4. Create the uploads folder
mkdir -p static/uploads
```

## Run the Server

```bash
# Inside the insight-nexus folder:
python app.py
```

Then open your phone browser and go to:
**http://localhost:5000**

To access from another device on the same Wi-Fi:
Find your phone's local IP with `ifconfig` and open:
**http://YOUR_PHONE_IP:5000**

---

## Admin Access

- Go to **http://localhost:5000/signin**
- Enter your password: `admin123`  ← change this in app.py (line 11)
- You'll see the Admin Dashboard
- Click **New Post** to write and publish a blog

---

## Changing Your Password

Open `app.py` and find line 11:
```python
ADMIN_PASSWORD = 'admin123'   # ← change this
```
Restart the server after saving.

---

## Project Structure

```
insight-nexus/
├── app.py               ← Main Flask server
├── blog.db              ← SQLite database (auto-created)
├── requirements.txt
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── uploads/         ← Uploaded images stored here
└── templates/
    ├── base.html
    ├── home.html
    ├── blog.html
    ├── post.html
    ├── about.html
    ├── contact.html
    ├── signin.html
    ├── admin.html
    └── new_post.html
```

---

## Adding a Blog Post

1. Sign in at `/signin`
2. Click **New Post**
3. Fill in: Title, Category, Excerpt, Content
4. Add a cover image (upload from phone OR paste a URL)
5. Click **Publish Post** — done!

Your post immediately appears on the Home and Blog pages.

---

## Keep Server Running (Optional)

Install `tmux` to keep the server alive after closing Termux:
```bash
pkg install tmux
tmux new -s blog
python app.py
# Press Ctrl+B, then D to detach (server keeps running)
# Reattach with: tmux attach -t blog
```
