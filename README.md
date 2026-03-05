# Smart College Student Assistance Portal

> **Final Year Engineering Project** - AI-Powered College Portal with Face Recognition, RAG-based Chat, and Job Assistance

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0+-green)
![AI](https://img.shields.io/badge/AI-Gemini-orange)

## 🌟 Features

### 👤 Admin Panel
- Complete student CRUD operations
- Photo upload with automatic face embedding extraction
- Academic details, skills, projects, and internships management
- Dashboard with statistics

### 🔍 Face Recognition Search
- Upload any student photo
- AI identifies the matching student
- Shows complete profile with confidence score

### 🧠 RAG-AI Chat
- Natural language queries about students
- "Who has Python skills?"
- "Find students for AI internship"
- Powered by Gemini + Sentence Transformers + FAISS

### 💼 Job Application Assistant
- Analyze job descriptions
- Match students to job requirements
- Generate resume bullet points
- Create cover letters

### 📄 PDF Reports
- Professional student profile PDFs
- Download with all details

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9 or higher
- pip package manager

### 2. Installation

```bash
# Navigate to project folder
cd college_portal

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file from the example:
```bash
copy .env.example .env
```

Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your-api-key-here
```

Get a free Gemini API key at: https://aistudio.google.com/app/apikey

### 4. Run the Application

```bash
python app.py
```

Open your browser to: **http://localhost:5000**

### 5. Default Admin Login
- **Username:** admin
- **Password:** admin123

## 📁 Project Structure

```
college_portal/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── models.py           # Database models
├── requirements.txt    # Dependencies
├── .env.example        # Environment template
│
├── routes/             # Route blueprints
│   ├── admin.py        # Admin CRUD
│   ├── student.py      # Student search & profiles
│   ├── ai_chat.py      # RAG chat
│   └── jobs.py         # Job assistant
│
├── face/               # Face recognition
│   └── face_engine.py
│
├── rag/                # RAG pipeline
│   ├── embedder.py     # Text embeddings
│   ├── retriever.py    # FAISS search
│   └── gemini_client.py
│
├── utils/
│   └── pdf_generator.py
│
├── templates/          # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── chat.html
│   ├── admin/
│   ├── explore/
│   ├── jobs/
│   └── errors/
│
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── uploads/
│
└── data/               # FAISS indices
```

## 💻 Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Flask 3.0, SQLAlchemy |
| Database | SQLite |
| Face Recognition | face-recognition, dlib |
| Embeddings | sentence-transformers |
| Vector Search | FAISS |
| LLM | Google Gemini |
| PDF | ReportLab |
| Frontend | HTML, CSS, JavaScript, Jinja2 |

## 📝 Usage Guide

### Adding Students
1. Login to Admin Panel (`/admin/login`)
2. Click "Add Student"
3. Fill details and upload photo
4. Face embedding is auto-extracted

### Face Search
1. Go to "Explore" page
2. Upload a student's photo
3. View matched profile

### AI Chat Examples
- "Show all CSE students"
- "Who has Python and ML skills?"
- "Students suitable for web development"
- "List internship experiences"

### Job Assistant
1. Paste job description
2. Click "Analyze"
3. View matched students
4. Generate resumes/cover letters

## ⚠️ Notes

### Face Recognition on Windows
`dlib` (required by face-recognition) needs Visual Studio C++ Build Tools:
1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install "Desktop development with C++"
3. Then run: `pip install face-recognition`

### Without Gemini API Key
The app works without Gemini but AI features will use fallback responses.

## 📄 License

This project is for educational purposes (Final Year Project).

## 🙏 Credits

- Flask Framework
- Google Gemini API
- Face Recognition by ageitgey
- Sentence Transformers by HuggingFace
- FAISS by Meta/Facebook
