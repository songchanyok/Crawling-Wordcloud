import os
import sys, re
import urllib.request
import datetime
import time

from pyspark.sql import SparkSession
import matplotlib.pyplot as plt
from matplotlib import font_manager

from wordcloud import WordCloud
import json, pandas as pd

from konlpy.tag import Mecab,Okt
from nltk.stem import PorterStemmer, LancasterStemmer
from nltk import Text

from collections import Counter

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
    
    
    return

def run_home():
    nlp = Okt()
    st.markdown("## 네이버 뉴스 검색 키워드 \n"
                "네이버 뉴스 검색을 통해 top keywords 들을 wordcloud 형태로 보여주는 대시보드입니다.")
    keyword = st.text_input("네이버 뉴스 검색")

    
    if keyword:
        node = 'news'
        cnt =0
        jsonResult=[]

        st.write("You entered: ",keyword)

        jsonResponse = getNaverSearch(node, str(keyword), 1, 100) 
        total = jsonResponse['total']

        
        while ((jsonResponse != None) and (jsonResponse['display'] != 0)):
            for post in jsonResponse['items']:
                cnt += 1
                getPostData(post, jsonResult, cnt)
                 
            start = jsonResponse['start'] + jsonResponse['display']
            jsonResponse = getNaverSearch(node, str(keyword), start, 100)
 
         
        st.dataframe(jsonResult)
     
        st.markdown('전체 검색 : %d 건' %total)
        st.markdown("가져온 데이터 : %d 건" %(cnt))

        #st.markdown(jsonResult[0]['title'])
        whole_title = [i['title'] for i in jsonResult]
        whole_description=[i['description'] for i in jsonResult]
        whole_title_and_description = [i['title'] + ' ' + i['description'] for i in jsonResult]
        whole_pDate=[i['pDate'][:10] for i in jsonResult]
        date_list=[]
        for i in range(len(jsonResult)):
            if i == 0:
                date_list.append(jsonResult[i]['pDate'][:10])
            else:
                if jsonResult[i]['pDate'][:10] not in date_list:
                    date_list.append(jsonResult[i]['pDate'][:10])

        
        df = pd.DataFrame({'title':whole_title, 'description':whole_description,'title+description':whole_title_and_description,
                           'pDate_ymd':whole_pDate})

        
        df['Noun'] = df['title+description'].apply(lambda x: nlp.nouns(x))

        #st.dataframe(df)
        

        keyword_noun = [j for i in df['Noun'] for j in i if j not in ['것','이번',str(keyword)] and len(j) > 1]

        keyword_noun_dict=dict(Counter(keyword_noun).most_common(100))

        font_path = './font/NanumGothic.ttf'
        fpath = os.path.join(os.getcwd(),"Nanum_Gothic/NanumGothic-Bold.ttf")
        prop = font_manager.FontProperties(fname=fpath)
        font = prop.get_name()
        plt.rc('font', family=font)
        
        wc = WordCloud(font_path = font_path ,
               background_color='white',
               width=1000,
               height=1000,
               max_font_size=300)

        fig = plt.figure(figsize=(25,20))
        wc.generate_from_frequencies(keyword_noun_dict) #워드클라우드 생성
        plt.imshow(wc, interpolation='bilinear')
        plt.axis("off")
        plt.title(f'네이버 검색 {str(keyword)} 관련 키워드 top 100',fontproperties=prop)
        #fig.suptitle(f'네이버 검색 {str(keyword)} 관련 키워드 top 100')
        fig.tight_layout()
        #plt.show()
        st.pyplot(fig)

        st.markdown(keyword_noun_dict)
        
        #Text Graph
        # date_1_keywords = [j for i in df.query('pDate_ymd == date_list[0]')['Noun'] for j in i if j not in ['것','이번',str(keyword)] and len(j) > 1]
        # date_2_keywords = [j for i in df.query('pDate_ymd == date_list[1]')['Noun'] for j in i if j not in ['것','이번',str(keyword)] and len(j) > 1]
        # date_3_keywords = [j for i in df.query('pDate_ymd == date_list[2]')['Noun'] for j in i if j not in ['것','이번',str(keyword)] and len(j) > 1]
        st.markdown('### 3일간 Top Keywords 변동 추이')
        text = plt.figure(figsize=(24,10))
        plt.xlabel('키워드',fontproperties=prop)
        plt.ylabel('빈도수',fontproperties=prop)
        plt.grid(True)

        #sorted_Keys = sorted(keyword_noun_dict, key=word_count.get, reverse=True)
        #sorted_Values = sorted(keyword_noun_dict.values(), reverse=True)

        plt.bar(range(len(keyword_noun_dict)), keyword_noun_dict.values(), align='center')
        plt.xticks(range(len(keyword_noun_dict)), keyword_noun_dict.keys(), rotation='vertical',fontproperties=prop)
        
        
        st.pyplot(text)

        text_2 = Text(keyword_noun_dict, name="kolaw")
        text_2.plot(30)

        st.pyplot(text_2)


        


        



        
   