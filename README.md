# 🤖 Universal File Chatbot

A powerful, feature-rich AI chatbot built with Streamlit and LangChain that supports multiple AI models, file uploads, web search capabilities, and persistent chat history. Think ChatGPT meets Claude, but running locally on your machine!

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 🎯 Core Features
- **Multiple AI Models**: Choose between Light (0.5B), Moderate (1B), and Heavy (8B) parameter models
- **Intelligent Web Search**: Automatic search detection with 100+ trigger keywords for real-time information
- **File Upload Support**: Upload and chat about PDF, DOCX, TXT, and various code files
- **Persistent Chat History**: All conversations are saved with full SQLite database backend
- **Smart Memory**: LangGraph checkpoint system preserving conversation context across sessions
- **Multi-Chat Management**: Create, switch between, and manage multiple conversations

### 💬 Chat Features
- **Streaming Responses**: Real-time AI responses with token-by-token streaming
- **Auto Web Search**: Automatically searches the web when queries need current information
- **Message History**: Complete conversation history with timestamps and search indicators
- **Chat Metadata**: Track model used, message count, file attachments, and last updated time
- **Search & Filter**: Quickly find past conversations with integrated search
- **Copy to Clipboard**: Easy copying of assistant responses

### 🔍 Web Search Capabilities
- **Auto-Detection**: Intelligently detects when queries need web search
- **100+ Keywords**: Comprehensive keyword matching for search triggers
- **Time-Sensitive Queries**: Automatically searches for latest, current, or recent information
- **DuckDuckGo Integration**: Privacy-focused web search powered by DuckDuckGo
- **Search Context Injection**: Seamlessly integrates search results into AI responses
- **Source Citations**: AI references search results in responses

### 📁 File Handling
- **Multiple Format Support**: PDF, DOCX, TXT, Python, JavaScript, HTML, CSS, Java, C++, JSON, Markdown, and more
- **File Preview**: View uploaded file content with character count
- **Context Injection**: AI automatically uses file content to answer questions
- **File Indicators**: Visual badges showing which chats have attached files
- **Persistent File Context**: File content remains available throughout conversation

### 🎨 User Interface
- **Clean & Modern Design**: Intuitive interface inspired by ChatGPT and Claude
- **Responsive Layout**: Wide layout with organized sidebar navigation
- **Visual Indicators**: Emojis and color-coded elements for better UX
- **Statistics Dashboard**: Track usage with detailed analytics (chats, messages, searches, characters)
- **Relative Timestamps**: Easy-to-read time indicators (Just now, 5m ago, Yesterday, etc.)
- **Streaming Indicators**: Visual feedback during AI response generation

### 🔧 Advanced Features
- **Model Switching**: Change AI models per conversation
- **Bulk Operations**: Clear all history with confirmation dialog
- **Individual Chat Deletion**: Remove specific conversations
- **Auto-Title Generation**: Chats automatically titled from first message (50 char limit)
- **Database Backend**: SQLite with proper foreign key constraints
- **Error Handling**: Graceful error messages with helpful suggestions
- **Loop Detection**: Automatic detection and prevention of infinite response loops
- **Max Token Limiting**: Configurable token limits to prevent runaway generations

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher (3.11+ recommended)
- 8GB+ RAM (16GB+ recommended for heavy models)
- Internet connection (for initial model downloads and web search)

### Installation

#### Windows (PowerShell)
```powershell
# Clone the repository
git clone https://github.com/VikasPrajapati1998/Chatbot.git
cd Chatbot

# Run setup script (installs everything)
.\setup.ps1

# Start the chatbot
.\run.ps1
```

#### Linux/Mac (Bash)
```bash
# Clone the repository
git clone https://github.com/VikasPrajapati1998/Chatbot.git
cd Chatbot

# Make scripts executable
chmod +x setup.sh run.sh

# Run setup script (installs everything)
./setup.sh

# Start the chatbot
./run.sh
```

#### Manual Installation
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Ollama from https://ollama.com/download

# 5. Pull AI models
ollama pull qwen2.5:0.5b
ollama pull llama3.2:1b
ollama pull llama3.1:8b

