from dotenv import load_dotenv

load_dotenv()


from typing import Any, Dict, List

from langchain import hub
from langchain_community.vectorstores import FAISS
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from langchain_core.documents import Document

from smolagents import tool

import json

from langchain.schema import Document
from langchain.schema import BaseRetriever

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from prompts.reasoning_prompts import formatted_reasoning_query
from retrieve.ScoreRetriever import ScoreRetriever

def process_json_string(input_string):
    # Check if the input starts with '''json and ends with '''
    if input_string.startswith("```json") and input_string.endswith("```"):
        # Remove the '''json prefix and ''' suffix
        trimmed_string = input_string[7:-3]  # Remove first 7 characters and last 3 characters
        # Load the resulting string into a JSON object
        try:
            json_object = json.loads(trimmed_string)
            return json_object
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
            return None
    else:
        return json.loads(input_string)

def run_reasoning(query: str, chat_history: List[Dict[str, Any]] = []) -> Dict:

    """
    Retrieve relevant information from stored email data using FAISS local vector retrieval.

    Args:
        query: The user query string.
        chat_history: A list of tuples with "role" and "content".

    Returns:
        dict: A response from the LLM, including retrieved information and sources.
    """

    if chat_history is None:
        chat_history = []

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    docsearch = FAISS.load_local("vector_storage", embeddings, allow_dangerous_deserialization=True)
    chat = ChatOpenAI(verbose=True, temperature=0.5, model="gpt-4o-mini")

    rephrase_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")

    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    stuff_documents_chain = create_stuff_documents_chain(chat, retrieval_qa_chat_prompt)

    retriever = ScoreRetriever(vectorstr=docsearch, k=50)

    history_aware_retriever = create_history_aware_retriever(
        llm=chat, retriever=retriever, prompt=rephrase_prompt
    )
    qa = create_retrieval_chain(
        retriever=history_aware_retriever, combine_docs_chain=stuff_documents_chain
    )


    final_formatted_reasoning_query = formatted_reasoning_query(query)
    result = qa.invoke(input={"input": final_formatted_reasoning_query, "chat_history": chat_history})

    new_res = {
        "query": result["input"],
        "result": process_json_string(result["answer"]),
        "source_documents": result["context"]
    }

    return new_res