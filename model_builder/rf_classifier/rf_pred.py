# coding: utf-8
# import matplotlib.pyplot as plt
# import matplotlib.patches as mpatches
# get_ipython().run_line_magic('matplotlib', 'inline')
import numpy as np
import psycopg2
import pandas as pd
import jieba
import jieba.analyse
import jieba.posseg as pseg
import re
import sys
import random
import pickle as pkl
from sklearn.feature_extraction.text import  TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
# from sklearn.cluster import KMeans
# from sklearn.decomposition import PCA
from sklearn.decomposition import TruncatedSVD
jieba.load_userdict("../dict.txt.big") 

from quantify_judgement import getGuiltyNum


# In[2]:
begin = int(sys.argv[1])
end = int(sys.argv[2])
n_components = int(sys.argv[3])
n_estimators = int(sys.argv[4])

def jieba_tokenize(text):
    return  [t for t in jieba.lcut(text) if re.match("^[\u4e00-\u9fa5]",t)] 

tfidf_vectorizer = pkl.load(open("../tfidf/tfidf_vectorizer.pkl" ,'rb'))
rf = pkl.load(open("rf_%d_%d_%d_%d.pkl" % (begin,end,n_components,n_estimators) ,'rb'))
svd = pkl.dump(open("svd_%d_%d_%d_%d.pkl" % (begin,end,n_components,n_estimators) ,'rb'))

# ix2Squid = pkl.load(open("../dataset/ix2Squid.pkl" ,'rb'))

conn = psycopg2.connect(database="law1", user="datac1", password="datac15543", host="localhost", port="5432")
print("Opened database successfully")
cur = conn.cursor()

rf = pkl.load(open("%s.pkl" % model_name ,'rb'))

def compare(sqlid):
    cur.execute("""SELECT sqlid,reasonfact FROM jdata_features WHERE sqlid IN (SELECT sqlid FROM jdata_meta WHERE cat = 'M' and parser_done = 1 and sqlid >= %d and sqlid < %d) """ % ((i-1)*10000,i*10000))
    rows = cur.fetchall()

    array =  tfidf_vectorizer.transform(row[1])
    feature = svd.transform(array)

    print(sqlid,int(getGuiltyNum(sqlid,conn)),rf.predict(feature))

print(compare(int(sys.argv[5])))
