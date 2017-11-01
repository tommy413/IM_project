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
from sklearn.decomposition import PCA
jieba.load_userdict("../dataset/dict.txt.big") 

def jieba_tokenize(text):
	return  [t for t in jieba.lcut(text) if re.match("^[\u4e00-\u9fa5]",t)] 

tfidf_vectorizer = pkl.load(open("../dataset/tfidf_vectorizer.pkl" ,'rb'))
# ix2Squid = pkl.load(open("../dataset/ix2Squid.pkl" ,'rb'))

conn = psycopg2.connect(database="law1", user="datac1", password="datac15543", host="ci.lu.im.ntu.edu.tw", port="5432")
print("Opened database successfully")

cur = conn.cursor()
testReasonFact = []
sqlidRsts = []

cur.execute("""SELECT sqlid,reasonfact FROM jdata_features WHERE sqlid IN (SELECT sqlid FROM jdata_meta WHERE cat = 'M' and parser_done = 1 LIMIT 100 )""")
rows = cur.fetchall()

for row in rows:
	#print(row)
	testReasonFact.append(row[1])
	sqlidRsts.append([row[0]])

tfidf_test_matrix = tfidf_vectorizer.transform(testReasonFact)

print(tfidf_test_matrix.shape)


for k in range(3,9):
	print("k = %d" % k)

	km = KMeans(n_clusters=k, init='k-means++', max_iter=300, n_init=100,verbose=1)

	result = km.fit_predict(tfidf_test_matrix)

	for i in range(0,len(result)):
		sqlidRsts[i].append(result[i])

for i in range(0,len(sqlidRsts)):
	print(sqlidRsts[i])

	