import openai
import streamlit as st
from streamlit_chat import message
import os
import re
import time
import pypdf
# import pickledb
import pinecone
import pandas as pd
from util.util import chat
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import ChatVectorDBChain
from langchain.vectorstores import FAISS
from langchain.vectorstores import Pinecone
from langchain import GoogleSearchAPIWrapper
from langchain.agents import initialize_agent, Tool
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts.prompt import PromptTemplate

st.set_page_config(page_title="FEC Chatbot", page_icon=":robot_face:")
st.title("**Simplifying Election Regulations for Local Candidates**")
st.markdown("Navigating the complexities of election laws can be overwhelming, "
            "especially for first-time candidates. We developed a **custom chatbot** to help you understand and adhere to these "
            "regulations with ease.")
st.markdown("\n\nRight now, the chatbot only answers questions about [FEC laws]("
            "https://www.fec.gov/resources/cms-content/documents/feca.pdf). In the future, we plan to add "
            "state-by-state election guidelines and filing information.", unsafe_allow_html=True)
st.markdown("\n\nWe also plan to integrate tools like Google Calendar and Gmail, automatically sending reminders and "
            "notifications for filing deadlines and regulation compliance.")
st.divider()
# Setting page title and header

openai.api_key = st.secrets["OPENAI_API_KEY"]

pinecone.init(
    api_key=st.secrets["PINECONE_KEY"],
    environment=st.secrets["PINECONE_ENV"]
)

index_name = "fec"
embeddings = OpenAIEmbeddings()

# Read DB
acc_pinecone = Pinecone.from_existing_index(index_name=index_name, embedding=embeddings)


# Initialise session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'generated_bool' not in st.session_state:
    st.session_state['generated_bool'] = False
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a chatbot designed to help local candidates understand FEC "
                                      "laws. If you are not sure, just say so. If the"
                                      "context is not helpful, proceed normally."}
    ]
    output = chat("Introduce yourself, and tell me 3 suggested questions.", messages=st.session_state['messages'])
    st.session_state['generated'].append(output)
    st.session_state['past'].append('')
    message(st.session_state["generated"][0], key=str(0))

# Sidebar - let user choose model and let user clear the current conversation
#st.sidebar.title("Sidebar")
#model_name = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4"))
#counter_placeholder = st.sidebar.empty()


# generate a response
def generate_response(prompt):

    template = """You are an AI assistant for answering questions about FEC laws. You are given the following 
    extracted parts of a long document and a question. Provide a CONVERSATIONAL, UNDERSTANDABLE answer. Suggest 3 
    follow-up questions. If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer. 
    If the question is not about FEC Laws, politely inform them that you are tuned to only answer questions about FEC 
    Laws. Suggest 3 additional questions. Question: {question} ========= {context} ========= Answer in Markdown:"""

    QA_PROMPT = PromptTemplate(template=template, input_variables=["question", "context"])

    qa = ChatVectorDBChain.from_llm(ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"), acc_pinecone,
                                    return_source_documents=True, qa_prompt=QA_PROMPT)

    prompt += " After answering, tell me where to find the info and include 3 suggested follow-up questions."
    result = qa({"question": prompt, "chat_history": ""})
    response = result['answer']

    return response


# container for chat history
response_container = st.container()
# container for text box
container = st.container()

clear_button = st.button("Clear Conversation", key="clear")
# reset everything
if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    #st.session_state['model_name'] = []

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_input("You:", key='input')
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        output = generate_response(user_input)
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
        st.session_state['generated_bool'] = True
    #st.session_state['model_name'].append(model_name)

if st.session_state['generated_bool']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))