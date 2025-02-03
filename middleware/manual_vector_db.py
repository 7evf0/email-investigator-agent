import faiss
import json
import numpy as np
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

file_path = "stored_emails.json"  # Change this to the actual file path

# ✅ Step 2: Load JSON data from file
with open(file_path, "r", encoding="utf-8") as file:
    email_data = json.load(file)  

# ✅ Step 1: Initialize OpenAI Embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

# ✅ Step 2: Convert Emails into LangChain Document Format
docs = []
for email in email_data:
    email_text = f"Subject: {email['subject']}\nCategory: {email['category']}\nBody: {email['body']}"
    doc = Document(page_content=email_text, metadata={"subject": email["subject"], "category": email["category"]})
    docs.append(doc)

# ✅ Step 3: Store Data in FAISS
vector_store = FAISS.from_documents(docs, embeddings)

# ✅ Step 4: Save FAISS index for later use
vector_store.save_local("vector_storage")
print("FAISS Vector Store Saved Successfully!")
