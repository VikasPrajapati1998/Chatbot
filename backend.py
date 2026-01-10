from typing import TypedDict, Annotated, List, Dict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import json
import os
from datetime import datetime

# -------------------- STATE --------------------

class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

# -------------------- DATABASE SETUP --------------------

DB_FILE = "chat_memory.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

# Create table for chat history metadata
cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        chat_id TEXT PRIMARY KEY,
        title TEXT,
        model TEXT,
        file_name TEXT,
        message_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Create table for storing chat messages for history loading
cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT,
        role TEXT,
        content TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chat_id) REFERENCES chat_history(chat_id) ON DELETE CASCADE
    )
""")

conn.commit()

# -------------------- MODEL MANAGEMENT --------------------

MODELS = {
    "Light (qwen2.5:0.5b)": {
        "name": "qwen2.5:0.5b",
        "emoji": "⚡",
        "description": "Fast & efficient for basic tasks"
    },
    "Moderate (llama3.2:1b)": {
        "name": "llama3.2:1b",
        "emoji": "🎯",
        "description": "Balanced performance for most tasks"
    },
    "Heavy (llama3.1:8b)": {
        "name": "llama3.1:8b",
        "emoji": "🚀",
        "description": "Maximum capability for complex tasks"
    }
}

def get_model(model_name: str):
    """Get or create a model instance."""
    return ChatOllama(
        model=model_name,
        temperature=0.3
    )

# -------------------- NODE --------------------

def chat_node(state: ChatState, model):
    response = model.invoke(state["messages"])
    return {"messages": [response]}

# -------------------- GRAPH --------------------

checkpointer = SqliteSaver(conn)

def create_workflow():
    """Create a new workflow instance."""
    graph = StateGraph(ChatState)
    return graph

# -------------------- RUN FUNCTION --------------------

def run_chat(messages: List[BaseMessage], thread_id: str, model_name: str):
    """
    Run chat with the given messages, thread_id, and model.
    Returns the updated state after processing.
    """
    model = get_model(model_name)
    
    graph = StateGraph(ChatState)
    graph.add_node("chat", lambda state: chat_node(state, model))
    graph.add_edge(START, "chat")
    graph.add_edge("chat", END)
    
    workflow = graph.compile(checkpointer=checkpointer)
    
    config = {"configurable": {"thread_id": thread_id}}
    return workflow.invoke({"messages": messages}, config=config)

# -------------------- CHAT HISTORY MANAGEMENT --------------------

def save_chat_metadata(chat_id: str, title: str, model: str, file_name: Optional[str] = None):
    """Save or update chat metadata."""
    cursor.execute("""
        INSERT INTO chat_history (chat_id, title, model, file_name, message_count, last_updated)
        VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
        ON CONFLICT(chat_id) DO UPDATE SET
            title = excluded.title,
            model = excluded.model,
            file_name = COALESCE(excluded.file_name, file_name),
            message_count = message_count + 1,
            last_updated = CURRENT_TIMESTAMP
    """, (chat_id, title, model, file_name))
    conn.commit()

def save_chat_message(chat_id: str, role: str, content: str):
    """Save individual chat message."""
    cursor.execute("""
        INSERT INTO chat_messages (chat_id, role, content)
        VALUES (?, ?, ?)
    """, (chat_id, role, content))
    conn.commit()

def get_chat_messages(chat_id: str) -> List[Dict]:
    """Get all messages for a specific chat."""
    cursor.execute("""
        SELECT role, content, timestamp
        FROM chat_messages
        WHERE chat_id = ?
        ORDER BY timestamp ASC
    """, (chat_id,))
    rows = cursor.fetchall()
    return [
        {
            "role": row[0],
            "content": row[1],
            "timestamp": row[2]
        }
        for row in rows
    ]

def get_all_chats() -> List[Dict]:
    """Get all chat history metadata."""
    cursor.execute("""
        SELECT chat_id, title, model, file_name, message_count, created_at, last_updated
        FROM chat_history
        ORDER BY last_updated DESC
    """)
    rows = cursor.fetchall()
    return [
        {
            "chat_id": row[0],
            "title": row[1],
            "model": row[2],
            "file_name": row[3],
            "message_count": row[4],
            "created_at": row[5],
            "last_updated": row[6]
        }
        for row in rows
    ]

def get_chat_metadata(chat_id: str) -> Optional[Dict]:
    """Get metadata for a specific chat."""
    cursor.execute("""
        SELECT chat_id, title, model, file_name, message_count, created_at, last_updated
        FROM chat_history
        WHERE chat_id = ?
    """, (chat_id,))
    row = cursor.fetchone()
    if row:
        return {
            "chat_id": row[0],
            "title": row[1],
            "model": row[2],
            "file_name": row[3],
            "message_count": row[4],
            "created_at": row[5],
            "last_updated": row[6]
        }
    return None

def delete_chat(chat_id: str):
    """Delete a specific chat and its messages."""
    cursor.execute("DELETE FROM chat_messages WHERE chat_id = ?", (chat_id,))
    cursor.execute("DELETE FROM chat_history WHERE chat_id = ?", (chat_id,))
    conn.commit()

def clear_all_chats():
    """Clear all chat history and checkpoint data."""
    cursor.execute("DELETE FROM chat_messages")
    cursor.execute("DELETE FROM chat_history")
    cursor.execute("DELETE FROM checkpoints")
    cursor.execute("DELETE FROM writes")
    conn.commit()

def generate_chat_title(first_message: str) -> str:
    """Generate a title from the first message."""
    # Remove extra whitespace and newlines
    clean_message = " ".join(first_message.split())
    title = clean_message[:50]
    if len(clean_message) > 50:
        title += "..."
    return title

def get_model_emoji(model_name: str) -> str:
    """Get emoji for a model."""
    for model_info in MODELS.values():
        if model_info["name"] == model_name:
            return model_info["emoji"]
    return "🤖"

def format_timestamp(timestamp_str: str) -> str:
    """Format timestamp to relative time."""
    try:
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 0:
            if diff.days == 1:
                return "Yesterday"
            elif diff.days < 7:
                return f"{diff.days} days ago"
            else:
                return dt.strftime("%b %d, %Y")
        
        hours = diff.seconds // 3600
        if hours > 0:
            return f"{hours}h ago"
        
        minutes = diff.seconds // 60
        if minutes > 0:
            return f"{minutes}m ago"
        
        return "Just now"
    except:
        return timestamp_str

def get_database_stats() -> Dict:
    """Get statistics about the database."""
    cursor.execute("SELECT COUNT(*) FROM chat_history")
    total_chats = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM chat_messages")
    total_messages = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(LENGTH(content)) FROM chat_messages")
    total_chars = cursor.fetchone()[0] or 0
    
    return {
        "total_chats": total_chats,
        "total_messages": total_messages,
        "total_chars": total_chars
    }