# 6. Start Ollama service (separate terminal)
ollama serve

# 7. Run the chatbot
streamlit run frontend.py
```

The application will open in your browser at `http://localhost:8501`

---

## 📖 Usage Guide

### Starting a New Chat
1. Click **"➕ New"** button in the sidebar
2. Select your preferred AI model from the dropdown
3. (Optional) Upload a file using the file uploader
4. Start chatting!

### Using Web Search
The chatbot automatically detects when your query needs web search based on:
- **Search keywords**: "search", "latest", "current", "news", "weather", "stock price", etc.
- **Question patterns**: "what is", "who is", "when did", "how much", etc.
- **Time-sensitive queries**: "today", "this week", "recent", "breaking", etc.

Examples that trigger auto-search:
- "What's the latest news about AI?"
- "Current weather in New York"
- "Who won the game yesterday?"
- "Search for Python tutorials"

The AI will cite search results in its responses when applicable.

### Uploading Files
1. Click **"📎 File Upload"** section
2. Choose any supported file (PDF, DOCX, code files, etc.)
3. File content is automatically loaded and displayed
4. Ask questions about the file content
5. File context persists throughout the conversation

### Managing Chat History
- **Load Previous Chat**: Click on any chat in the sidebar
- **Delete Chat**: Click the 🗑️ button next to the chat
- **Search Chats**: Use the search box to filter conversations by title
- **View Statistics**: Click **"📊 Stats"** to see:
  - Total chats
  - Total messages
  - Total searches performed
  - Total characters processed
- **Clear All History**: Click "🗑️ Clear All" (requires confirmation)

### Model Selection
Choose the right model for your task:

- **⚡ Light (qwen2.5:0.5b)**: 
  - Fast & efficient for basic tasks
  - Quick responses
  - Lower resource usage
  
- **🎯 Moderate (llama3.2:1b)**: 
  - Balanced performance for most tasks
  - Good quality responses
  - Moderate resource usage
  
- **💪 Heavy (llama3.1:8b)**: 
  - Maximum capability for complex tasks
  - Best quality responses
  - Higher resource requirements

---

## 🗂️ Project Structure

```
Chatbot/
│
├── backend.py              # Core logic: streaming, search, models
├── database.py             # SQLite database operations
├── frontend.py             # Streamlit UI and user interactions
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── setup.ps1              # Windows setup script
├── run.ps1                # Windows run script
├── setup.sh               # Linux/Mac setup script
├── run.sh                 # Linux/Mac run script
│
├── .gitignore             # Git ignore patterns
├── Setup_Llama_Local.md   # Ollama setup guide
│
└── chat_memory.db         # SQLite database (auto-created)
```

### Key Components

#### backend.py
- Web search integration with DuckDuckGo
- Streaming chat responses
- Model management
- Search keyword detection (100+ keywords)
- Loop detection and prevention
- Search result context injection

#### database.py
- SQLite database initialization
- Chat metadata management
- Message storage and retrieval
- Statistics generation
- Timestamp formatting
- Auto-title generation

#### frontend.py
- Streamlit user interface
- Chat history sidebar
- File upload handling
- Model selection
- Real-time streaming display
- Statistics dashboard

---

## 🗄️ Database Schema

### Tables

#### `chat_history`
Stores chat session metadata.

| Column | Type | Description |
|--------|------|-------------|
| chat_id | TEXT | Primary key, unique chat identifier (UUID) |
| title | TEXT | Auto-generated chat title (max 50 chars) |
| model | TEXT | AI model used for this chat |
| file_name | TEXT | Name of uploaded file (if any) |
| message_count | INTEGER | Total messages in conversation |
| created_at | TIMESTAMP | Chat creation time |
| last_updated | TIMESTAMP | Last message time |

#### `chat_messages`
Stores individual messages from conversations.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Auto-increment primary key |
| chat_id | TEXT | Foreign key to chat_history |
| role | TEXT | 'user' or 'assistant' |
| content | TEXT | Message content |
| search_used | BOOLEAN | Whether web search was used |
| timestamp | TIMESTAMP | Message creation time |

