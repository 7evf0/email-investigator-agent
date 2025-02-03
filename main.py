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

from smolagents import tool, CodeAgent, OpenAIServerModel, ManagedAgent, DuckDuckGoSearchTool, GoogleSearchTool

from tools.github_emails import *
from tools.security_emails import *
from tools.storage import *
from tools.advertisement_emails import fetch_random_product

from prompts.email_generation_prompts import *

llm = OpenAIServerModel(temperature=0.3, model_id="gpt-4o-mini")


from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":

    print("Entered")

    github_agent = CodeAgent(tools=[fetch_github_pr_commits, summarize_commit_message, store_emails_plain, store_emails_vector], model=llm, add_base_tools=True)
    #github_agent.run(github_prompt)

    security_agent = CodeAgent(tools=[fetch_security_cases, store_emails_plain, store_emails_vector], model=llm, additional_authorized_imports=["requests","bs4"])
    #security_agent.run(security_prompt)

    billing_agent = CodeAgent(tools=[fetch_random_product, store_emails_plain, store_emails_vector], model=llm, add_base_tools=True)
    billing_agent.run(billing_prompt)

    #manager_agent = CodeAgent(tools=[], model=llm, managed_agents=[manager_github_agent])

    #manager_agent.run("Generate and design 25 professional mock emails with categories of: [GitHub pull request notifications, standard emails with colleagues]. Write the emails to the person with first name of Tevfik Emre and surname Sungur.")