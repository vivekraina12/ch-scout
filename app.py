import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="C&H Scout — NSE India",
    page_icon="📈",
    layout="wide"
)

# Read and display the HTML app
with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

components.html(html_content, height=900, scrolling=True)