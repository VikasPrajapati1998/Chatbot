
# **LLaMA LOCAL SETUP GUIDE (USING OLLAMA)**

This document explains how to set up a LLaMA model locally
and use it with Python, LangChain, and LangGraph.

------------------------------------------------------------
## **STEP 1: INSTALL OLLAMA**
------------------------------------------------------------
- WINDOWS:
    1. Download from: https://ollama.com/download
    2. Run the installer
    3. Restart the system

- LINUX / MACOS:
Run the following command in terminal:

`curl -fsSL https://ollama.com/install.sh | sh`

------------------------------------------------------------
## **STEP 2: VERIFY INSTALLATION**
------------------------------------------------------------

- Run:
`ollama --version`

If a version number appears, installation is successful.


------------------------------------------------------------
## **STEP 3: START OLLAMA SERVER**
------------------------------------------------------------

- Run:
`ollama serve`

If you see an error about port 11434 already in use,
it means Ollama is already running.


------------------------------------------------------------
## **STEP 4: PULL A LLaMA MODEL**
------------------------------------------------------------

- Recommended lightweight model:

`ollama pull llama3.1:8b`

- Other supported models:

`ollama pull llama3:8b`
`ollama pull mistral:7b`
`ollama pull phi3:mini`


------------------------------------------------------------
## **STEP 5: TEST THE MODEL**
------------------------------------------------------------

- Run:
`ollama run llama3.1:8b`

- Example prompt:
Write a short blog about AI in India


------------------------------------------------------------
## **STEP 6: INSTALL PYTHON DEPENDENCIES**
------------------------------------------------------------

- Run:
`pip install langchain langchain-community langchain-openai ollama`


------------------------------------------------------------
## **STEP 7: USE LLaMA IN PYTHON**
------------------------------------------------------------

- Example code:
```
from langchain_community.chat_models import ChatOllama

model = ChatOllama(
    model="llama3.1:8b",
    temperature=0.7
)

response = model.invoke("Explain LLaMA models in simple terms")
print(response.content)
```

------------------------------------------------------------
## **STEP 8: USE WITH LANGGRAPH**
------------------------------------------------------------

- Example structure:
```
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from langchain_community.chat_models import ChatOllama

class BlogState(TypedDict):
    title: str
    outline: str
    content: str
    score: float

model = ChatOllama(model="llama3.1:8b")
```

------------------------------------------------------------
## **STEP 9: PERFORMANCE OPTIMIZATION**
------------------------------------------------------------

- REDUCE RAM USAGE:
```
model = ChatOllama(
    model="llama3.1:8b",
    temperature=0.5,
    num_ctx=2048
)
```
- CPU-ONLY SYSTEMS:
Use a smaller model:

`ollama pull phi3:mini`


------------------------------------------------------------
## **STEP 10: COMMON ISSUES**
------------------------------------------------------------

- PORT 11434 ALREADY IN USE (WINDOWS):
```
netstat -ano | findstr 11434
taskkill /PID <pid> /F
```

- CHECK INSTALLED MODELS:

`ollama list`


------------------------------------------------------------
## **MODEL STORAGE LOCATIONS**
------------------------------------------------------------

- WINDOWS:
`C:\\Users\\<user>\\.ollama\\models`

- LINUX:
`~/.ollama/models`

- MACOS:
`~/.ollama/models`


------------------------------------------------------------
## **VERIFICATION CHECKLIST**
------------------------------------------------------------

- Ollama installed
- LLaMA model pulled
- Ollama server running
- Python integration working
- LangGraph compatible
- Offline usage supported


You are now ready to run LLaMA locally.

