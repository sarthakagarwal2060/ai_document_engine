# AI Document Engine

This is a full-stack AI documentation engine that automatically monitors GitHub for code changes and generates documentation using Groq and ChromaDB.

## Architecture
- **Frontend:** Streamlit (Port 8501)
- **Backend:** FastAPI (Port 8000)
- **Database:** Local SQLite (ChromaDB)
- **Deployment:** Docker (Single Container via Nginx)

---

## 🚀 How to Deploy on Render

This project is optimized to be deployed as a single "Web Service" on [Render.com](https://render.com). 

### Step 1: Create the Web Service
1. Go to your Render Dashboard and click **New > Web Service**.
2. Connect your GitHub account and select the `ai_document_engine` repository.
3. Under **Language/Environment**, select **Docker**.

### Step 2: Configure the Build
Scroll down to the Advanced Settings and ensure the following are set:
- **Dockerfile Path:** `ai_doc_engine/Dockerfile.render`
- **Docker Command:** *(Leave blank)*

### Step 3: Add Persistent Storage (Crucial!)
To prevent your documentation from being deleted when the server restarts, you must attach a Render Disk.
1. Scroll down to **Advanced > Disks**.
2. Click **Add Disk**.
3. **Name:** `chroma-storage`
4. **Mount Path:** `/app/chroma_db`
5. **Size:** 1 GB

### Step 4: Add Environment Variables
Scroll down to **Environment Variables** and add the following keys:
- `GITHUB_TOKEN`: Your GitHub Personal Access Token.
- `TARGET_REPO`: The repository to monitor (e.g., `sarthakagarwal2060/ai_document_engine`).
- `GROQ_API_KEY`: Your Groq LLM API Key.

### Step 5: Deploy & Connect GitHub Webhooks
1. Click **Create Web Service** at the bottom of the page.
2. Wait a few minutes for Docker to build and start the server.
3. Once live, Render will give you a public URL (e.g., `https://ai-doc-engine-xyz.onrender.com`).
4. **Go to GitHub Settings > Webhooks**.
5. Add a new webhook. In the Payload URL, enter: `https://ai-doc-engine-xyz.onrender.com/webhook/github`
6. Set the Content Type to `application/json`.

You are done! You can visit your Render URL in the browser to view the Streamlit UI, and GitHub will automatically send updates to that exact same URL in the background!
