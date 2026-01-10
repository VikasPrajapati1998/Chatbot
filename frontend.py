import streamlit as st
from backend import (
    run_chat, save_chat_metadata, save_chat_message, get_all_chats, 
    get_chat_messages, get_chat_metadata, delete_chat, clear_all_chats, 
    generate_chat_title, MODELS, get_model_emoji, format_timestamp,
    get_database_stats
)
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import uuid
import os

# Optional loaders
from pypdf import PdfReader
from docx import Document

st.set_page_config(
    page_title="Universal Chatbot", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🤖"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .chat-item {
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .chat-item:hover {
        background-color: #f0f2f6;
    }
    .stButton button {
        transition: all 0.3s;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- SESSION STATE --------------------

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

# -------------------- FILE HANDLER --------------------

def extract_file_content(uploaded_file):
    """Extract text content from various file types."""
    filename = uploaded_file.name
    ext = os.path.splitext(filename)[1].lower()

    try:
        # TEXT FILES
        if ext in [".txt", ".py", ".js", ".html", ".css", ".c", ".cpp", ".java", ".json", ".md"]:
            return uploaded_file.read().decode("utf-8")

        # PDF FILE
        if ext == ".pdf":
            reader = PdfReader(uploaded_file)
            return "\n".join(page.extract_text() or "" for page in reader.pages)

        # DOCX FILE
        if ext == ".docx":
            doc = Document(uploaded_file)
            return "\n".join(p.text for p in doc.paragraphs)

        # UNKNOWN / BINARY FILE
        return f"""Uploaded file: {filename}
        File type: {ext}
        Size: {uploaded_file.size} bytes
        This is a binary or unsupported format."""

    except Exception as e:
        return f"Error reading file {filename}: {str(e)}"

def load_chat_history(chat_id: str):
    """Load chat history from database."""
    messages = get_chat_messages(chat_id)
    metadata = get_chat_metadata(chat_id)
    
    if messages:
        st.session_state.history = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in messages
        ]
    else:
        st.session_state.history = []
    
    if metadata:
        st.session_state.chat_title = metadata["title"]
        st.session_state.selected_model = metadata["model"]
        st.session_state.file_name = metadata["file_name"]

# -------------------- SIDEBAR - CHAT HISTORY --------------------

with st.sidebar:
    st.title("💬 Chat Manager")
    
    # Action Buttons
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
            st.rerun()
    
    with col2:
        if st.button("📊 Stats", use_container_width=True):
            st.session_state.show_stats = not st.session_state.show_stats
    
    # Show Statistics
    if st.session_state.show_stats:
        stats = get_database_stats()
        st.markdown("### 📈 Statistics")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Chats", stats["total_chats"])
        with col2:
            st.metric("Messages", stats["total_messages"])
        
        st.metric("Characters", f"{stats['total_chars']:,}")
        st.divider()
    
    # Clear All History Button
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
    
    # Search/Filter
    search_query = st.text_input("🔍 Search chats", placeholder="Type to search...")
    
    st.divider()
    
    # Display all chats
    all_chats = get_all_chats()
    
    if all_chats:
        # Filter chats based on search
        if search_query:
            all_chats = [
                chat for chat in all_chats 
                if search_query.lower() in chat['title'].lower()
            ]
        
        st.markdown(f"### 📚 Chats ({len(all_chats)})")
        
        for chat in all_chats:
            is_current = chat['chat_id'] == st.session_state.chat_id
            
            # Create a container for each chat
            with st.container():
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    # Get model emoji
                    model_emoji = get_model_emoji(chat['model'])
                    
                    # Format button label
                    file_indicator = " 📎" if chat['file_name'] else ""
                    button_label = f"{model_emoji} {chat['title']}{file_indicator}"
                    
                    if st.button(
                        button_label,
                        key=f"load_{chat['chat_id']}",
                        use_container_width=True,
                        type="primary" if is_current else "secondary"
                    ):
                        st.session_state.chat_id = chat['chat_id']
                        load_chat_history(chat['chat_id'])
                        st.session_state.file_context = ""
                        st.session_state.file_injected = False
                        st.session_state.confirm_clear = False
                        st.rerun()
                    
                    # Show metadata
                    st.caption(
                        f"💬 {chat['message_count']} msgs | "
                        f"🕒 {format_timestamp(chat['last_updated'])}"
                    )
                
                with col2:
                    if st.button("🗑️", key=f"del_{chat['chat_id']}", help="Delete"):
                        delete_chat(chat['chat_id'])
                        if chat['chat_id'] == st.session_state.chat_id:
                            st.session_state.chat_id = str(uuid.uuid4())
                            st.session_state.history = []
                            st.session_state.chat_title = "New Chat"
                            st.session_state.file_name = None
                        st.rerun()
                
                st.divider()
    else:
        st.info("💡 No chats yet. Start a conversation!")

# -------------------- MAIN CHAT AREA --------------------

# Header with chat info
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    st.title("🤖 Universal File Chatbot")
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

# Display chat history
chat_container = st.container()
with chat_container:
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# -------------------- BOTTOM CONTROLS --------------------

st.divider()

# Create columns for controls
col1, col2 = st.columns([3, 1])

with col1:
    # Model Selection with descriptions
    st.markdown("### 🎯 Model Selection")
    
    model_options = list(MODELS.keys())
    current_model_key = None
    
    for key, info in MODELS.items():
        if info["name"] == st.session_state.selected_model:
            current_model_key = key
            break
    
    if current_model_key is None:
        current_model_key = model_options[0]
    
    selected_model_key = st.selectbox(
        "Choose AI Model",
        options=model_options,
        index=model_options.index(current_model_key),
        key="model_selector",
        help="Select model based on task complexity"
    )
    
    # Show model description
    model_info = MODELS[selected_model_key]
    st.caption(f"{model_info['emoji']} {model_info['description']}")
    st.session_state.selected_model = model_info["name"]

with col2:
    # File Upload
    st.markdown("### 📎 File Upload")
    uploaded_file = st.file_uploader(
        "Attach a file",
        type=None,
        key="file_uploader",
        help="Upload any file type"
    )
    
    if uploaded_file:
        content = extract_file_content(uploaded_file)
        if content != st.session_state.file_context:
            st.session_state.file_context = content
            st.session_state.file_name = uploaded_file.name
            st.session_state.file_injected = False
            st.success(f"✅ Loaded")

# Show file preview if file is loaded
if st.session_state.file_context:
    with st.expander(f"📄 View File: {st.session_state.file_name or 'Uploaded File'}"):
        preview_length = min(1500, len(st.session_state.file_context))
        st.code(
            st.session_state.file_context[:preview_length] + 
            ("...\n[Content truncated]" if len(st.session_state.file_context) > preview_length else ""),
            language=None
        )
        st.caption(f"Total characters: {len(st.session_state.file_context):,}")

st.divider()

# Handle user input
user_input = st.chat_input("💬 Type your message here...")

if user_input:
    # Generate title from first message if this is a new chat
    if not st.session_state.history:
        st.session_state.chat_title = generate_chat_title(user_input)
    
    # Add user message to history
    st.session_state.history.append({"role": "user", "content": user_input})
    
    # Save message to database
    save_chat_message(st.session_state.chat_id, "user", user_input)
    
    with st.chat_message("user"):
        st.write(user_input)

    # Prepare messages for the model
    messages = []

    # Inject file context ONLY ONCE at the beginning
    if st.session_state.file_context and not st.session_state.file_injected:
        messages.append(
            SystemMessage(
                content=f"""The user has uploaded a file named '{st.session_state.file_name}'. Use its content to answer their questions.

            FILE CONTENT:
            {st.session_state.file_context}"""
            )
        )
        st.session_state.file_injected = True

    # Add conversation history (excluding the current message we just added)
    for msg in st.session_state.history[:-1]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))

    # Add the current user message
    messages.append(HumanMessage(content=user_input))

    # Get AI response with error handling
    try:
        with st.spinner("🤔 Thinking..."):
            result = run_chat(
                messages, 
                st.session_state.chat_id, 
                st.session_state.selected_model
            )
            ai_reply = result["messages"][-1].content

        # Add AI response to history
        st.session_state.history.append({"role": "assistant", "content": ai_reply})
        
        # Save AI message to database
        save_chat_message(st.session_state.chat_id, "assistant", ai_reply)
        
        # Save chat metadata
        save_chat_metadata(
            st.session_state.chat_id,
            st.session_state.chat_title,
            st.session_state.selected_model,
            st.session_state.file_name
        )
        
        with st.chat_message("assistant"):
            st.write(ai_reply)
        
        # Reset confirm_clear flag on new message
        st.session_state.confirm_clear = False
            
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        st.session_state.history.append({"role": "assistant", "content": error_msg})
        save_chat_message(st.session_state.chat_id, "assistant", error_msg)
        
        with st.chat_message("assistant"):
            st.error(error_msg)
            st.caption("💡 Tip: Try switching to a different model or check if Ollama is running")

# -------------------- FOOTER --------------------

st.divider()

footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.caption(f"🆔 Chat ID: `{st.session_state.chat_id[:8]}...`")

with footer_col2:
    st.caption(f"🤖 Model: {st.session_state.selected_model}")

with footer_col3:
    msg_count = len(st.session_state.history)
    st.caption(f"💬 Messages: {msg_count}")
