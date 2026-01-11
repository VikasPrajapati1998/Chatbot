import streamlit as st
from backend import run_chat_stream, MODELS, get_model_emoji
from database import (
    save_chat_metadata, save_chat_message, get_all_chats,
    get_chat_messages, get_chat_metadata, delete_chat, clear_all_chats,
    generate_chat_title, format_timestamp, get_database_stats, rename_chat
)
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import uuid
import os
from pypdf import PdfReader
from docx import Document

st.set_page_config(
    page_title="Universal Chatbot", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🤖"
)

st.markdown("""
<style>
    .chat-item {padding: 10px; border-radius: 5px; margin: 5px 0;}
    .chat-item:hover {background-color: #f0f2f6;}
    .stButton button {transition: all 0.3s;}
    .metric-card {background-color: #f0f2f6; padding: 10px; border-radius: 8px; margin: 5px 0;}
</style>
""", unsafe_allow_html=True)

# SESSION STATE
if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())
if "history" not in st.session_state:
    st.session_state.history = []
if "file_context" not in st.session_state:
    st.session_state.file_context = ""
if "file_name" not in st.session_state:
    st.session_state.file_name = None
if "file_injected" not in st.session_state:
    st.session_state.file_injected = False
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "qwen2.5:0.5b"
if "chat_title" not in st.session_state:
    st.session_state.chat_title = "New Chat"
if "confirm_clear" not in st.session_state:
    st.session_state.confirm_clear = False
if "show_stats" not in st.session_state:
    st.session_state.show_stats = False
if "rename_mode" not in st.session_state:
    st.session_state.rename_mode = False
if "temp_title" not in st.session_state:
    st.session_state.temp_title = ""

def extract_file_content(uploaded_file):
    filename = uploaded_file.name
    ext = os.path.splitext(filename)[1].lower()
    try:
        if ext in [".txt", ".py", ".js", ".html", ".css", ".c", ".cpp", ".java", ".json", ".md"]:
            return uploaded_file.read().decode("utf-8")
        if ext == ".pdf":
            reader = PdfReader(uploaded_file)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        if ext == ".docx":
            doc = Document(uploaded_file)
            return "\n".join(p.text for p in doc.paragraphs)
        return f"Uploaded file: {filename}\nFile type: {ext}\nSize: {uploaded_file.size} bytes\nThis is a binary or unsupported format."
    except Exception as e:
        return f"Error reading file {filename}: {str(e)}"

def load_chat_history(chat_id: str):
    messages = get_chat_messages(chat_id)
    metadata = get_chat_metadata(chat_id)
    if messages:
        st.session_state.history = [{"role": msg["role"], "content": msg["content"], "search_used": msg.get("search_used", False)} for msg in messages]
    else:
        st.session_state.history = []
    if metadata:
        st.session_state.chat_title = metadata["title"]
        st.session_state.selected_model = metadata["model"]
        st.session_state.file_name = metadata["file_name"]

