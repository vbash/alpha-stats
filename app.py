import streamlit as st
import pandas as pd
import plotly.express as px
import pyarrow as pa

st.set_page_config(page_title="Alpha Stats Carbine", layout="wide")


st.title("Рейтинг спортсменів-стрільців. Практична стрільба. Карабін.")

url = "https://alphastatistic.com"


st.title("Ми переїхали на нову адресу: [alphastatistic.com](%s)" % url)
st.write("check out this [alphastatistic.com](%s)" % url)
st.markdown("check out this [link](%s)" % url)
