from test import run_llm
from reasoning import run_reasoning

import streamlit as st
from streamlit_chat import message
from st_pages import Page, add_page_title

from middleware.mail_retriever import mail_retriever

from RetrievalTool import run_chart_agent, run_agent

import plotly.express as px
from streamlit_option_menu import option_menu
import streamlit_shadcn_ui as ui

from report_generator import generate_report, generate

import json
import time
import pandas as pd
import numpy as np

def create_sources_format(sources: set[str]) -> str:
    if not sources:
        return ""
    sources_list = list(sources)
    sources_list.sort()
    sources_string = "Source Emails:\n"

    for i, source in enumerate(sources_list):
        if i < 5:
            sources_string += f"{i+1}. {source}\n"
        else:
            break

    return sources_string

def stream_data(prompt: str):
    for word in prompt.split(" "):
        yield word + " "
        time.sleep(0.02)
    
option_menu(None, ["Home", "Chat", "Report", 'Settings'],
        icons=['house', 'cloud-upload', "list-task", 'gear'],
        key='menu', orientation="horizontal")

if st.session_state["menu"] == "Home":
    st.header("Welcome to the Email Investigator")
    st.subheader("Available Emails")

    all_docs = mail_retriever()

    choice = ui.select(options=set(doc.metadata["category"] for doc in all_docs))

    for i, doc in enumerate([doc for doc in all_docs if doc.metadata["category"] == choice]):
        with st.expander(doc.metadata["subject"]):
            st.write(doc.page_content)

if st.session_state["menu"] == "Report":

    with st.spinner("Creating Report"):

        structured_data = generate()

        text_data = [sec for sec in structured_data if sec["type"] == "text"]
        json_data = [sec for sec in structured_data if sec["type"] == "json"]

        f"""{text_data[0]["content"]}"""
        st.dataframe(pd.DataFrame(json_data[0]["content"]))

        st.write(text_data[1]["content"])
        st.dataframe(pd.DataFrame(json_data[1]["content"]))

        st.write(text_data[2]["content"])
        st.dataframe(pd.DataFrame(json_data[2]["content"]))

        st.write(text_data[3]["content"])

if st.session_state["menu"] == "Chat":
        
    st.header("Email Investigator Agent")

    prompt = st.chat_input("Enter your question here...")

    # Initialize session state variables
    if "user_prompt_history" not in st.session_state:
        st.session_state["user_prompt_history"] = []

    if "chat_answers_history" not in st.session_state:
        st.session_state["chat_answers_history"] = []

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    if "status" not in st.session_state:
        st.session_state["status"] = []

    if "sources" not in st.session_state:
        st.session_state["sources"] = []

    if "charts" not in st.session_state:
        st.session_state["charts"] = []

    last_result = ""

    if prompt:

        with st.spinner("Generating Response"):
            # Retrieve response from the backend
            generated_response = run_reasoning(
                query=prompt, chat_history=st.session_state["chat_history"]
            )

            #generated_response = run_agent(
            #    prompt=prompt, chat_history=[]
            #)

            top_3_documents = sorted(generated_response["source_documents"], key=lambda doc: doc.metadata["score"], reverse=True)[:3]

            #generated_response = run_agent(prompt=prompt, chat_history=st.session_state["chat_history"])

            # Extract email subjects from source documents
            email_subjects = [doc.metadata["subject"] for doc in top_3_documents]

            formatted_response = (
                f"{generated_response['result']["result"]}"
            )

            #{create_sources_format(email_subjects)}

            # Update histories
            st.session_state["user_prompt_history"].append(prompt)
            st.session_state["chat_answers_history"].append(formatted_response)
            st.session_state["status"].append(json.dumps(generated_response["result"]['chain']))
            st.session_state["sources"].append(email_subjects)
            st.session_state["charts"].append({})

            # Append the current interaction to chat history
            st.session_state["chat_history"].append(("human", prompt))
            st.session_state["chat_history"].append(("ai",generated_response["result"]["result"]))
            last_result = generated_response["result"]["result"]

    # Display chat history in Streamlit
    if st.session_state["chat_answers_history"]:
        history_length = len(st.session_state["chat_answers_history"])
        
        for i, (generated_response, user_query, status, sources, chart) in enumerate(zip(
            st.session_state["chat_answers_history"], 
            st.session_state["user_prompt_history"], 
            st.session_state["status"],
            st.session_state["sources"],
            st.session_state["charts"]
        )):

            with st.status("Chain of Thoughts"):
                status = json.loads(status)
                for step in status:
                    st.write(step["result"])
            
            with st.chat_message("user"):
                st.write(user_query)

            with st.chat_message("ai"):
                if i < history_length - 1:
                    st.write(generated_response)
                else:
                    st.write_stream(stream_data(generated_response))

                ui.badges(badge_list=[(subject, "default") for subject in sources])
            
            with st.expander("Charts"):
                if i < history_length - 1:
                    if chart == {}:
                        st.write("No charts generated for this prompt.")
                    else:
                        st.subheader(chart["title"])
                        st.bar_chart(data=chart["key_value_dict"], x_label=chart["x_label"], y_label=chart["y_label"])

    if prompt:
        with st.expander("Charts"):

            with st.spinner("Evaluating for chart generation."):

                bar_chart_info = run_chart_agent(query=prompt, response=last_result)

                if(bar_chart_info["result"]) == True:

                    bar_chart = bar_chart_info["bar_chart_object"]

                    st.subheader(bar_chart["title"])
                    st.bar_chart(data=bar_chart["key_value_dict"], x_label=bar_chart["x_label"], y_label=bar_chart["y_label"])

                    st.session_state["charts"][-1] = bar_chart

                else:
                    st.write("No charts generated for this prompt.")