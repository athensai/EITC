from census import Census
from us import states
from datetime import date, timedelta
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
import streamlit as st
import openai
import os
import json
import time
import requests

#c = Census(st.secrets("CENSUS_API_KEY"))

@st.cache_data
def chat(content, messages=[], model="gpt-3.5-turbo", max_tokens=None, role="user") -> str:
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


def embedding(text, model="text-embedding-ada-002"):
    openai.api_key = st.secrets("OPENAI_API_KEY")
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model=model)['data'][0]['embedding']

@st.cache_data
def search(q, location="United States", news=False, time="w", n=8):
    params = {
        "q": q,
        "location": location,
        "hl": "en",
        "gl": "us",
        "google_domain": "google.com",
        "api_key": st.secrets["SERP_API_KEY"],
        "num": n
    }
    if news:
        params["tbm"] = "nws"
        params["tbs"] = "qdr:" + time
    results = GoogleSearch(params)
    return results.get_dict()

def scrape(url):
    response = requests.get(url)

    # Check if the response contains an HTTP error
    if response.status_code >= 400:
        return "Error: HTTP " + str(response.status_code) + " error"

    soup = BeautifulSoup(response.text, "html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text