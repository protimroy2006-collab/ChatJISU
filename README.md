# CHATJIS - JIS University ChatBot

A modern Flask-based chatbot assistant for JIS University with an upgraded UI.

## Quick Deploy to Render.com (Free)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/CHATJIS.git
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click **New +** → **Web Service**
4. Connect your CHATJIS repository
5. Fill in:
   - **Name:** chatjis
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
6. Click **Deploy**

Your app will be live in ~2 minutes at: `https://chatjis-xxx.onrender.com`

## Features
- Modern, gradient-based UI
- Real-time chat responses
- JIS University knowledge base
- Responsive design
- Production-ready

## Local Development
```bash
pip install -r requirements.txt
python app.py
```
Visit `http://localhost:5000`

## Tech Stack
- Backend: Flask (Python)
- Frontend: HTML5, CSS3, Vanilla JavaScript
- Styling: Modern gradients & animations

---
**Ready to deploy?** Follow the steps above!
