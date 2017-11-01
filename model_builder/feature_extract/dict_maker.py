# coding: utf-8
import numpy as np
import psycopg2
import jieba
import jieba.analyse
import jieba.posseg as pseg
import re
import math
jieba.load_userdict("dict.txt.big") 

conn = psycopg2.connect(database="law1", user="datac1", password="datac15543", host="localhost", port="5432")
print("Opened database successfully")

cur = conn.cursor()
df = {}
doc_count = 0

for i in range(1,1260):
	cur.execute("""SELECT sqlid,jfull FROM jdata WHERE sqlid IN (SELECT sqlid FROM jdata_meta WHERE sqlid >= %d and sqlid < %d and cat = 'M') """ % ((i-1)*10000,i*10000))
	rows = cur.fetchall()

	for row in rows:
		doc_count = doc_count + 1
		tokens = set()
		
		ts = jieba.analyse.extract_tags(row[1], topK=100, withWeight=False, allowPOS=('n','v','a')) 
		tokens = tokens.union(set(ts))

		rs = jieba.analyse.textrank(row[1], topK=100, withWeight=False, allowPOS=('n','v','a')) 
		tokens = tokens.union(set(rs))

		for w in tokens:
			df[w] = df.get(w,0.0) + 1.0
	print(i,len(df.keys()))

count = 0
words = sorted(list(df.keys()))
f = open("law_idf.txt.1",'w')
for t in words:
	# if re.match("^[\u4e00-\u9fa5]",t):
	f.write("%s %f\n" % (t,math.log(float(doc_count)/df[w]) ) )
	count = count + 1
print(count)
