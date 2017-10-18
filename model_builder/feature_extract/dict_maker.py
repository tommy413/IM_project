# coding: utf-8
import numpy as np
import psycopg2
import pandas as pd
import jieba
import jieba.analyse
import jieba.posseg as pseg
import re
jieba.load_userdict("dict.txt.big") 

conn = psycopg2.connect(database="law1", user="datac1", password="datac15543", host="localhost", port="5432")
print("Opened database successfully")

cur = conn.cursor()
tokens = set()

for i in range(1,1252):
	cur.execute("""SELECT sqlid,jfull FROM jdata where sqlid >= %d and sqlid < %d""" % ((i-1)*1000,i*1000))
	rows = cur.fetchall()

	for row in rows:
		#tokens = tokens.union(jieba.cut(row[1],cut_all=True))
		tokens = tokens.union(jieba.cut_for_search(row[1]))
	print(i,len(tokens))

tokens = sorted(list(tokens))
f = open("law_dict.txt.1",'w')
count = 1
for t in tokens:
	if re.match("^[\u4e00-\u9fa5]",t):
		f.write("%d %s\n" % (count,t))
		count = count + 1
print(count)