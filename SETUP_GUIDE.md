# J.A.R.V.I.S - College Assistant Portal
## Complete Setup Guide for Any System

---

## 📋 Prerequisites

Before starting, ensure you have:
- **Python 3.9+** installed ([Download Python](https://www.python.org/downloads/))
- **Git** (optional, for cloning)
- **Internet connection** (for downloading packages)

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Open Terminal/Command Prompt

**Windows:** Press `Win + R`, type `cmd`, press Enter
**Mac/Linux:** Open Terminal application

### Step 2: Navigate to Project Folder

```bash
cd path/to/college_portal
```

### Step 3: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

> ⏳ **Note:** First installation may take 5-10 minutes as it downloads TensorFlow and models.

### Step 5: Configure Environment

Edit the `.env` file with your settings:

```
GEMINI_API_KEY=your-gemini-api-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

> 💡 Get free Gemini API key at: https://aistudio.google.com/app/apikey

### Step 6: Run the Application

```bash
python app.py
```

### Step 7: Open in Browser

Go to: **http://localhost:5000**

---

## 🔐 Default Login Credentials

| Type | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |

---

## 📁 Project Structure

```
college_portal/
├── app.py              # Main application
├── config.py           # Configuration
├── models.py           # Database models
├── requirements.txt    # Dependencies
├── .env                # Environment variables (edit this!)
├── reset_admin.py      # Reset admin password
├── add_sample_data.py  # Add demo students
│
├── routes/             # API Routes
│   ├── admin.py        # Admin panel
│   ├── student.py      # Student search
│   ├── ai_chat.py      # AI chat
│   └── jobs.py         # Job assistant
│
├── face/               # Face recognition
│   └── face_engine.py
│
├── rag/                # AI/RAG pipeline
│   ├── embedder.py
│   ├── retriever.py
│   └── gemini_client.py
│
├── templates/          # HTML templates
├── static/             # CSS, JS, uploads
└── data/               # Database files
```

---

## 🛠️ Troubleshooting

### Issue: "Module not found" error
```bash
pip install -r requirements.txt
```

### Issue: Admin login not working
```bash
python reset_admin.py
# Then restart the server
```

### Issue: Face recognition slow on first use
This is normal! DeepFace downloads models (~500MB) on first use. Be patient.

### Issue: Gemini API not working
1. Check your API key in `.env`
2. Get new key from: https://aistudio.google.com/app/apikey
3. Restart the server

### Issue: Port 5000 already in use
```bash
# Find and kill the process using port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F

# Or run on different port:
# Edit app.py line 86: port=5001
```

---

## 📱 Features Overview

### 1. Admin Panel (`/admin`)
- Add/Edit/Delete students
- Upload student photos
- View dashboard statistics

### 2. Face Recognition (`/explore`)
- Upload any photo
- AI identifies matching student
- Shows confidence score

### 3. AI Chat (`/chat`)
- Ask questions in natural language
- "Who has Python skills?"
- "Show CSE students"

### 4. Job Assistant (`/jobs`)
- Paste job descriptions
- AI matches students
- Generate resumes & cover letters

---

## 🔧 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| FLASK_SECRET_KEY | Session encryption key | Optional |
| GEMINI_API_KEY | Google Gemini API key | Yes (for AI features) |
| ADMIN_USERNAME | Admin login username | Optional (default: admin) |
| ADMIN_PASSWORD | Admin login password | Optional (default: admin123) |

---

## 💻 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 4 GB | 8 GB+ |
| Storage | 2 GB | 5 GB+ |
| Python | 3.9 | 3.10+ |
| OS | Windows 10/Ubuntu 20/macOS 11 | Latest versions |

---

## 🚀 Deployment (Production)

### Option 1: Local Network
```bash
python app.py
# Access from other devices: http://YOUR_IP:5000
```

### Option 2: Cloud (Render/Railway)
1. Push code to GitHub
2. Connect to Render/Railway
3. Set environment variables
4. Deploy!

---

## 📞 Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Restart the server
3. Delete `college_portal.db` and restart (creates fresh database)

---

## ✨ Quick Commands Reference

```bash
# Start server
python app.py

# Reset admin password
python reset_admin.py

# Add sample students
python add_sample_data.py

# Install dependencies
pip install -r requirements.txt
```

---

**Made with ❤️ for Final Year Project**
