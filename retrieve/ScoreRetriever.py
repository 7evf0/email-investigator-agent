from dotenv import load_dotenv

load_dotenv()

from typing import Any, Dict, List

from langchain_community.vectorstores import FAISS

from langchain_core.documents import Document

from langchain.schema import Document
from langchain.schema import BaseRetriever

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever


class ScoreRetriever(BaseRetriever):
    """A toy retriever that contains the top k documents that contain the user query.

    This retriever only implements the sync method _get_relevant_documents.

    If the retriever were to involve file access or network access, it could benefit
    from a native async implementation of `_aget_relevant_documents`.

    As usual, with Runnables, there's a default async implementation that's provided
    that delegates to the sync implementation running on another thread.
    """

    vectorstr: FAISS
    """Vector database to retrieve from."""
    k: int
    """Number of top results to return"""
    
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        
        matching_documents, scores = zip(*self.vectorstr.similarity_search_with_score(query, k=self.k))
        for doc, score in zip(matching_documents, scores):
            doc.metadata["score"] = float(score)
        
        return matching_documents