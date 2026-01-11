from typing import TypedDict, Annotated, List, Dict, Optional, Iterator
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_community.tools import DuckDuckGoSearchRun
import re
from database import get_db_connection

# -------------------- STATE --------------------

class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    search_results: Optional[str]
    needs_search: bool

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
        search_query = extract_search_query(query)
        results = search_tool.run(search_query)
        return results
    except Exception as e:
        return f"Search error: {str(e)}"

def extract_search_query(user_query: str) -> str:
    """Extract the best search query from user input."""
    query = user_query.lower()
    
    question_words = ["what is", "who is", "where is", "when did", "how to", 
                     "tell me about", "search for", "look up", "find"]
    
    for qw in question_words:
        if query.startswith(qw):
            query = query[len(qw):].strip()
            break
    
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

def get_model(model_name: str, streaming: bool = False):
    """Get or create a model instance."""
    return ChatOllama(
        model=model_name,
        temperature=0.3,
        streaming=streaming
    )

def get_model_emoji(model_name: str) -> str:
    """Get emoji for a model."""
    for model_info in MODELS.values():
        if model_info["name"] == model_name:
            return model_info["emoji"]
    return "🤖"

# -------------------- GRAPH --------------------

checkpointer = SqliteSaver(get_db_connection())

# -------------------- STREAMING RUN FUNCTION --------------------

def run_chat_stream(messages: List[BaseMessage], thread_id: str, model_name: str,
                   force_search: bool = False, enable_auto_search: bool = True,
                   max_tokens: int = 2000):
    """
    Run chat with streaming and optional web search.
    
    Args:
        messages: List of conversation messages
        thread_id: Unique thread identifier
        model_name: Name of the model to use
        force_search: Force web search regardless of content
        enable_auto_search: Enable automatic search detection
        max_tokens: Maximum tokens to prevent infinite loops
    
    Yields:
        Streaming chunks and metadata
    """
    # Determine if search is needed
    needs_search = force_search
    
    if not needs_search and enable_auto_search:
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                needs_search = should_search(msg.content)
                break
    
    # Perform search if needed
    search_results = None
    if needs_search:
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                search_results = perform_search(msg.content)
                break
    
    # Prepare messages with search context if available
    final_messages = messages.copy()
    if search_results:
        search_context = SystemMessage(
            content=f"""You have access to current web search results. Use this information to answer the user's question accurately.

SEARCH RESULTS:
{search_results}

Important: 
- Use the search results to provide up-to-date information
- Cite sources when possible (mention "According to recent sources" or similar)
- If search results are not relevant, acknowledge this and use your knowledge
- Be concise and accurate
"""
        )
        final_messages.insert(-1, search_context)
    
    # Direct streaming with loop detection
    model = get_model(model_name, streaming=True)
    
    token_count = 0
    last_chunks = []
    repetition_threshold = 50  # Number of characters to check for repetition
    
    for chunk in model.stream(final_messages):
        # Check for infinite loop (repetitive content)
        if chunk.content:
            last_chunks.append(chunk.content)
            
            # Keep only last few chunks for comparison
            if len(last_chunks) > 20:
                last_chunks.pop(0)
            
            # Check for repetition
            recent_text = "".join(last_chunks[-10:]) if len(last_chunks) >= 10 else ""
            if len(recent_text) > repetition_threshold:
                # Check if last part repeats
                half = len(recent_text) // 2
                if recent_text[:half] == recent_text[half:2*half]:
                    # Detected repetition, stop generation
                    break
            
            # Stop if max tokens reached
            token_count += 1
            if token_count > max_tokens:
                break
        
        yield chunk, {}, needs_search
