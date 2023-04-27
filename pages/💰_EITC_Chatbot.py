import openai
import streamlit as st
from streamlit_chat import message
import pinecone
from langchain.chat_models import ChatOpenAI
from langchain.chains import ChatVectorDBChain
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts.prompt import PromptTemplate
from streamlit_extras.app_logo import add_logo

st.set_page_config(page_title="EITC Chatbot", page_icon=":robot_face:")

pinecone.init(
    api_key=st.secrets["PINECONE_KEY"],
    environment=st.secrets["PINECONE_ENV"]
)

openai.api_key = st.secrets["OPENAI_API_KEY"]
index_name = "eitc"
embeddings = OpenAIEmbeddings()
eitc = Pinecone.from_existing_index(index_name=index_name, embedding=embeddings)

@st.cache_data
def chat(content, messages=[], model="gpt-3.5-turbo", max_tokens=None, role="user") -> str:
    if len(messages) > 4:
        messages[-3:]
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    message = {
        "role": role,
        "content": content
    }
    messages.append(message)
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.2,
        max_tokens=max_tokens
    )
    return response.choices[0].message["content"]

# reset everything
def clear():
    if 'generated' in st.session_state:
        del st.session_state['generated']
    if 'generated_bool' in st.session_state:
        del st.session_state['generated_bool']
    if 'past' in st.session_state:
        del st.session_state['past']
    if 'messages' in st.session_state:
        del st.session_state['messages']

        # generate a response
@st.cache_data
def generate_response(prompt):

    template = "You are an AI assistant for answering questions about the Earned Income Tax Credit in " + language +  """You are 
    Provide a SIMPLE, UNDERSTANDABLE answer, but be DETAILED. Explain like I'm 10. If you don't know the answer, just say "Hmm, I'm not sure." 
    Don't try to make up an answer. If the question is not about the EITC, politely inform them that you are tuned to only 
    answer questions about the EITC. Use bullet points, line breaks. Suggest 3 additional questions. Question: {question} ========= {context} ========= MARKDOWN: """

    QA_PROMPT = PromptTemplate(template=template, input_variables=["question", "context"])

    qa = ChatVectorDBChain.from_llm(ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"), eitc,
                                    return_source_documents=False, qa_prompt=QA_PROMPT)

    prompt += "After answering, include 3 suggested follow-up questions."
    result = qa({"question": prompt, "chat_history": ""})
    response = result['answer']

    return response
st.sidebar.title("Language")

language = st.sidebar.radio("Choose a language:", ("English", "Español", "ကညီကျိာ်", "အရှေ့ပိုးကရင်", "ဖျိ"), on_change=clear())

# Read DB
# Sidebar - let user choose model and let user clear the current conversation
clear_button = st.sidebar.button("Reset Conversation", key="clear")
if clear_button:
    clear()

# Initialise session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'generated_bool' not in st.session_state:
    st.session_state['generated_bool'] = False
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": f"""You are a friendly chatbot designed to help understand the Earned "
                                      "Income Tax Credit (EITC) in {language} language. Explain like I'm 10, simple BUT WITH DETAIL. Include examples if helpful."
                                      "If you are not sure, just say so. If the"
                                      "context is not helpful, proceed normally. ONLY SPEAK IN {language}. Use bullet points, new lines, etc."""}
    ]
    output = chat("Introduce yourself, and tell me 3 suggested questions.", messages=st.session_state['messages'])
    st.session_state['generated'].append(output)
    st.session_state['past'].append('')
    message(st.session_state["generated"][0], key=str(0))

# container for chat history
response_container = st.container()
# container for text box
container = st.container()

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
       for i in range(1, len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=f"{i}_user")
            message(st.session_state["generated"][i], key=f"{i}_response")
