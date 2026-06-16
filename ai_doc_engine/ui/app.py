import streamlit as st
import os
import json

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

if menu_selection == "🔔 Pending Updates":
    st.subheader("Pending Documentation Updates")
    st.info("The dashboard will be implemented in Stage 2.")
    
elif menu_selection == "💬 Chat with Docs":
    st.subheader("Chat with your Codebase")
    st.info("Chat UI will be implemented in Issue 5.")
    
elif menu_selection == "⚙️ Settings":
    st.subheader("Repository Settings")
    st.info("Settings will be implemented in Stage 5.")
