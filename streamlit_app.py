import sys 
sys.dont_write_bytecode = True #ignore __pycache__
import warnings
warnings.filterwarnings('ignore')

import numpy as np
np.seterr(divide='ignore', invalid='ignore')

import SMARTControl as sc
from pathlib import Path
import streamlit as st


st.set_page_config(layout='wide', 
                   page_icon = "📡",
                   initial_sidebar_state='expanded')


with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)





# @st.cache (allow_output_mutation=True)
##### SideBar
st.sidebar.header('SMART`Control`')

st.sidebar.markdown('''
---
Created with ❤️ by [Saulo, Nicolás and Cláudia](https://github.com/SauloVSFh/PirnaStudyCase)
''')


#### Main page
sc.utils.header()

def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()


markdown_fn = 'README.md'
intro_markdown = read_markdown_file(markdown_fn)
st.markdown(intro_markdown, unsafe_allow_html=True)

sc.utils.bottom()