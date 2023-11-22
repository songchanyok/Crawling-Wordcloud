import os
import sys, re
import urllib.request

from pyspark.sql import SparkSession
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import json, pandas as pd

import streamlit as st
from streamlit_option_menu import option_menu

from home import run_home




def main():
    with st.sidebar:
        selected = option_menu("대시보드 메뉴",['워드클라우드 홈'], icons=['house'], 
                               menu_icon="cast",default_index=0)
    if selected=="워드클라우드 홈":
        run_home()
        

    else:
        print("error")
if __name__ =="__main__":
    main()

