# coding: utf-8
import numpy as np
import psycopg2
import pandas as pd
import jieba
import jieba.analyse
import jieba.posseg as pseg
import re
import pickle as pkl
from sklearn.feature_extraction.text import  TfidfVectorizer
from sklearn.cluster import KMeans
jieba.load_userdict("dict.txt.big") 

def jieba_tokenize(text):
	return  [t for t in jieba.lcut(text) if re.match("^[\u4e00-\u9fa5]",t)] 

tfidf_vectorizer = TfidfVectorizer(tokenizer=jieba_tokenize, lowercase=False, ngram_range = (1,3), max_df = 0.85, min_df = 0.15)

conn = psycopg2.connect(database="law1", user="datac1", password="datac15543", host="localhost", port="5432")
print("Opened database successfully")

cur = conn.cursor()
allText = []
ix2Squid = {}

for i in range(1,1252):
	cur.execute("""SELECT jfull FROM jdata where sqlid IN (Select sqlid FROM jdata_meta WHERE sqlid >= %d and sqlid < %d and cat = 'M') """ % ((i-1)*10000,i*10000))
	rows = cur.fetchall()

	for row in rows:
		#ix2Squid[len(allText)] = row[0]
		allText.append(row[0])
	print(i,len(allText))

tfidf_vectorizer.fit(allText)

#pkl.dump(tfidf_matrix, open("tfidf_matrix.pkl" ,'wb'), pkl.HIGHEST_PROTOCOL)
pkl.dump(tfidf_vectorizer, open("tfidf_vectorizer.pkl" ,'wb'), pkl.HIGHEST_PROTOCOL)
#pkl.dump(ix2Squid, open("ix2Squid.pkl" ,'wb'), pkl.HIGHEST_PROTOCOL)

#print(tfidf_matrix.shape)
