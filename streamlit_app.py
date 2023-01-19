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

############# Try image as hyperlink

# import base64

# @st.cache(allow_output_mutation=True)
# def get_base64_of_bin_file(bin_file):
#     with open(bin_file, 'rb') as f:
#         data = f.read()
#     return base64.b64encode(data).decode()

# @st.cache(allow_output_mutation=True)
# def get_img_with_href(local_img_path, target_url):
#     img_format = os.path.splitext(local_img_path)[-1].replace('.', '')
#     bin_str = get_base64_of_bin_file(local_img_path)
#     html_code = f'''
#         <a href="{target_url}">
#             <img src="data:image/{img_format};base64,{bin_str}" />
#         </a>'''
#     return html_code



# cols = st.columns((10,10))
# with cols[0]:
#     TUDresden_fn = 'Assets/TuDresden_white.png'
#     gif_html = get_img_with_href(TUDresden_fn, 'https://docs.streamlit.io')
#     st.markdown(gif_html, unsafe_allow_html=True)
# with cols[1]:
#     SMARTControl_fn = 'Assets/SMARTControl_white.png'
#     gif_html = get_img_with_href(TUDresden_fn, 'https://docs.streamlit.io')
#     st.markdown(gif_html, unsafe_allow_html=True)
# # st.markdown(f"[![Foo]({TUDresden_fn})](http://google.com.au/)")



# PROBLEM HERE WITH THE SIZE OF THE IMAGE BUT IMAGE 

# image can be resize as below:
#     can base64 do the same?


# from PIL import Image

# bottom_image = st.file_uploader('', type='jpg', key=6)
# if bottom_image is not None:
#     image = Image.open(bottom_image)
#     new_image = image.resize((600, 400))
#     st.image(new_image)
    
