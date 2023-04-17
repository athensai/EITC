import openai
import streamlit as st
import os
import util.util
from util.util import chat
from util.util import search, scrape

# Set up page configuration
st.set_page_config(page_title="Communications", page_icon=":mega:", layout="wide")

st.title('Communications 📣')

st.markdown('Not every candidate has the luxury of a large campaign team to develop customized emails, '
            'press releases, and social media posts. Our app can help save them **time**, **money**, and **energy** '
            'by generating personalized communications.')

st.markdown(
    "\n\nWe first search for information on the candidate, their background, and their platform. This allows us to " \
    'custom-tailor our messages to each candidate, going beyond the often generic output of ChatGPT and similar ' \
    'services.')
st.markdown(
    "\n\nThen, we generate personalized communications, including **emails**, **press releases**, and **social media "
    "posts**.")
st.markdown(
    "\n\nWe understand that not every candidate has information on the web. In the future, we plan to add support for "
    "**file uploads**, making personalization easier.")

# Initialize session state variables
if 'personalize' not in st.session_state:
    st.session_state['personalize'] = False

if 'generate' not in st.session_state:
    st.session_state['generate'] = False

if 'made' not in st.session_state:
    st.session_state['made'] = False

name = st.text_input("Candidate Name: ") + " campaign issues bio"
# Personalize button
if st.button("Personalize"):
    st.session_state['personalize'] = True
    st.session_state['generate'] = False

# Display additional options if the Personalize button has been clicked
if st.session_state['personalize']:
    if not st.session_state['generate']:
        st.write("Personalizing! This should take under a minute.")
    results = search(name)
    summaries = []
    q = "\nTell me about the candidate's biography, platform, " \
        "and main issues. Keep it concise but specific."

    meta = ""
    for result in results['organic_results']:
        link = result['link']
        text = scrape(link)
        if len(text) < 4000:
            title = result['title']
            snippet = result['snippet']
            summary = chat(text + q, max_tokens=200)
            summaries.append(summary)
            st.write(summary)

    all = ", ".join(summary for summary in summaries)
    meta = chat(all + q, max_tokens=200)

    # Create a tab selection
    tabs = st.selectbox('Medium:', ('Email', 'Social Media', 'Press Release', 'Other'))
    types = st.selectbox('Type:', ('Fundraising', 'Volunteer', 'Event', 'Other'))
    if tabs == 'Other' or types == 'Other':
        tabs = st.text_input("Details:")

    # Generate button
    if st.button("Generate"):
        st.session_state['generate'] = True

# Display output if the Generate button has been clicked
if st.session_state['generate'] and not st.session_state['generated']:
    st.write(meta)
    output = chat(
        f"Generate an engaging, long, and unrepetitive {tabs} for {types} in the perspective of candidate. Use this "
        f"info, if relevant {meta}.")
    st.session_state['made'] = True

if st.session_state['made']:
    st.write(output)
