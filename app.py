import os
import sys, re
import urllib.request

from pyspark.sql import SparkSession
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import json, pandas as pd

import streamlit as st
from streamlit_option_menu import option_menu


client_id = "j1EkU_Uw0eHCSI7xIo6x"
client_secret = "be0nqCUsny"


def main():
    with st.sidebar:
        selected = option_menu("대시보드 메뉴",['워드클라우드 홈'], icons=['house'], 
                               menu_icon="cast",default_index=0)
    if selected=="홈":
        st.markdown("## 네이버 뉴스 검색 키워드 \n"
                "네이버 뉴스 검색을 통해 top keywords 들을 wordcloud 형태로 보여주는 대시보드입니다.")
        keyword = st.text_input("네이버 뉴스 검색")
        encText = urllib.parse.quote(str(keyword))
        url = "https://openapi.naver.com/v1/search/news?query="+encText

        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id",client_id)
        request.add_header("X-Naver-Client-Secret",client_secret)
        response = urllib.request.urlopen(request)

        rescode = response.getcode()
        if(rescode==200):
            response_body = response.read()
            #print(response_body.decode('utf-8'))
            response_json = json.loads(response_body)
            st.dataframe(response_json)
        else:
            st.markdown("Error Code:" + rescode)

    else:
        print("error")
if __name__ =="__main__":
    main()

