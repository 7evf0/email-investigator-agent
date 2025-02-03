from dotenv import load_dotenv

load_dotenv()


from typing import Any, Dict, List

from langchain import hub
from langchain_community.vectorstores import FAISS
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate

from smolagents import tool, CodeAgent, OpenAIServerModel

import ast

from prompts.report_prompt import main_prompt

import json
from datetime import date

import re

llm = OpenAIServerModel(model_id="gpt-4o-mini", temperature=0.3)

@tool
def retrieve_all_mails() -> list:
    """
    Retrieves all of the emails for report generation.

    Returns:
        all_docs: List of all returned documents, including page_content and metadata.
    """

    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    docsearch = FAISS.load_local("email_vector_db", embeddings, allow_dangerous_deserialization=True)
    
    retriever = docsearch.as_retriever(search_kwargs={"k": 50})
    all_docs = retriever.invoke("")

    billing_count = len([doc for doc in all_docs if doc.metadata["category"] == "Billing"])
    security_count = len([doc for doc in all_docs if doc.metadata["category"] == "Security"])
    PR_count = len([doc for doc in all_docs if doc.metadata["category"] == "Github PR"])

    return all_docs

@tool
def get_current_date() -> date:
    """
    Returns the date of today.
    """
    return date.today()

@tool
def billing_json(emails: list) -> list:

    """
    Returns the json list of emails with 'Billing' category.

    Args:
        emails: List of all retrieved emails.
    """

    billing_emails = []                                                                   
    for email in emails:                                                                  
        if email.metadata['category'] == 'Billing':                                       
            content = email.page_content                                                  
            product_name = content.split("Product Name: ")[1].split("\n")[0]              
            amount = float(content.split("Price: $$")[1].split("\n")[0])                  
            status = "Awaiting Payment"  # All billing emails are awaiting payment        
            billing_emails.append({"Product Name": product_name, "Amount": amount,        
    "Status": status})                                                                    
                                                                                        
    # Sort billing emails by amount                                                       
    billing_emails.sort(key=lambda x: x["Amount"], reverse=True)

    return billing_emails

@tool
def security_json(emails: list) -> list:

    """
    Returns the json list of emails with 'Security' category.

    Args:
        emails: List of all retrieved emails.
    """

    security_alerts = []                                                                  
    for email in emails:                                                                  
        if email.metadata['category'] == 'Security':                                      
            content = email.page_content                                                  
            alert_type = content.split("Subject: ")[1].split("\n")[0]                     
            warning_date = content.split("Warning Date: ")[1].split("\n")[0]              
            action_required = "Immediate action required"                               
            security_alerts.append({"Alert Type": alert_type, "Date": warning_date, "Action Required": action_required})                                                  
                                                                                            
    # Sort security alerts by date                                                        
    security_alerts.sort(key=lambda x: x["Date"], reverse=True)                                         
    print(security_alerts)

    return security_alerts

@tool
def github_pr_json(emails: list) -> list:

    """
    Returns the json list of emails with 'Github PR' category.

    Args:
        emails: List of all retrieved emails.
    """

    github_prs = []                                                                       
    for email in emails:                                                                  
        if email.metadata['category'] == 'Github PR':                                     
            content = email.page_content                                                  
            pr_title = content.split("Subject: ")[1].split("\n")[0]                       
            committer = content.split("Committer: ")[1].split("\n")[0]                    
            pr_date = content.split("Date: ")[1].split("\n")[0]                           
            pr_hour = content.split("Hour: ")[1].split("\n")[0]                           
            review_status = "Awaiting Review"  # Assuming all PRs are awaiting review     
            github_prs.append({"PR Title": pr_title, "Commiter": committer, "Status":     
    review_status, "Date": pr_date, "Hour": pr_hour})                                     
                                                                                            
    # Sort GitHub PRs by date and hour                                                    
    github_prs.sort(key=lambda x: (x["Date"], x["Hour"]), reverse=True)                                 
    
    return github_prs

@tool
def split_report_multiple(report_text: str) -> list:
    """
    Splits a plain-text email report into structured sections, extracting all JSON lists 
    and the text surrounding them.

    Args:
        report_text: Plain text of the whole report.
    
    Returns:
    - A list of dictionaries, each containing either "text" or "json" content.
    """
    sections = []
    json_pattern = re.compile(r"\[\{(.*?)\}\]", re.DOTALL)  # Regex to find JSON lists

    # Find all JSON-like data
    matches = list(json_pattern.finditer(report_text))
    
    if not matches:  # If no JSON is found, return the whole text
        return [{"type": "text", "content": report_text.strip()}]

    last_end = 0  # Track position for text before JSON blocks

    for match in matches:
        start, end = match.span()

        # Add the text before the JSON (if any)
        if start > last_end:
            text_chunk = report_text[last_end:start].strip()
            if text_chunk:
                sections.append({"type": "text", "content": text_chunk})

        # Extract and parse the JSON block
        json_chunk = match.group(0)  # Raw JSON-like text
        try:
            parsed_json = ast.literal_eval(json_chunk)  # Convert to a Python list
            sections.append({"type": "json", "content": parsed_json})
        except json.JSONDecodeError:
            sections.append({"type": "text", "content": json_chunk})  # If JSON parsing fails, keep as text

        last_end = end  # Update position

    # Add the remaining text after the last JSON block
    remaining_text = report_text[last_end:].strip()
    if remaining_text:
        sections.append({"type": "text", "content": remaining_text})

    return sections

def generate():

    report_agent = CodeAgent(tools=[retrieve_all_mails, get_current_date, billing_json, security_json, github_pr_json], model=llm, additional_authorized_imports=["datetime"], max_steps=8)

    res = report_agent.run(main_prompt)
    print(res)

    res = split_report_multiple(res)

    return res



def generate_report():

    print("Entered...")

    all_docs, count_billing_emails, count_security_emails, count_PR_emails = retrieve_all_mails()

    report_prompt_template = PromptTemplate(
        input_variables=["emails"], template=main_prompt
    )

    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")

    chain = report_prompt_template | llm
    res = chain.invoke(input={"emails": all_docs, "count_billing_emails": count_billing_emails, "count_security_emails": count_security_emails, "count_PR_emails": count_PR_emails})

    print(res)
    return split_report_multiple(res.content)

import re
import json

import re
import json


# Example Usage
report_text = """## 📧 Email Investigation Report
**Date:** October 30, 2023  
**Generated by:** Email Investigator Agent  

---

### 1️⃣ Billing Summary
- **Total Billing Emails:** 15
- **Pending Payments:**  

[
    {"Product Name": "White Gold Plated Princess", "Amount": 9.99, "Status": "Awaiting Payment"},
    {"Product Name": "Mens Casual Slim Fit", "Amount": 15.99, "Status": "Awaiting Payment"}
]

- **Most Urgent Payment:**
  John Hardy Women's Legends Naga Gold & Silver Dragon Station Chain Bracelet (Amount: $ 695.00)

---

### 2️⃣ Security Alerts
- **Total Security Warnings:** 15
- **Critical Alerts:**

[
    {"Alert Type": "Data Loss Prevention", "Date": "2025-02-01", "Action Required": "Immediate review"},
    {"Alert Type": "Weak Password Policies", "Date": "2025-02-01", "Action Required": "Immediate review"}
]

- **Urgent Warnings:**
- Weak Password Policies (2025-02-01) → Immediate review
"""

