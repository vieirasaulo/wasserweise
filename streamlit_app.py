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
intro_markdown = '''
# About the Project
This platform has been developed by students of the GroundwatCH program during their studies at the Technische Universität Dresden (TU Dresden), within the framework of the study project **“Development of simple digital tools for hydrogeological characterization and monitoring at the Pirna test field”.**

The Pirna test field is located in the German Federal State of Saxony and it is a teaching and research field where different groundwater-related investigations have been performed in the last 15 years. It comprises more than 30 wells whereby some of them are equipped with measurement devices transmitting information to an online server, leading to huge opportunities to develop tools such as the one you are interacting with.


#### Capabilities

The platform is reproduced in an open code and it is a replicable tool. Up to date, the main capabilities of the platform are:


* Gathering of water level measurements from the installed divers at the field, transforming them it into hydraulic heads
* Visualization of real-time monitored groundwater levels for desired specific time and date
* Visualization of equipotential lines and groundwater flow direction by selecting specific wells that the user wants to consider
* Time series visualization and comparison of groundwater levels and Elbe River stage
* Hydrostatigraphic profile visualization of drilled wells



#### Current status

**This is an alpha version of an update app at a very early stage.**
* Important information about it
	1. Source of data: PegelAlarm and Inowas sensor web
	2. Where the database is stored:
		* In local repo
		* updates are commited to git and github
	3. Problem
		* Github is not a good solution for hosting a database
	4. Challenges
		* Host the database out of github
		* Deploy app_update.py online
	5. What to do next
		* Check if when cloning this repo locally the app will work well        

#### Limitations and Future improvements

The current identified limitations of the platform are listed as follow.

* This tool for groundwater flow direction cannot be blindly trusted. A calibration with the divers installed in the field should be performed
* It is considered a monitoring platform, not a platform to be used for models. It is limited to analyze and discuss the quality of the data and divers
* It only considers hydraulic heads for determining the groundwater flow direction
* No physical or chemical parameters (EC, T, etc.) are considered, despite more further parameters can be added in a future upgraded version


#### Acknowledgments

Our special thanks to our committed supervisors during our Study Project, specially to Dr. Ing. Thomas Fichtner from the Department of Hydrosciences of the Technische Universität Dresden, whose enthusiasm and knowledge guided us through all the project development. We would also like to express our particular thanks to Dr. Zhao Chen and Dr. Jana Glass for their support and recommendations.

This work would not have been possible without the financial support of the Erasmus+ Programme of the European Union. We would like to specially recognize the effort of all those involved in the **Joint Master Programme in Groundwater and Global Change Impacts and Adaptation.**


#### Further Information and Instructions

Check our [GitHub](https://github.com/SauloVSFh/PirnaStudyCase) to know more about it.

'''
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
    
#