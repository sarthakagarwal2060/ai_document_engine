# 🧠 AI Documentation Engine

An intelligent, decoupled full-stack application that automatically ingests your codebase, generates comprehensive documentation using Large Language Models (LLMs), and keeps it perfectly up-to-date by listening to GitHub webhooks.

## 🌟 Key Features

* **🤖 AI-Powered RAG Chatbot:** Ask questions about your codebase and get highly accurate, citation-backed answers.
* **⚡ Decoupled Architecture:** A lightweight React frontend powered by a lightning-fast FastAPI Python backend.
* **🔄 Automated Webhooks:** Listen to GitHub pushes in real-time. The AI automatically analyzes diffs, detects what functions changed, and drafts updated documentation for review.
* **🔍 Semantic Search:** Uses Pinecone Serverless Vector Database and `sentence-transformers` for instant, context-aware code retrieval.
* **✅ Human-in-the-Loop Review:** Pending documentation updates are queued in the UI for developers to approve or reject before they are permanently embedded into the vector store.

---

## 🏗️ Architecture

This project has been heavily optimized for cloud deployment (Render + Vercel) and is split into two distinct services:

### 1. Backend (`/ai_doc_engine`)
* **Framework:** FastAPI (Python)
* **LLM Provider:** Groq (Llama 3)
* **Vector Database:** Pinecone
* **Key Tasks:** Code AST parsing, LLM inference, embedding generation, and handling background GitHub webhook tasks.

### 2. Frontend (`/frontend`)
* **Framework:** React + Vite
* **Styling:** Vanilla CSS (Glassmorphism + Dark Mode aesthetic)
* **Key Tasks:** Real-time polling for ingestion status, rendering markdown chat responses, and managing the Pending Updates review queue.

---

## 🚀 Local Development Setup

### Prerequisites
* Python 3.10+
* Node.js v18+
* API Keys for: **Groq**, **Pinecone**, and a **GitHub Personal Access Token**.

### Backend Setup
```bash
# Navigate to the backend directory
cd ai_doc_engine

# Create a virtual environment and activate it
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (Downloads CPU-only PyTorch for speed)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# Create your environment variables file
cp .env.example .env
# Edit .env with your real API keys

# Start the FastAPI server
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup
```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Create environment variable file
echo "VITE_API_URL=http://127.0.0.1:8000/api" > .env

# Start the Vite dev server
npm run dev
```

---

## ☁️ Deployment Guide

### Backend (Render)
1. Connect your repository to **Render** and create a new **Web Service**.
2. Set the Root Directory to `ai_doc_engine`.
3. Set the Start Command to: `uvicorn api.main:app --host 0.0.0.0 --port 8000`
4. In the Environment section, add your `GROQ_API_KEY`, `PINECONE_API_KEY`, `GITHUB_TOKEN`, etc.
5. Deploy! (The custom `Dockerfile` ensures it builds quickly without bloated NVIDIA drivers).

### Frontend (Vercel)
1. Connect your repository to **Vercel**.
2. Set the Root Directory to `frontend`.
3. Go to Environment Variables and add `VITE_API_URL` pointing to your live Render backend URL (e.g., `https://your-backend.onrender.com/api`).
4. Deploy!

### GitHub Webhooks
To enable automatic documentation drafting on every push:
1. Go to your target GitHub repository > **Settings** > **Webhooks**.
2. Add Webhook:
   * **Payload URL:** `https://your-backend.onrender.com/webhook/github`
   * **Content type:** `application/json`
   * **Events:** `Just the push event`

---

## 🔑 Environment Variables Reference

**Backend (`ai_doc_engine/.env`)**
```env
GITHUB_TOKEN=your_github_token
TARGET_REPO=username/repository_name
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=aidocengine
```

**Frontend (`frontend/.env`)**
```env
VITE_API_URL=https://ai-document-engine.vercel.app/
```
