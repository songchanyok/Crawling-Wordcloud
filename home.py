import os
import sys, re
import urllib.request
import datetime
import time

from pyspark.sql import SparkSession
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import json, pandas as pd

import streamlit as st
#[CODE 1]
def getNaverSearch(node, srcText, start, display):    
    base = "https://openapi.naver.com/v1/search"
    node = "/%s.json" % node
    parameters = "?query=%s&start=%s&display=%s" % (urllib.parse.quote(srcText), start, display)

    url = base + node + parameters    
    responseDecode = getRequestUrl(url)   #[CODE 2]
    
    if (responseDecode == None):
        return None
    else:
        return json.loads(responseDecode)

#[CODE 2]
def getRequestUrl(url):    
    client_id = "j1EkU_Uw0eHCSI7xIo6x"
    client_secret = "be0nqCUsny"

    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", client_id)
    req.add_header("X-Naver-Client-Secret", client_secret)
    
    try: 
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            return response.read().decode('utf-8')
    except Exception as e:
        #print(e)
        return None
    
def getPostData(post, jsonResult, cnt):    
    

    title = post['title']
    description = post['description']
    org_link = post['originallink']
    link = post['link']
    
    pDate = datetime.datetime.strptime(post['pubDate'],  '%a, %d %b %Y %H:%M:%S +0900')
    pDate = pDate.strftime('%Y-%m-%d %H:%M:%S')
    
    
    jsonResult.append({'cnt':cnt, 'title':title, 'description': description, 
'org_link':org_link,   'link': link,   'pDate':pDate})
    
    #temp = pd.DataFrame({'title':title, 'description': description}) #'title+description':title+description,

    #data = pd.concat([data, temp]) 
    
    return

def run_home():
    
    st.markdown("## 네이버 뉴스 검색 키워드 \n"
                "네이버 뉴스 검색을 통해 top keywords 들을 wordcloud 형태로 보여주는 대시보드입니다.")
    keyword = st.text_input("네이버 뉴스 검색")

    
    if keyword:
        node = 'news'
        cnt =0
        jsonResult=[]
        #data=pd.DataFrame()

        st.write("You entered: ",keyword)

        jsonResponse = getNaverSearch(node, str(keyword), 1, 100) 
        total = jsonResponse['total']

        
        while ((jsonResponse != None) and (jsonResponse['display'] != 0)):
            for post in jsonResponse['items']:
                cnt += 1
                rslt = getPostData(post, jsonResult, cnt)
                 
            start = jsonResponse['start'] + jsonResponse['display']
            jsonResponse = getNaverSearch(node, str(keyword), start, 100)
 
         
        st.dataframe(jsonResult)
     
        #st.markdown(jsonResult)
        #title_description_word=jsonResult['title']+jsonResult['description']
        #data = pd.DataFrame({'title+description_word':title_description_word})
        
        st.markdown('전체 검색 : %d 건' %total)
        st.markdown("가져온 데이터 : %d 건" %(cnt))

        st.markdown(jsonResult[0]['title'])


        
   