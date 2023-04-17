import streamlit as st
import pandas as pd
import tiktoken
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import openai
import os
from apify_client import ApifyClient
from datetime import datetime
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from langchain.agents import create_pandas_dataframe_agent
from util.util import search, chat, scrape
from openai.embeddings_utils import get_embedding, cosine_similarity

st.title("Opposition Research Bot")
st.markdown("Candidates need to stay informed about their opponents' activities and messaging. We have developed an "
            "**opposition research bot** that helps"
            "you track and analyze your opponent's activities in real-time using Google News and Twitter data.")
st.markdown("\n\nOur bot not only keeps you updated on your opponent's activities but also helps "
            "develop potential **attack points** and **counter messaging**. This ensures that your "
            "campaign is always prepared to respond and adapt to the dynamic political environment.")
st.markdown("\n\nIn the future, we hope to add other data sources, including fundraising data, to give a more "
            "comprehensive picture of your opponent's activities.")

name = st.text_input("Opponent Name")
twitter = st.text_input("Opponent Twitter Handle").strip("@").strip(" ")

# embedding model parameters
embedding_model = "text-embedding-ada-002"
embedding_encoding = "cl100k_base"  # this the encoding for text-embedding-ada-002
max_tokens = 8000  # the maximum for text-embedding-ada-002 is 8191
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = ApifyClient(st.secrets["APIFY_KEY"])
encoding = tiktoken.get_encoding(embedding_encoding)


@st.cache_data
def fetch_twitter_data(handles=None, keyword=None, n=100, from_date=None, to_date=None):
    run_input = {
        "tweetsDesired": n,
    }
    if handles is not None:
        run_input["handle"] = handles
        run_input["profilesDesired"] = len(handles)
    elif keyword is not None:
        run_input["searchTerms"] = keyword

    if from_date is not None:
        run_input["from_date"] = from_date
    if to_date is not None:
        run_input["to_date"] = to_date

    run = client.actor("quacker/twitter-scraper").call(run_input=run_input)
    tweet_data = [(item['created_at'], item['full_text'], item['user']['screen_name']) for item in
                  client.dataset(run["defaultDatasetId"]).iterate_items()]
    df = pd.DataFrame(tweet_data, columns=['Date', 'Text', 'Author'])
    return df

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


# Initialize session state variables
if 'search' not in st.session_state:
    st.session_state['search'] = False

if st.button("Generate"):
    st.session_state['search'] = True

if st.session_state['search']:
    with st.spinner(text="Generating report. This can take up to 2 minutes."):
        results = search(name, news=True, time="m", n=5)
        sys = [{
            "role": "system",
            "content": "You are a Democratic opposition research bot. " \
                       "Analyze this passage, identify controversial points or " \
                       "attack-worthy content, and provide specific quotes and " \
                       "a concise summary."
        }]
        summaries = []
        for result in results['news_results']:
            link = result['link']
            text = scrape(link)
            abridged = text[:2000]
            last_period_index = abridged.rfind('.')
            abridged = abridged[:last_period_index + 1]
            title = result['title']
            summary = chat(abridged, messages=sys, max_tokens=300)
            summaries.append(summary)
            all = ", ".join(summary for summary in summaries)
            if len(all) > 2000:
                all = all[:2000]
                last_period_index = all.rfind('.')
                all = all[:last_period_index + 1]
        meta = chat("You are a Democratic opposition research bot. Use this information to write a research report of the "
                    "opponent's recent activities and key points to attack them on. Use quotes if possible, but DO NOT "
                    "include footnotes. " + all + "MARKDOWN TEXT: ##", max_tokens=500, model="gpt-4")
    st.markdown(meta)

    with st.spinner(text="Generating Twitter report. This can take up to 2 minutes."):
        df = fetch_twitter_data([twitter])
        tweets = "\n".join(df['Text'])
        if len(tweets) > 2000:
            tweets = tweets[:2000]
            last_line_index = tweets.rfind('\n')
            tweets = tweets[:last_line_index + 1]
        tweets = "\n".join(df['Text'])[:1000]
        st.subheader("Tweet Analysis")
        tweet_summary = chat(f"You are a Democratic opposition research bot. Write a research report of the following "
                             f"tweets by {twitter}. Find anything controversial"
                             f" or useful to attack them on. Mention specific tweets and Devise a counter-messaging "
                             f"strategy. {tweets}. \nMARKDOWN TEXT:", model="gpt-4")

    st.markdown(tweet_summary)
    csv = convert_df(df)

    st.download_button(
        label="Download tweets as CSV",
        data=csv,
        file_name='df.csv',
        mime='text/csv',
    )
