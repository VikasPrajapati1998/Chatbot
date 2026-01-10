# 🤖 Universal File Chatbot

A powerful, feature-rich AI chatbot built with Streamlit and LangChain that supports multiple AI models, file uploads, and persistent chat history. Think ChatGPT meets Claude, but running locally on your machine!

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 🎯 Core Features
- **Multiple AI Models**: Choose between Light (0.5B), Moderate (1B), and Heavy (8B) parameter models
- **File Upload Support**: Upload and chat about PDF, DOCX, TXT, and various code files
- **Persistent Chat History**: All conversations are saved and can be accessed anytime
- **Smart Memory**: Checkpoint-based memory system preserving conversation context
- **Multi-Chat Management**: Create, switch between, and manage multiple conversations

### 💬 Chat Features
- **Real-time Responses**: Fast AI-powered responses using Ollama
- **Message History**: Complete conversation history with timestamps
- **Chat Metadata**: Track model used, message count, and last updated time
- **Search & Filter**: Quickly find past conversations
- **Export Capabilities**: Save your chats for future reference

### 📁 File Handling
- **Multiple Format Support**: PDF, DOCX, TXT, Python, JavaScript, HTML, CSS, Java, C++, JSON, Markdown
- **File Preview**: View uploaded file content before chatting
- **Context Injection**: AI automatically uses file content to answer questions
- **File Indicators**: Visual badges showing which chats have attached files

### 🎨 User Interface
- **Clean & Modern Design**: Intuitive interface inspired by ChatGPT and Claude
- **Responsive Layout**: Wide layout with organized sidebar
- **Visual Indicators**: Emojis and color-coded elements for better UX
- **Statistics Dashboard**: Track your usage with detailed analytics
- **Relative Timestamps**: Easy-to-read time indicators (Just now, 5m ago, etc.)

### 🔧 Advanced Features
- **Model Switching**: Change AI models per conversation
- **Bulk Operations**: Clear all history with confirmation
- **Individual Chat Deletion**: Remove specific conversations
- **Auto-Title Generation**: Chats automatically titled from first message
- **Database Backend**: SQLite for reliable data persistence
- **Error Handling**: Graceful error messages with helpful suggestions

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- 4GB+ RAM (8GB+ recommended for heavy models)
- Internet connection (for initial model downloads)

### Installation

#### Windows (PowerShell)
```powershell
# Clone the repository
git clone <your-repo-url>
cd universal-chatbot

# Run setup script (installs everything)
.\setup.ps1

# Start the chatbot
.\run.ps1
```

#### Linux/Mac (Bash)
```bash
# Clone the repository
git clone <your-repo-url>
cd universal-chatbot

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

# 4. Install Ollama from https://ollama.ai/download

# 5. Pull AI models
ollama pull qwen2.5:0.5b
ollama pull llama3.2:1b
ollama pull llama3.1:8b

# 6. Start Ollama service (separate terminal)
ollama serve

# 7. Run the chatbot
streamlit run frontend.py
```

---

## 📖 Usage Guide

### Starting a New Chat
1. Click **"➕ New"** button in the sidebar
2. Select your preferred AI model
3. (Optional) Upload a file using the file uploader
4. Start chatting!

### Uploading Files
1. Click **"📎 File Upload"** section
2. Choose any supported file
3. File content is automatically loaded
4. Ask questions about the file content

### Managing Chat History
- **Load Previous Chat**: Click on any chat in the sidebar
- **Delete Chat**: Click the 🗑️ button next to chat
- **Search Chats**: Use the search box to filter conversations
- **View Statistics**: Click **"📊 Stats"** to see usage metrics

### Model Selection
- **⚡ Light (qwen2.5:0.5b)**: Fast & efficient for basic tasks
- **🎯 Moderate (llama3.2:1b)**: Balanced performance for most tasks
- **🚀 Heavy (llama3.1:8b)**: Maximum capability for complex tasks

---

## 🏗️ Project Structure

```
universal-chatbot/
│
├── backend.py              # Backend logic, model management, database
├── frontend.py             # Streamlit UI and user interactions
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── setup.ps1              # Windows setup script
├── run.ps1                # Windows run script
├── setup.sh               # Linux/Mac setup script
├── run.sh                 # Linux/Mac run script
│
└── chat_memory.db         # SQLite database (auto-created)
```

