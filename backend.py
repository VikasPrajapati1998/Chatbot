from typing import TypedDict, Annotated, List, Dict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_community.tools import DuckDuckGoSearchRun
import sqlite3
import json
import os
import re
from datetime import datetime

# -------------------- STATE --------------------

class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    search_results: Optional[str]
    needs_search: bool

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
        search_used BOOLEAN DEFAULT 0,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chat_id) REFERENCES chat_history(chat_id) ON DELETE CASCADE
    )
""")

conn.commit()

# -------------------- WEB SEARCH SETUP --------------------

search_tool = DuckDuckGoSearchRun(name="Search")

# Keywords that trigger automatic search
SEARCH_KEYWORDS = [
    # Search actions
    "search", "look up", "find", "google", "browse", "check", "lookup",
    "search for", "find out", "discover", "investigate", "research",
    
    # Time-sensitive
    "latest", "current", "today", "now", "recent", "newest", "updated",
    "this week", "this month", "this year", "yesterday", "tomorrow",
    "breaking", "live", "real-time", "up-to-date", "contemporary",
    
    # News & Events
    "news", "happening", "event", "announcement", "release", "launch",
    "update", "report", "headline", "story", "breaking news",
    
    # Question starters
    "what is", "who is", "when did", "where is", "how much", "how many",
    "what are", "who are", "when was", "when will", "where are",
    "what kind of", "which is", "why did", "how did", "how to find",
    
    # Current information
    "weather", "temperature", "forecast", "climate",
    "stock", "price", "cost", "value", "rate", "exchange rate",
    "score", "result", "winner", "ranking", "standings",
    
    # Statistics & Data
    "statistics", "stats", "data", "numbers", "figure", "count",
    "population", "gdp", "revenue", "sales", "market",
    
    # Location-based
    "near me", "nearby", "around", "local", "in my area",
    "location", "address", "directions", "map",
    
    # Availability & Status
    "available", "open", "closed", "operating hours", "schedule",
    "status", "is working", "is down", "outage",
    
    # Comparisons
    "compare", "versus", "vs", "difference between", "better than",
    "best", "top", "highest", "lowest", "cheapest", "most expensive",
    
    # Reviews & Opinions
    "review", "rating", "opinion", "feedback", "recommendation",
    "recommended", "popular", "trending", "viral",
    
    # Technology & Products
    "download", "install", "buy", "purchase", "order",
    "release date", "specifications", "specs", "features",
    "compatibility", "requirements", "version",
    
    # Sports
    "game", "match", "tournament", "championship", "league",
    "playoff", "final", "season", "team", "player",
    
    # Entertainment
    "movie", "show", "series", "episode", "trailer",
    "concert", "tour", "album", "song", "artist",
    
    # Business & Finance
    "company", "ceo", "earnings", "profit", "loss",
    "merger", "acquisition", "ipo", "shares", "dividend",
    
    # Health & Medical (current info)
    "outbreak", "epidemic", "pandemic", "vaccine", "treatment",
    "hospital", "clinic", "doctor", "appointment",
    
    # Travel
    "flight", "hotel", "booking", "reservation", "ticket",
    "destination", "travel", "tourism", "visa",
    
    # Government & Politics
    "election", "vote", "poll", "candidate", "president",
    "prime minister", "government", "policy", "law", "bill",
    
    # Education
    "university", "college", "admission", "deadline", "course",
    "scholarship", "ranking", "accreditation",
    
    # Jobs & Careers
    "job", "hiring", "salary", "career", "opening",
    "vacancy", "position", "employment", "recruitment"
]

def should_search(query: str) -> bool:
    """Determine if a query needs web search based on keywords."""
    query_lower = query.lower()
    
    # Check for search keywords
    for keyword in SEARCH_KEYWORDS:
        if keyword in query_lower:
            return True
    
    # Check for time-sensitive questions
    time_patterns = [
        r'\b(today|now|currently|latest|recent)\b',
        r'\b(this (year|month|week))\b',
        r'\b(in \d{4})\b',  # year reference
    ]
    
    for pattern in time_patterns:
        if re.search(pattern, query_lower):
            return True
    
    return False

def perform_search(query: str) -> str:
    """Perform web search and return results."""
    try:
        # Use the LLM to generate a better search query
        search_query = extract_search_query(query)
        
        # Perform the search
        results = search_tool.run(search_query)
        
        return results
    except Exception as e:
        return f"Search error: {str(e)}"

def extract_search_query(user_query: str) -> str:
    """Extract the best search query from user input."""
    # Remove common question words and get core query
    query = user_query.lower()
    
    # Remove question words
    question_words = ["what is", "who is", "where is", "when did", "how to", 
                     "tell me about", "search for", "look up", "find"]
    
    for qw in question_words:
        if query.startswith(qw):
            query = query[len(qw):].strip()
            break
    
    # Remove trailing question marks
    query = query.rstrip("?").strip()
    
    return query if query else user_query

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
        "emoji": "💪",
        "description": "Maximum capability for complex tasks"
    }
}

def get_model(model_name: str):
    """Get or create a model instance."""
    return ChatOllama(
        model=model_name,
        temperature=0.3
    )

# -------------------- NODES --------------------

def search_node(state: ChatState) -> ChatState:
    """Perform web search if needed."""
    if state.get("needs_search", False):
        # Get the last user message
        last_message = None
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                last_message = msg.content
                break
        
        if last_message:
            search_results = perform_search(last_message)
            return {
                "search_results": search_results,
                "needs_search": False
            }
    
    return {"search_results": None, "needs_search": False}

def chat_node(state: ChatState, model) -> ChatState:
    """Generate AI response, optionally using search results."""
    messages = state["messages"].copy()
    
    # If we have search results, add them as context
    if state.get("search_results"):
        search_context = SystemMessage(
            content=f"""You have access to current web search results. Use this information to answer the user's question accurately.

            SEARCH RESULTS:
            {state['search_results']}

            Important: 
            - Use the search results to provide up-to-date information
            - Cite sources when possible (mention "According to recent sources" or similar)
            - If search results are not relevant, acknowledge this and use your knowledge
            - Be concise and accurate
            """
        )
        messages.insert(-1, search_context)  # Insert before last user message
    
    response = model.invoke(messages)
    return {"messages": [response]}

# -------------------- GRAPH --------------------

checkpointer = SqliteSaver(conn)

# -------------------- RUN FUNCTION --------------------

def run_chat(messages: List[BaseMessage], thread_id: str, model_name: str, 
             force_search: bool = False, enable_auto_search: bool = True):
    """
    Run chat with optional web search capability.
    
    Args:
        messages: List of conversation messages
        thread_id: Unique thread identifier
        model_name: Name of the model to use
        force_search: Force web search regardless of content
        enable_auto_search: Enable automatic search detection
    
    Returns:
        Updated state with response and search info
    """
    model = get_model(model_name)
    
    # Determine if search is needed
    needs_search = force_search
    
    if not needs_search and enable_auto_search:
        # Check last user message for search triggers
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                needs_search = should_search(msg.content)
                break
    
    # Build the graph
    graph = StateGraph(ChatState)
    
    # Add nodes
    graph.add_node("search", search_node)
    graph.add_node("chat", lambda state: chat_node(state, model))
    
    # Add edges based on search needs
    if needs_search:
        graph.add_edge(START, "search")
        graph.add_edge("search", "chat")
    else:
        graph.add_edge(START, "chat")
    
    graph.add_edge("chat", END)
    
    # Compile workflow
    workflow = graph.compile(checkpointer=checkpointer)
    
    # Run the workflow
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {
        "messages": messages,
        "needs_search": needs_search,
        "search_results": None
    }
    
    result = workflow.invoke(initial_state, config=config)
    
    return {
        "messages": result["messages"],
        "search_used": needs_search,
        "search_results": result.get("search_results")
    }

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

def save_chat_message(chat_id: str, role: str, content: str, search_used: bool = False):
    """Save individual chat message."""
    cursor.execute("""
        INSERT INTO chat_messages (chat_id, role, content, search_used)
        VALUES (?, ?, ?, ?)
    """, (chat_id, role, content, search_used))
    conn.commit()

def get_chat_messages(chat_id: str) -> List[Dict]:
    """Get all messages for a specific chat."""
    cursor.execute("""
        SELECT role, content, search_used, timestamp
        FROM chat_messages
        WHERE chat_id = ?
        ORDER BY timestamp ASC
    """, (chat_id,))
    rows = cursor.fetchall()
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
    
    cursor.execute("SELECT COUNT(*) FROM chat_messages WHERE search_used = 1")
    total_searches = cursor.fetchone()[0]
    
    return {
        "total_chats": total_chats,
        "total_messages": total_messages,
        "total_chars": total_chars,
        "total_searches": total_searches
    }


