import sys 
import os
sys.dont_write_bytecode = True #ignore __pycache__
import warnings
warnings.filterwarnings('ignore')

import numpy as np
np.seterr(divide='ignore', invalid='ignore')

import SMARTControl as sc
from pathlib import Path
import streamlit as st
import utils_dashboard as utl


def main():    
    # Settings
    st.set_page_config(layout="wide", page_title='SMARTControl')
    utl.set_page_title('SMARTControl')
    st.set_option('deprecation.showPyplotGlobalUse', False)
    # Loading CSS
    utl.local_css("frontend/css/streamlit.css")
    utl.remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')


main()



#### Main page
sc.utils.header()

def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()

markdown_fn = 'README.md'
intro_markdown = read_markdown_file(markdown_fn)
st.markdown(intro_markdown, unsafe_allow_html=True)






sc.utils.bottom()