#### `checkpoints` (LangGraph)
LangGraph checkpoint storage for conversation state.

#### `writes` (LangGraph)
LangGraph write operations for state management.

---

## 🔧 Configuration

### Supported File Types
- **Documents**: `.pdf`, `.docx`, `.txt`, `.md`
- **Code**: `.py`, `.js`, `.html`, `.css`, `.c`, `.cpp`, `.java`, `.json`
- **Data**: Text-based files (binary files show metadata only)

### Model Configuration
Edit `backend.py` to add/modify models:

```python
MODELS = {
    "Light (qwen2.5:0.5b)": {
        "name": "qwen2.5:0.5b",
        "emoji": "⚡",
        "description": "Fast & efficient for basic tasks"
    },
    # Add your custom models here
    "Custom Model": {
        "name": "your-model-name",
        "emoji": "🔥",
        "description": "Your description"
    }
}
```

### Web Search Keywords
Edit `SEARCH_KEYWORDS` in `backend.py` to customize search triggers:

```python
SEARCH_KEYWORDS = [
    "search", "latest", "current", "news",
    # Add your custom keywords here
]
```

### Streaming Parameters
Adjust in `run_chat_stream()` function:

```python
def run_chat_stream(messages, thread_id, model_name,
                   force_search=False,
                   enable_auto_search=True,
                   max_tokens=2000):  # Adjust max tokens
```

### Streamlit Configuration
Create `.streamlit/config.toml` for custom settings:

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
headless = false
enableXsrfProtection = true
```

---

## 🛠 Troubleshooting

### Common Issues

**Problem: Ollama not found**
```bash
# Solution: Install Ollama
# Windows: Download from https://ollama.com/download
# Linux: curl -fsSL https://ollama.com/install.sh | sh
# Mac: brew install ollama
```

**Problem: Model not responding**
```bash
# Check if Ollama is running
ollama serve

# Verify models are downloaded
ollama list

# Pull missing models
ollama pull qwen2.5:0.5b
```

**Problem: Port 8501 already in use**
```bash
# Use different port
streamlit run frontend.py --server.port 8502
```

**Problem: Web search not working**
```bash
# Check internet connection
# Verify duckduckgo-search is installed
pip install duckduckgo-search

# Check for search trigger keywords in your query
```

**Problem: Streaming responses stop mid-generation**
- This is the loop detection feature working
- Increase `max_tokens` in `backend.py` if needed
- Check for repetitive content in model output

**Problem: File upload not working**
```bash
# Check file size (keep under 50MB)
# Verify file extension is supported
# Check file permissions
```

**Problem: Database locked error**
```bash
# Close any other instances of the app
# Restart Streamlit
# If persists, delete chat_memory.db (will lose history)
```

**Problem: Virtual environment issues**
```bash
# Recreate virtual environment
rm -rf venv  # or Remove-Item -Recurse -Force venv on Windows
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## 🚀 Advanced Usage

### Using Custom Ollama Models
```bash
# Pull any Ollama model
ollama pull mistral
ollama pull codellama

# Add to MODELS dict in backend.py
"Custom Mistral": {
    "name": "mistral",
    "emoji": "🔥",
    "description": "Custom Mistral model"
}
```

### Programmatic Access
```python
from backend import run_chat_stream
from langchain_core.messages import HumanMessage

# Create message list
messages = [HumanMessage(content="What's the weather today?")]

# Run with streaming
for chunk, metadata, search_used in run_chat_stream(
    messages=messages,
    thread_id="my-thread",
    model_name="qwen2.5:0.5b",
    enable_auto_search=True
):
    if chunk.content:
        print(chunk.content, end="", flush=True)
```

### Database Queries
```python
from database import (
    get_all_chats,
    get_chat_messages,
    get_database_stats,
    save_chat_metadata
)

# Get all chats
chats = get_all_chats()
for chat in chats:
    print(f"{chat['title']} - {chat['message_count']} messages")

# Get messages from specific chat
messages = get_chat_messages("chat-id-here")

# Get statistics
stats = get_database_stats()
print(f"Total searches: {stats['total_searches']}")
```

