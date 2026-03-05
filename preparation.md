# J.A.R.V.I.S Technical Viva Preparation Guide
## Comprehensive Analysis of System Architecture & Dependencies

This document provides a detailed breakdown of the technical stack used in J.A.R.V.I.S, designed to assist in explaining technical choices during project evaluation or invigilator questioning.

---

### 1. Web Framework & Core Infrastructure

#### **flask (>=3.0.0)**
- **Purpose**: The "Skeleton" of the application. It handles routing (URL mapping), request handling, and template rendering.
- **Why chosen?**: Flask is a micro-framework. Unlike Django, it is lightweight and gives the developer full control over the components. It's perfect for AI-driven projects where we need to integrate custom Python logic easily.
- **Why not others (like Django)?**: Django is "batteries-included" and can be bloated for a specialized AI assistant. Flask's flexibility allowed us to integrate DeepFace and Groq without the framework getting in the way.

#### **flask-sqlalchemy (>=3.1.0)**
- **Purpose**: Object-Relational Mapper (ORM). It allows us to interact with the database using Python classes instead of writing raw SQL queries.
- **Why chosen?**: It provides a high level of abstraction. If we want to switch from SQLite to PostgreSQL in the future, we only change a configuration line, not the code.
- **Why not others (like raw SQL)?**: raw SQL is prone to "SQL Injection" attacks. SQLAlchemy automatically sanitizes inputs, making the system secure by default.

#### **flask-login (>=0.6.0)**
- **Purpose**: User session management. It handles logging in, logging out, and remembering user sessions.
- **Why chosen?**: It is the industry standard for Flask. It handles the "is_authenticated" checks seamlessly and integrates perfectly with our User model.
- **Why not others (like Custom JWT)?**: Building session management from scratch is risky from a security standpoint. Flask-Login is battle-tested.

#### **werkzeug (>=3.0.0)**
- **Purpose**: A comprehensive WSGI utility library. We use it primarily for `generate_password_hash` and `check_password_hash`.
- **Why chosen?**: J.A.R.V.I.S never stores plain-text passwords. Werkzeug provides the "PBKDF2" hashing algorithm, which is highly secure against brute-force attacks.

#### **python-dotenv (>=1.0.0)**
- **Purpose**: Security. It loads sensitive keys (like the Groq API Key) from a `.env` file instead of hardcoding them in the script.
- **Why chosen?**: It prevents accidental exposure of API keys if the code is uploaded to GitHub. It's a standard DevOps best practice.

---

### 2. Computer Vision & Biometrics

#### **deepface (>=0.0.79)**
- **Purpose**: The "Eyes" of J.A.R.V.I.S. It handles face detection, verification, and analysis.
- **Why chosen?**: It is a "wrapper" that can use multiple models like VGG-Face, FaceNet, or OpenFace. It is much easier to set up than the traditional `dlib`-based `face_recognition` library, which often has complex C++ dependencies.
- **Why not others (like face_recognition)?**: `face_recognition` requires `cmake` and `dlib`, which can be a nightmare to install on different OS. DeepFace is pure-Python friendly.

#### **opencv-python (>=4.8.0)**
- **Purpose**: Image processing. It handles the camera feed, image resizing, and color conversions (BGR to RGB).
- **Why chosen?**: It is the world's leading computer vision library. Fast, efficient, and supports almost every image format.

#### **tf-keras (>=2.15.0)**
- **Purpose**: The backend engine for DeepFace. DeepFace uses Deep Learning models that require a TensorFlow/Keras environment to run predictions.

#### **numpy (>=1.24.0)**
- **Purpose**: Mathematical processing. Images are essentially large 3D arrays of numbers. Numpy allows J.A.R.V.I.S to perform high-speed calculations on these "image arrays."

---

### 3. RAG Pipeline & AI Logic (Retrieval-Augmented Generation)

#### **sentence-transformers (>=2.2.0)**
- **Purpose**: The "Neural Semantic Engine." It converts text (like student profiles) into mathematical vectors (embeddings) that represent the *meaning* of the text.
- **Why chosen?**: It uses BERT-based models that understand context. For example, it knows that "Machine Learning" and "Data Science" are related.
- **Why not others?**: Traditional keyword search (like CTRL+F) would fail if you search for "AI" but the document says "Artificial Intelligence." Sentence-transformers solve this.

#### **faiss-cpu (>=1.7.0)**
- **Purpose**: The "Vector Database." It stores the numeric embeddings from the RAG pipeline and allows for lightning-fast similarity searches.
- **Why chosen?**: Created by Facebook Research, it is the fastest library for searching billions of vectors. It allows J.A.R.V.I.S to find relevant student data in milliseconds.

#### **groq (>=0.4.0)**
- **Purpose**: The "Brain" of J.A.R.V.I.S. It connects to Groq's LPU (Language Processing Unit) for ultra-fast AI responses.
- **Why chosen?**: Speed. Groq can generate text at 300-500 tokens per second, making J.A.R.V.I.S feel "instant" compared to OpenAI's GPT-4 or Gemini.

---

### 4. Generation & Assets

#### **reportlab (>=4.0.0)**
- **Purpose**: Document synthesis. Specifically, it allows the Job Intelligence Hub to generate professional PDF resumes and cover letters on the fly.
- **Why chosen?**: It allows for precise layout control (X, Y coordinates) on the PDF page, producing high-quality enterprise documents.

#### **pillow (>=10.0.0)**
- **Purpose**: Image handling. It assists ReportLab and OpenCV in processing student photos for profile rendering and PDF generation.
---
### Summary Checklist for Invigilators:
1. **Frontend**: HTML5, CSS3, JS (Vanilla for performance).
2. **Backend**: Flask (Micro-service architecture).
3. **Database**: SQLite (Development) / SQLAlchemy (ORM).
4. **AI/LLM**: Groq (LPU Inference).
5. **RAG**: FAISS + Sentence-Transformers (Contextual Retrieval).
6. **Biometrics**: DeepFace (Neural Face Synthesis).
