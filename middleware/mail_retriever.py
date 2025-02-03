from smolagents import Tool
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from smolagents import OpenAIServerModel, tool
import json

def mail_retriever():
    vector_db = FAISS.load_local("vector_storage", OpenAIEmbeddings(), allow_dangerous_deserialization=True)

    retriever = vector_db.as_retriever(search_kwargs={"k": 50})
    all_docs = retriever.invoke("")

    # Print retrieved documents
    return all_docs