### Custom Search Integration
```python
from backend import perform_search, should_search

# Check if query needs search
query = "What's the latest AI news?"
needs_search = should_search(query)  # Returns True

# Perform search
if needs_search:
    results = perform_search(query)
    print(results)
```

---

## 📊 Performance Tips

1. **Model Selection**:
   - Use Light (0.5B) for quick queries and basic conversations
   - Use Moderate (1B) for general-purpose tasks
   - Reserve Heavy (8B) for complex reasoning and detailed responses

2. **Web Search Optimization**:
   - Search is automatic but can be disabled in code
   - Search results are cached in conversation context
   - Manual search can be forced via `force_search=True`

3. **File Uploads**:
   - Keep files under 50MB for best performance
   - Text files process faster than PDFs
   - Extract text from large PDFs before uploading
   - File context is only injected once per conversation

4. **Database Maintenance**:
   - Clear old chats periodically using "Clear All"
   - Database auto-vacuums on operations
   - Export important conversations before clearing

5. **Memory Management**:
   - Each model has different RAM requirements
   - Close other applications when using Heavy model
   - Monitor RAM usage in Task Manager/Activity Monitor

6. **Streaming Performance**:
   - Streaming reduces perceived latency
   - Loop detection prevents infinite generations
   - Max tokens limit prevents excessive responses

---

## 🛣️ Roadmap

### Implemented Features ✅
- [x] Streaming responses
- [x] Web search integration
- [x] Multiple model support
- [x] File upload handling
- [x] Chat history persistence
- [x] Statistics dashboard
- [x] Auto-title generation
- [x] Search indicators
- [x] Loop detection

### Planned Features 🚧
- [ ] Dark mode toggle
- [ ] Export chat as PDF/Markdown
- [ ] Code syntax highlighting in responses
- [ ] Voice input/output
- [ ] Image upload support (vision models)
- [ ] Multi-file upload simultaneously
- [ ] Conversation branching
- [ ] Custom system prompts per chat
- [ ] API access endpoint
- [ ] Mobile-responsive design improvements
- [ ] Chat folders and tags
- [ ] Advanced search filters
- [ ] Collaborative features (shared chats)
- [ ] Analytics dashboard
- [ ] Plugin system
- [ ] Cloud sync option

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/AmazingFeature`
3. **Commit your changes**: `git commit -m 'Add some AmazingFeature'`
4. **Push to the branch**: `git push origin feature/AmazingFeature`
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 style guide for Python code
- Add comments for complex logic
- Test changes with all three models
- Update documentation as needed
- Keep dependencies minimal

### Areas for Contribution
- UI/UX improvements
- Additional file format support
- Search algorithm enhancements
- Performance optimizations
- Bug fixes
- Documentation improvements
- Translation/internationalization

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/VikasPrajapati1998/Chatbot/blob/main/LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Streamlit** - For the amazing web framework
- **LangChain** - For powerful LLM orchestration tools
- **LangGraph** - For stateful conversation management
- **Ollama** - For local AI model hosting
- **DuckDuckGo** - For privacy-focused web search
- **Meta AI** - For Llama models
- **Alibaba Cloud** - For Qwen models

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/VikasPrajapati1998/Chatbot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/VikasPrajapati1998/Chatbot/discussions)
- **Email**: vp191198@gmail.com

---

## 📝 Changelog

### Version 2.0.0 (Current)
- ✨ Added web search integration with auto-detection
- ✨ Implemented streaming responses
- ✨ Added loop detection and prevention
- ✨ Enhanced database schema with search tracking
- ✨ Improved error handling
- ✨ Added statistics dashboard
- 🐛 Fixed file context persistence
- 🐛 Fixed chat history loading

### Version 1.0.0
- Initial release
- Basic chat functionality
- File upload support
- Multiple model support
- Chat history

---

<div align="center">

**Made with ❤️ by Vikas Prajapati**

⭐ Star this repo if you find it helpful!

[⬆️ Back to Top](#-universal-file-chatbot)

</div>
