
# coding: utf-8

# In[11]:


# coding: utf-8
import numpy as np
import psycopg2
import sys,os
import pandas as pd
import jieba
import jieba.analyse
import jieba.posseg as pseg
import re
import pickle as pkl
import word2vec
from sklearn.feature_extraction.text import  TfidfVectorizer
from sklearn.cluster import KMeans
jieba.load_userdict("dict.txt.big") 


# In[7]:


conn = psycopg2.connect(database="law1", user="datac1", password="datac15543", host="localhost", port="5432")
print("Opened database successfully")

cur = conn.cursor()

begin = int(sys.argv[1])
end = int(sys.argv[2])
# model_name = sys.argv[3]
WORDVEC_DIM = int(sys.argv[3])
model_text = "%d_%d_corpus.txt" % (begin,end)
# In[36]:

if not os.path.isfile(model_text):
    f = open(model_text,'w')
    for i in range(begin,end):
        cur.execute("""SELECT jfull FROM jdata where sqlid IN (Select sqlid FROM jdata_meta WHERE sqlid >= %d and sqlid < %d and cat = 'M') """ % ((i-1)*10000,i*10000))
        rows = cur.fetchall()

        for row in rows:
            #ix2Squid[len(allText)] = row[0]
            tokens = [t for t in jieba.lcut(row[0]) if re.match("^[\u4e00-\u9fa5]",t)]
            for w in tokens:
                f.write("%s " % str(w))
            f.write("\n")
            
        print(i)

#word2vec.word2phrase(model_text, model_phrase, verbose=True)


# In[45]:


MIN_COUNT = 5
WINDOW = 3
NEGATIVE_SAMPLES = 5
# ITERATIONS = 0
# MODEL = 1
LEARNING_RATE = 0.0025


# In[46]:


model = word2vec.word2vec(
        train=model_text,
        output="law_word2vec_%d.bin" % WORDVEC_DIM,
        size=WORDVEC_DIM,
        min_count=MIN_COUNT,
        window=WINDOW,
        negative=NEGATIVE_SAMPLES,
        alpha=LEARNING_RATE,
        verbose=True
        )


# In[47]:

print(model.vectors.shape)

#cluster = word2vec.word2clusters(model_text, 'law_clusters_%d.txt'% WORDVEC_DIM, 100, verbose=True)
