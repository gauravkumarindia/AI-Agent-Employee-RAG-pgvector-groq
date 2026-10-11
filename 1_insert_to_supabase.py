
# 1. Install
!pip install -q langchain-postgres langchain-huggingface sentence-transformers psycopg

from langchain_postgres import PGVector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# 2. PASTE YOUR SESSION POOLER URI HERE - must be pooler.supabase.com, not db.supabase.co
# Add +psycopg and ?sslmode=require at end
DB_URI = "postgresql://postgres.cmnxmuobhzlldxuebowh:kHiNL60uC7VUQrlF@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

docs = [
    Document(page_content="Raj Kumar - Engineering - Python, FastAPI, 5 years experience", metadata={"id": 101}),
    Document(page_content="Anjali Sharma - HR - Hiring, onboarding, 3 years", metadata={"id": 102}),
    Document(page_content="Amit Singh - Engineering - Java, Spring, 4 years", metadata={"id": 103}),
]

# 3. create_extension=False is the fix - you already enabled vector in SQL Editor
vectorstore = PGVector.from_documents(
    documents=docs,
    embedding=embeddings,
    collection_name="employees_demo",
    connection=DB_URI,
    pre_delete_collection=True,
    create_extension=False,
)
print("Stored!")

results = vectorstore.similarity_search("Who knows Python in engineering?", k=2)
for r in results:
    print("-", r.page_content)