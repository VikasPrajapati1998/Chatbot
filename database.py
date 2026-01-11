import sqlite3
from typing import List, Dict, Optional
from datetime import datetime

# -------------------- DATABASE SETUP --------------------

DB_FILE = "chat_memory.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)

# Create tables
def init_database():
    """Initialize database tables."""
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
            search_used BOOLEAN DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES chat_history(chat_id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    cursor.close()

# Initialize database on import
init_database()

# -------------------- DATABASE FUNCTIONS --------------------

def save_chat_metadata(chat_id: str, title: str, model: str, file_name: Optional[str] = None):
    """Save or update chat metadata."""
    cursor = conn.cursor()
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
    cursor.close()

def save_chat_message(chat_id: str, role: str, content: str, search_used: bool = False):
    """Save individual chat message."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_messages (chat_id, role, content, search_used)
        VALUES (?, ?, ?, ?)
    """, (chat_id, role, content, search_used))
    conn.commit()
    cursor.close()

def get_chat_messages(chat_id: str) -> List[Dict]:
    """Get all messages for a specific chat."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content, search_used, timestamp
        FROM chat_messages
        WHERE chat_id = ?
        ORDER BY timestamp ASC
    """, (chat_id,))
    rows = cursor.fetchall()
    cursor.close()
    
    return [
        {
            "role": row[0],
            "content": row[1],
            "search_used": row[2],
            "timestamp": row[3]
        }
        for row in rows
    ]

def get_all_chats() -> List[Dict]:
    """Get all chat history metadata."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT chat_id, title, model, file_name, message_count, created_at, last_updated
        FROM chat_history
        ORDER BY last_updated DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    
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
    cursor = conn.cursor()
    cursor.execute("""
        SELECT chat_id, title, model, file_name, message_count, created_at, last_updated
        FROM chat_history
        WHERE chat_id = ?
    """, (chat_id,))
    row = cursor.fetchone()
    cursor.close()
    
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
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_messages WHERE chat_id = ?", (chat_id,))
    cursor.execute("DELETE FROM chat_history WHERE chat_id = ?", (chat_id,))
    conn.commit()
    cursor.close()

def rename_chat(chat_id: str, new_title: str):
    """Rename a specific chat."""
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE chat_history 
        SET title = ?, last_updated = CURRENT_TIMESTAMP
        WHERE chat_id = ?
    """, (new_title, chat_id))
    conn.commit()
    cursor.close()

def clear_all_chats():
    """Clear all chat history and checkpoint data."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_messages")
    cursor.execute("DELETE FROM chat_history")
    cursor.execute("DELETE FROM checkpoints")
    cursor.execute("DELETE FROM writes")
    conn.commit()
    cursor.close()

def get_database_stats() -> Dict:
    """Get statistics about the database."""
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM chat_history")
    total_chats = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM chat_messages")
    total_messages = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(LENGTH(content)) FROM chat_messages")
    total_chars = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM chat_messages WHERE search_used = 1")
    total_searches = cursor.fetchone()[0]
    
    cursor.close()
    
    return {
        "total_chats": total_chats,
        "total_messages": total_messages,
        "total_chars": total_chars,
        "total_searches": total_searches
    }

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

def generate_chat_title(first_message: str) -> str:
    """Generate a title from the first message."""
    clean_message = " ".join(first_message.split())
    title = clean_message[:50]
    if len(clean_message) > 50:
        title += "..."
    return title

# Export connection for checkpointer
def get_db_connection():
    """Get database connection for checkpointer."""
    return conn