# SIDEBAR
with st.sidebar:
    st.title("💬 Chat Manager")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ New", use_container_width=True, type="primary"):
            st.session_state.chat_id = str(uuid.uuid4())
            st.session_state.history = []
            st.session_state.file_context = ""
            st.session_state.file_name = None
            st.session_state.file_injected = False
            st.session_state.chat_title = "New Chat"
            st.session_state.confirm_clear = False
            st.session_state.rename_mode = False
            st.rerun()
    with col2:
        if st.button("📊 Stats", use_container_width=True):
            st.session_state.show_stats = not st.session_state.show_stats
    
    if st.session_state.show_stats:
        stats = get_database_stats()
        st.markdown("### 📈 Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Chats", stats["total_chats"])
            st.metric("Messages", stats["total_messages"])
        with col2:
            st.metric("Searches", stats["total_searches"])
            st.metric("Characters", f"{stats['total_chars']:,}")
        st.divider()
    
    if st.button("🗑️ Clear All", use_container_width=True, type="secondary"):
        if st.session_state.confirm_clear:
            clear_all_chats()
            st.session_state.chat_id = str(uuid.uuid4())
            st.session_state.history = []
            st.session_state.file_context = ""
            st.session_state.file_name = None
            st.session_state.file_injected = False
            st.session_state.chat_title = "New Chat"
            st.session_state.confirm_clear = False
            st.session_state.rename_mode = False
            st.success("✅ All history cleared!")
            st.rerun()
        else:
            st.session_state.confirm_clear = True
            st.rerun()
    
    if st.session_state.confirm_clear:
        st.warning("⚠️ Click 'Clear All' again to confirm")
        if st.button("Cancel", use_container_width=True):
            st.session_state.confirm_clear = False
            st.rerun()
    
    st.divider()
    search_query = st.text_input("🔍 Search chats", placeholder="Type to search...")
    st.divider()
    
    all_chats = get_all_chats()
    if all_chats:
        if search_query:
            all_chats = [chat for chat in all_chats if search_query.lower() in chat['title'].lower()]
        st.markdown(f"### 📚 Chats ({len(all_chats)})")
        for chat in all_chats:
            is_current = chat['chat_id'] == st.session_state.chat_id
            with st.container():
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    model_emoji = get_model_emoji(chat['model'])
                    file_indicator = " 📎" if chat['file_name'] else ""
                    button_label = f"{model_emoji} {chat['title']}{file_indicator}"
                    if st.button(button_label, key=f"load_{chat['chat_id']}", use_container_width=True, type="primary" if is_current else "secondary"):
                        st.session_state.chat_id = chat['chat_id']
                        load_chat_history(chat['chat_id'])
                        st.session_state.file_context = ""
                        st.session_state.file_injected = False
                        st.session_state.confirm_clear = False
                        st.session_state.rename_mode = False
                        st.rerun()
                    st.caption(f"💬 {chat['message_count']} msgs | 🕐 {format_timestamp(chat['last_updated'])}")
                with col2:
                    if st.button("✏️", key=f"rename_{chat['chat_id']}", help="Rename"):
                        st.session_state.chat_id = chat['chat_id']
                        load_chat_history(chat['chat_id'])
                        st.session_state.rename_mode = True
                        st.session_state.temp_title = chat['title']
                        st.rerun()
                with col3:
                    if st.button("🗑️", key=f"del_{chat['chat_id']}", help="Delete"):
                        delete_chat(chat['chat_id'])
                        if chat['chat_id'] == st.session_state.chat_id:
                            st.session_state.chat_id = str(uuid.uuid4())
                            st.session_state.history = []
                            st.session_state.chat_title = "New Chat"
                            st.session_state.file_name = None
                            st.session_state.rename_mode = False
                        st.rerun()
                st.divider()
    else:
        st.info("💡 No chats yet. Start a conversation!")

# HEADER
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.title("🤖 Universal File Chatbot")
    
    # Rename mode
    if st.session_state.rename_mode:
        st.markdown("### ✏️ Rename Chat")
        col_input, col_save, col_cancel = st.columns([3, 1, 1])
        with col_input:
            new_title = st.text_input(
                "New chat name",
                value=st.session_state.temp_title,
                key="rename_input",
                placeholder="Enter new chat name..."
            )
        with col_save:
            if st.button("💾 Save", use_container_width=True, type="primary"):
                if new_title and new_title.strip():
                    rename_chat(st.session_state.chat_id, new_title.strip())
                    st.session_state.chat_title = new_title.strip()
                    st.session_state.rename_mode = False
                    st.success("✅ Chat renamed!")
                    st.rerun()
                else:
                    st.warning("⚠️ Please enter a valid name")
        with col_cancel:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.rename_mode = False
                st.rerun()
    else:
        st.caption(f"📝 {st.session_state.chat_title}")

with col2:
    model_emoji = get_model_emoji(st.session_state.selected_model)
    st.metric("Model", f"{model_emoji}")
with col3:
    if st.session_state.file_name:
        st.metric("File", "📎")
    else:
        st.metric("File", "—")

st.divider()

# CHAT HISTORY
chat_container = st.container()
with chat_container:
    for i, msg in enumerate(st.session_state.history):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                col_copy, col_search = st.columns([1, 4])
                with col_copy:
                    if st.button("📋 Copy", key=f"copy_{i}"):
                        st.code(msg["content"], language=None)
                        st.success("✅ Copied to display! Use Ctrl+C to copy from the code block above.")
                if msg.get("search_used", False):
                    with col_search:
                        st.caption("🔍 Web search used")

