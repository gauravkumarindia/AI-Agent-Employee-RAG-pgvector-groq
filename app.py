# app.py - FastAPI without langchain_groq (uses groq directly)
import os
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
# from langchain_huggingface import HuggingFaceEmbeddings
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except:
    from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_postgres import PGVector

# load_dotenv()

DATABASE_URL = f"postgresql://postgres.cmnxmuobhzlldxuebowh:kHiNL60uC7VUQrlF@aws-0-ap-south-1.pooler.supabase.com:5432/postgres?sslmode=require"
GROQ_API_KEY = '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'
API_KEY = os.getenv("API_KEY", "mysecretkey123")

VECTOR_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = PGVector(
    embeddings=embeddings,
    collection_name="employees_demo",
    connection=VECTOR_URL,
    create_extension=False,
)

groq_client = Groq(api_key=GROQ_API_KEY)

app = FastAPI(title="Employee RAG - Postgres")

class AskRequest(BaseModel):
    question: str

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

@app.post("/ask")
def ask(req: AskRequest, api_key: str = Depends(verify_api_key)):
    docs = vectorstore.similarity_search(req.question, k=3)
    context = "\n".join([d.page_content for d in docs])
    
    prompt = f"Context:\n{context}\n\nQuestion: {req.question}\nAnswer based only on context:"
    
    resp = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role":"user","content": prompt}],
        temperature=0
    )
    answer = resp.choices[0].message.content
    return {"answer": answer, "sources": [d.page_content[:150] for d in docs]}

@app.get("/")
def root():
    return {"status":"RAG API running with Postgres - no langchain_groq needed"}
