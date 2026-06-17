import streamlit as st
import os
import json
from engine.rag_store import DocVectorStore
from engine.doc_generator import DocGenerator
from engine.github_service import GitHubService
from engine.llm_service import LLMService

UPDATES_FILE = "/app/chroma_db/pending_updates.json"

def load_pending_updates():
    if os.path.exists(UPDATES_FILE):
        with open(UPDATES_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def remove_pending_update(index):
    updates = load_pending_updates()
    if 0 <= index < len(updates):
        updates.pop(index)
        with open(UPDATES_FILE, "w") as f:
            json.dump(updates, f)

def approve_update(index, doc_id, text, metadata):
    db = DocVectorStore()
    db.upsert_doc(doc_id=doc_id, text=text, metadata=metadata)
    remove_pending_update(index)

# Stage 1: Base Layout & Premium Styling
st.set_page_config(
    page_title="AI Doc Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Premium Dark Mode CSS & Modern Typography
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Vibrant Gradient Header */
    .premium-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Subtle subtitle */
    .premium-subtitle {
        color: #A0AEC0;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Hide Default Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="premium-header">AI Document Engine</h1>', unsafe_allow_html=True)
st.markdown('<p class="premium-subtitle">Your self-updating codebase knowledge graph.</p>', unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("Navigation")
menu_selection = st.sidebar.radio(
    "",
    ["🔔 Pending Updates", "💬 Chat with Docs", "⚙️ Settings"]
)

UPDATES_FILE = "/app/chroma_db/pending_updates.json"

def load_pending_updates():
    if os.path.exists(UPDATES_FILE):
        with open(UPDATES_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

if menu_selection == "🔔 Pending Updates":
    st.subheader("Pending Documentation Updates")
    
    updates = load_pending_updates()
    
    if not updates:
        st.success("🎉 All caught up! No pending documentation updates.")
    else:
        st.warning(f"⚠️ You have {len(updates)} code units requiring documentation review.")
        
        for i, update in enumerate(updates):
            with st.expander(f"📄 {update.get('filename')} ➡️ {update.get('unit_name')} [{update.get('severity')}]"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<h3 style="color:#ff4b4b;">🛑 Old Documentation</h3>', unsafe_allow_html=True)
                    old_doc = update.get('old_doc')
                    if old_doc:
                        st.info(old_doc)
                    else:
                        st.warning("No previous documentation existed for this unit.")
                        
                with col2:
                    st.markdown('<h3 style="color:#09ab3b;">✅ AI Drafted Documentation</h3>', unsafe_allow_html=True)
                    new_doc = update.get('new_doc_draft')
                    if new_doc:
                        st.success(new_doc)
                    else:
                        st.error("No draft generated.")
                        
                st.write("---")
                
                col_btn1, col_btn2 = st.columns([1, 1])
                
                doc_id = f"{update.get('filename')}::{update.get('unit_name')}"
                metadata = {
                    "unit_type": "function", # Default
                    "name": update.get('unit_name'),
                    "file_path": update.get('filename')
                }
                
                with col_btn1:
                    if st.button("✅ Approve Draft", key=f"approve_{i}"):
                        approve_update(i, doc_id, new_doc, metadata)
                        st.success("Draft approved and saved to database!")
                        st.rerun()
                        
                with col_btn2:
                    if st.button("❌ Reject", key=f"reject_{i}"):
                        remove_pending_update(i)
                        st.warning("Draft rejected.")
                        st.rerun()
    
elif menu_selection == "💬 Chat with Docs":
    st.subheader("Chat with your Codebase")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am your AI Document Engine. Ask me anything about your codebase!"}
        ]
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    prompt = st.chat_input("Ask a question about your code...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.spinner("Searching knowledge base..."):
            db_store = DocVectorStore()
            docs, metadatas = db_store.search_with_citations(prompt)
            context = "\n\n".join(docs) if docs else "No relevant documentation found."
            
        with st.spinner("Generating answer..."):
            llm_service = LLMService()
            response = llm_service.chat_with_context(prompt, context)
            
        with st.chat_message("assistant"):
            st.markdown(response)
            st.info("Citations will be implemented in Stage 7.")
            
        st.session_state.messages.append({"role": "assistant", "content": response})
    
elif menu_selection == "⚙️ Settings":
    st.subheader("Repository Settings")
    st.markdown("Use this panel to manage your Documentation Engine's global state.")
    
    st.write("---")
    st.markdown("### 🔄 Full Manual Ingestion")
    st.warning("Running a full ingestion will scan your entire repository and overwrite existing documentation.")
    
    if st.button("🚀 Run Full Repository Ingestion"):
        with st.spinner("Fetching files, parsing code, and generating documentation. This may take several minutes..."):
            try:
                git_service = GitHubService()
                llm_service = LLMService()
                db_store = DocVectorStore()
                
                generator = DocGenerator(llm_service, db_store)
                generator.generate_for_repo(git_service)
                
                st.success("✅ Full repository successfully ingested and documented!")
            except Exception as e:
                st.error(f"❌ An error occurred during ingestion: {str(e)}")