# CONTROLS
st.divider()
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("### 🎯 Model Selection")
    model_options = list(MODELS.keys())
    current_model_key = None
    for key, info in MODELS.items():
        if info["name"] == st.session_state.selected_model:
            current_model_key = key
            break
    if current_model_key is None:
        current_model_key = model_options[0]
    selected_model_key = st.selectbox("Choose AI Model", options=model_options, index=model_options.index(current_model_key), key="model_selector", help="Select model based on task complexity")
    model_info = MODELS[selected_model_key]
    st.caption(f"{model_info['emoji']} {model_info['description']}")
    st.session_state.selected_model = model_info["name"]

with col2:
    st.markdown("### 📎 File Upload")
    uploaded_file = st.file_uploader("Attach a file", type=None, key="file_uploader", help="Upload any file type")
    if uploaded_file:
        content = extract_file_content(uploaded_file)
        if content != st.session_state.file_context:
            st.session_state.file_context = content
            st.session_state.file_name = uploaded_file.name
            st.session_state.file_injected = False
            st.success(f"✅ Loaded")

if st.session_state.file_context:
    with st.expander(f"📄 View File: {st.session_state.file_name or 'Uploaded File'}"):
        preview_length = min(1500, len(st.session_state.file_context))
        st.code(st.session_state.file_context[:preview_length] + ("...\n[Content truncated]" if len(st.session_state.file_context) > preview_length else ""), language=None)
        st.caption(f"Total characters: {len(st.session_state.file_context):,}")

st.divider()

# INPUT
user_input = st.chat_input("💬 Type your message here...")

if user_input:
    if not st.session_state.history:
        st.session_state.chat_title = generate_chat_title(user_input)
    st.session_state.history.append({"role": "user", "content": user_input, "search_used": False})
    save_chat_message(st.session_state.chat_id, "user", user_input, False)
    st.session_state.rename_mode = False  # Exit rename mode when sending a message
    st.rerun()

# PROCESS RESPONSE
if st.session_state.history and st.session_state.history[-1]["role"] == "user":
    last_user_msg = st.session_state.history[-1]["content"]
    messages = []
    if st.session_state.file_context and not st.session_state.file_injected:
        messages.append(SystemMessage(content=f"The user has uploaded a file named '{st.session_state.file_name}'. Use its content to answer their questions.\n\nFILE CONTENT:\n{st.session_state.file_context}"))
        st.session_state.file_injected = True
    for msg in st.session_state.history[:-1]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=last_user_msg))
    
    with st.chat_message("user"):
        st.markdown(last_user_msg)
    
    try:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            search_used = False
            st.session_state.generating = True
            
            with st.spinner("⏳ Generating..."):
                for chunk, metadata, search_flag in run_chat_stream(messages, st.session_state.chat_id, st.session_state.selected_model, force_search=False, enable_auto_search=True):
                    search_used = search_flag
                    if chunk.content:
                        full_response += chunk.content
                        message_placeholder.markdown(full_response + "▋")
            
            message_placeholder.markdown(full_response)
            if search_used:
                st.caption("🔍 Web search used")
            st.session_state.generating = False
        
        st.session_state.history.append({"role": "assistant", "content": full_response, "search_used": search_used})
        save_chat_message(st.session_state.chat_id, "assistant", full_response, search_used)
        save_chat_metadata(st.session_state.chat_id, st.session_state.chat_title, st.session_state.selected_model, st.session_state.file_name)
        st.session_state.confirm_clear = False
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        st.session_state.history.append({"role": "assistant", "content": error_msg, "search_used": False})
        save_chat_message(st.session_state.chat_id, "assistant", error_msg, False)
        with st.chat_message("assistant"):
            st.error(error_msg)
            st.caption("💡 Tip: Try switching to a different model or check if Ollama is running")
        st.session_state.generating = False

# FOOTER
st.divider()
footer_col1, footer_col2, footer_col3 = st.columns(3)
with footer_col1:
    st.caption(f"🆔 Chat ID: `{st.session_state.chat_id[:8]}...`")
with footer_col2:
    st.caption(f"🤖 Model: {st.session_state.selected_model}")
with footer_col3:
    msg_count = len(st.session_state.history)
    st.caption(f"💬 Messages: {msg_count}")
