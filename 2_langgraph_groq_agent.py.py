from getpass import getpass
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from typing import TypedDict

GROQ_API_KEY = getpass("Enter your Groq API key (gsk_...): ")
DB_PASSWORD = getpass("Enter your Supabase DB password: ")

POOLER_URI = f"postgresql://postgres.xxxxx:{DB_PASSWORD}@aws-0-ap-south-1.pooler.supabase.com:5432/postgres?sslmode=require"
VECTOR_URI = POOLER_URI.replace("postgresql://", "postgresql+psycopg://")

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = PGVector(
    embeddings=embeddings,
    collection_name="employees_demo",
    connection=VECTOR_URI,
    create_extension=False,
)

llm = ChatGroq(model="openai/gpt-oss-120b", api_key=GROQ_API_KEY, temperature=0)

class State(TypedDict):
    question: str
    context: str
    answer: str

def retrieve(state: State):
    docs = vectorstore.similarity_search(state["question"], k=2)
    ctx = "\n".join([d.page_content for d in docs])
    return {"context": ctx}

def generate(state: State):
    prompt = f"Answer only from context below.\nContext:\n{state['context']}\n\nQuestion: {state['question']}"
    resp = llm.invoke(prompt)
    return {"answer": resp.content}

builder = StateGraph(State)
builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", END)

# FIXED PART - use with
with PostgresSaver.from_conn_string(POOLER_URI) as checkpointer:
    checkpointer.setup()
    graph = builder.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "emp_user_1"}}
    print("Ready! Ask about employees. Type 'exit' to stop.")
    while True:
        q = input("\nYour question: ")
        if q.lower() in ["exit", "quit"]:
            print("Bye!")
            break
        result = graph.invoke({"question": q}, config=config)
        print("\nAnswer:", result["answer"])