---

## 🗄️ Database Schema

### Tables

#### `chat_history`
Stores chat metadata and information.

| Column | Type | Description |
|--------|------|-------------|
| chat_id | TEXT | Primary key, unique chat identifier |
| title | TEXT | Auto-generated chat title |
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
| timestamp | TIMESTAMP | Message creation time |

---

## 🔧 Configuration

### Supported File Types
- **Documents**: `.pdf`, `.docx`, `.txt`, `.md`
- **Code**: `.py`, `.js`, `.html`, `.css`, `.c`, `.cpp`, `.java`, `.json`
- **Data**: `.csv`, `.xlsx` (with optional dependencies)

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
}
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
```

---

## 🐛 Troubleshooting

### Common Issues

**Problem: Ollama not found**
```bash
# Solution: Install Ollama
# Windows: Download from https://ollama.ai/download
# Linux: curl -fsSL https://ollama.ai/install.sh | sh
# Mac: brew install ollama
```

**Problem: Model not responding**
```bash
# Solution: Check if Ollama is running
ollama serve

# Verify models are downloaded
ollama list
```

**Problem: Port already in use**
```bash
# Solution: Use different port
streamlit run frontend.py --server.port 8502
```

**Problem: Virtual environment issues**
```bash
# Solution: Recreate virtual environment
rm -rf venv  # or Remove-Item -Recurse -Force venv on Windows
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Problem: File upload not working**
```bash
# Solution: Check file size and format
# Ensure file is under 200MB
# Verify file extension is supported
```

---

## 🚀 Advanced Usage

### Using Custom Models
```bash
# Pull any Ollama model
ollama pull mistral

# Add to MODELS dict in backend.py
"Custom Mistral": {
    "name": "mistral",
    "emoji": "🔥",
    "description": "Custom Mistral model"
}
```

### Programmatic Access
```python
from backend import run_chat
from langchain_core.messages import HumanMessage

messages = [HumanMessage(content="Hello!")]
result = run_chat(messages, "thread-123", "qwen2.5:0.5b")
print(result["messages"][-1].content)
```

### Database Queries
```python
from backend import get_all_chats, get_chat_messages

# Get all chats
chats = get_all_chats()

# Get messages from specific chat
messages = get_chat_messages("chat-id-here")
```

---

## 📊 Performance Tips

1. **Model Selection**:
   - Use Light model for quick queries
   - Use Moderate for general conversations
   - Reserve Heavy model for complex tasks

2. **File Uploads**:
   - Keep files under 50MB for best performance
   - Text files process faster than PDFs
   - Extract text from large PDFs before uploading

3. **Database Maintenance**:
   - Clear old chats periodically
   - Export important conversations
   - Database auto-optimizes on startup

---

## 🛣️ Roadmap

### Planned Features
- [ ] Streaming responses (real-time token display)
- [ ] Dark mode toggle
- [ ] Export chat as PDF/Markdown
- [ ] Code syntax highlighting
- [ ] Voice input/output
- [ ] Image upload support (vision models)
- [ ] Multi-file upload
- [ ] Conversation branching
- [ ] Custom system prompts
- [ ] API access
- [ ] Mobile app

### Future Enhancements
- Advanced search with filters
- Chat folders and tags
- Collaborative features
- Analytics dashboard
- Plugin system
- Cloud sync

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/AmazingFeature`
3. **Commit your changes**: `git commit -m 'Add some AmazingFeature'`
4. **Push to the branch**: `git push origin feature/AmazingFeature`
5. **Open a Pull Request**

### Development Setup
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black .
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Streamlit** - For the amazing web framework
- **LangChain** - For the powerful LLM orchestration
- **Ollama** - For local AI model hosting
- **Meta/Alibaba** - For the Llama and Qwen models

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/universal-chatbot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/universal-chatbot/discussions)
- **Email**: your.email@example.com

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

## 📸 Screenshots

### Main Chat Interface
```
[Screenshot of main chat interface]
```

### Chat History Sidebar
```
[Screenshot of sidebar with chat history]
```

### File Upload Feature
```
[Screenshot of file upload and preview]
```

### Statistics Dashboard
```
[Screenshot of statistics view]
```

---

<div align="center">

**Made with ❤️ by [Your Name]**

[⬆ Back to Top](#-universal-file-chatbot)

</div>