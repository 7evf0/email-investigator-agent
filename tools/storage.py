from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_core.tools import Tool

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.docstore.in_memory import InMemoryDocstore
from uuid import uuid4
import faiss

import requests
import random
import json
import os

from smolagents import tool, CodeAgent, OpenAIServerModel, ManagedAgent

@tool
def store_emails_plain(emails: list) -> str:
    """
    Store emails in the local file.

    Args:
        emails: Plain email object list with each email contains only 'subject', 'category' and 'body' fields. List includes multiple email objects.
    """
    
    file_path = "deneme.json"

    # Check if the file exists and load existing data
    if os.path.exists(file_path):
        with open(file_path, "r") as json_file:
            try:
                existing_emails = json.load(json_file)
            except json.JSONDecodeError:
                existing_emails = []  # If file is empty or corrupted, start fresh
    else:
        existing_emails = []

    # Append new emails to the existing list
    updated_emails = existing_emails + emails

    # Save the updated list back to the file
    with open(file_path, "w") as json_file:
        json.dump(updated_emails, json_file, indent=4)

    return f"Emails successfully added to '{file_path}'."

@tool
def store_emails_vector(emails: list) -> str:
    """
    Store emails in the vector database.

    Args:
        emails: Plain email object list with each email contains only 'subject', 'category' and 'body' fields. List includes multiple email objects.
    """
    try:
        vector_store = FAISS.load_local("deneme", OpenAIEmbeddings(), allow_dangerous_deserialization=True)
    except:
        index = faiss.IndexFlatL2(len(OpenAIEmbeddings().embed_query("hello world")))

        vector_store = FAISS(
            embedding_function=OpenAIEmbeddings(),
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )

    documents = []

    for email in emails:

        mail_doc = Document(
            page_content=email["body"],
            metadata={"category": email["category"], "subject": email["subject"]}
        )

        documents.append(mail_doc)

    uuids = [str(uuid4()) for _ in range(len(documents))]

    vector_store.add_documents(documents=documents, ids=uuids)
    vector_store.save_local("deneme")

    return f"Emails stored successfully."