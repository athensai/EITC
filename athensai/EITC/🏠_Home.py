import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Athens AI",
    page_icon=":dart:",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.title("AthensAI: Democratizing AI for Local Candidates")

st.markdown("""
## The Problem
Local Democratic candidates often face significant challenges when it comes to staffing and funding their campaigns. With limited resources, they struggle to effectively communicate with constituents, research opponents, navigate complex election finance laws, and refine their messaging.

## Our Solution: AthensAI
AthensAI offers a suite of powerful AI tools designed to help local Democratic candidates save time and money, allowing them to focus on what matters most - connecting with voters and winning elections.

Here's what our app can do for you:

### 1. Personalized Communication Tool
**Why it's useful:** Crafting personalized communications, such as emails and press releases, can be time-consuming and challenging. Our AI tool generates tailored content that resonates with your target audience, streamlining your communication efforts.

### 2. Opposition Research Tool
**Why it's useful:** Researching opponents is a critical part of any campaign, but it can be difficult to stay updated on their activities. Our tool automatically gathers information from Google News and Twitter, keeping you informed about your opponents' actions and statements.

### 3. FEC Chatbot
**Why it's useful:** Navigating election finance laws can be complex and confusing. Our FEC Chatbot is here to help by answering your questions about election finance regulations, ensuring your campaign stays compliant and avoids

### 4. Message Testing
**Why it's useful:** Crafting the perfect message is essential for engaging voters and promoting your campaign. Our Message Testing Bot helps you refine your messaging by analyzing the impact and effectiveness of your content. With real-time feedback, you can optimize your communication strategy and ensure your message resonates with your target audience.""")
