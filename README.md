# AI Agent: Employee RAG with Postgres pgvector + LangChain + LangGraph + Groq

Production-style RAG project that moves from local FAISS to cloud Postgres (Supabase) with AI Agent search. Built on a slow laptop and Colab.

## Overview
Two main scripts:
1. **Insert Records** - Takes employee data, creates HuggingFace embeddings (384-dim), stores in Supabase Postgres using pgvector extension
2. **AI Agent Search** - LangGraph agent that retrieves from pgvector and answers using Groq Llama 3.1 8B. Uses PostgresSaver for chat memory + interactive prompt in terminal/Colab.

Live table proof: `langchain_pg_embedding` with `embedding vector` and `document varchar` columns.

## Architecture
```
Employee Docs (Raj, Amit, Anjali)
   -> HuggingFaceEmbeddings (all-MiniLM-L6-v2)
   -> PGVector (Supabase Postgres + pgvector extension)
   -> Retriever (similarity_search)
   -> Groq Chat (llama-3.1-8b-instant)
   -> LangGraph (retrieve -> generate)
   -> PostgresSaver (memory in same Postgres)
```

## Tech Stack
- Python 3.10+
- Supabase Postgres with `vector` extension (pgvector)
- LangChain, langchain-postgres, langchain-groq, langchain-huggingface
- LangGraph, langgraph-checkpoint-postgres
- Groq free API
- psycopg[binary]

## Project Structure
```
.
├── 1_insert_to_supabase.py      # Insert 3 employees to Supabase
├── 2_langgraph_groq_agent.py    # AI Agent with user prompt loop
├── requirements.txt
└── README.md
```

## Setup

### 1. Supabase Setup
1. Create project at supabase.com
2. Go to SQL Editor and run:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```
3. Note your DB password and pooler URI. Use **Session Pooler (port 5432)** for Colab, not Direct (6543), because Colab does not support IPv6:
```
postgresql://postgres.PROJECT_ID:PASSWORD@aws-0-ap-south-1.pooler.supabase.com:5432/postgres?sslmode=require
```

### 2. Groq API Key
Get free key from console.groq.com -> API Keys -> Create. Starts with `gsk_...`

### 3. Install
```bash
pip install langchain langgraph langchain-groq langchain-huggingface langchain-postgres langgraph-checkpoint-postgres psycopg[binary]
```

On slow laptop if `PostgresSaver` fails:
```bash
pip install langgraph-checkpoint-postgres
# fallback: code auto-switches to MemorySaver
```

## How to Run

### Script 1: Insert Records
Stores employees like "Raj Kumar - Engineering - Python, 5 years" etc.
```bash
python 1_insert_to_supabase.py
```
Check in Supabase: Table Editor -> `langchain_pg_embedding` -> you should see 3 rows with embedding vector and document.

SQL check:
```sql
SELECT document, cmetadata FROM langchain_pg_embedding LIMIT 5;
SELECT * FROM langchain_pg_collection;
```

### Script 2: AI Agent Search
This asks for keys after running (secure) and then loops for questions.

```bash
python 2_langgraph_groq_agent.py
```

Flow after running:
```
Enter your Groq API key (gsk_...): ****
Enter your Supabase DB password: ****
Ready! Ask about employees. Type 'exit' to stop.

Your question: Who works in HR?
Answer: Anjali Sharma - HR ...

Your question: Who knows Python in Engineering?
Answer: Raj Kumar and Amit Singh ...

Your question: exit
Bye!
```

Key code fix for latest LangGraph (common error):
```python
# old (error): checkpointer = PostgresSaver.from_conn_string(URI)
# new (correct):
with PostgresSaver.from_conn_string(POOLER_URI) as checkpointer:
    checkpointer.setup()
    graph = builder.compile(checkpointer=checkpointer)
    # loop inside with block
```

## Example Questions
- Who works in HR?
- Who knows Python?
- Which engineer has 5 years experience?
- Who is in Engineering department?

## Troubleshooting

1. **AttributeError: '_GeneratorContextManager' object has no attribute 'setup'**
   Fix: Use `with PostgresSaver.from_conn_string() as checkpointer:` block.

2. **ModuleNotFoundError: No module named 'langgraph.checkpoint.postgres'**
   Fix: `pip install langgraph-checkpoint-postgres`

3. **IPv6 / connection timeout in Colab**
   Fix: Use Session Pooler URI (port 5432) with `?sslmode=require`, not Direct.

4. **FAISS vs pgvector**
   FAISS = file on laptop, lost on restart. pgvector = permanent in Postgres cloud.

## Key Points
- How to enable pgvector with `CREATE EXTENSION vector`
- Difference between Supabase Direct vs Pooler for Colab
- How to store embeddings and metadata in `langchain_pg_embedding`
- How to view data like phpMyAdmin using Table Editor and SQL Editor
- How to build RAG agent with LangGraph and add chat memory with PostgresSaver
- How to use Groq free LLM securely with `getpass` and `input()` loops

## Resume Line
"Built production RAG using Postgres (Supabase) + pgvector for vector storage, Groq Llama 3.1 for generation, and LangGraph with Postgres checkpointer for memory."

## FastAPI Extension (New)

### Additional Files
- **app.py** : API creation file - Creates FastAPI server with Postgres vector search and direct Groq client. Avoids `langchain_groq` to fix `pydantic_v1` error. Endpoint `/ask` with `x-api-key` protection.
- **callapi.py** : For normal calling of API - Single request test
- **callapi2.py** : For next calling of API - Continuous chat loop via API

### How to Run API
**Terminal 1 (keep running):**
```bash
python -m uvicorn app:app --reload
```

**Terminal 2:**
```bash
python callapi.py
# or
python callapi2.py
```

### Why direct Groq client?
`langchain_groq` fails with `ModuleNotFoundError: No module named 'langchain_core.pydantic_v1'` on latest langchain versions. Solution: use `from groq import Groq` directly, works without venv.

Install fix:
```bash
python -m pip install groq psycopg langchain-huggingface langchain-postgres
```

## Future Improvements
- Add Streamlit UI
- Add HNSW index tuning for faster search
- Add RLS enabled for production

---
Built on low-spec laptop to prove you don't need heavy infra for GenAI.
