import streamlit as st

st.set_page_config(
    page_title="LizAgents",
    page_icon='🌈',
    layout='wide'
)

st.header("🌈LizAgents")
st.write("""
[![view source code ](https://img.shields.io/badge/GitHub%20Repository-gray?logo=github)](https://github.com/liz-starfield/LizAgents)
""")
st.write("""
### 🦄Vision Agent
Give me a task, I will simulate the behavior of a human operating a browser to help you process and complete tasks step by step.
### 🐷Memory Agent
I am an intelligent agent with memory, let me help you handle complex tasks, or come to chat with me.
### 🐮CSV Agent
Provide me with a CSV file and ask me about it, and I will tell you everything about the CSV file.
### 🐳PDF Agent
Provide me with a PDF file and ask me about it, and I will tell you everything about the PDF file.
### 🐯Search Agent
I can search the internet for the latest information. What would you like to know? Let me help you.
### 🐸Chat Agent
I am a basic intelligent agent; ask me a question, and I will give you the answer.
""")