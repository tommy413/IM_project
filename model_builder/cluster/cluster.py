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
import random
import pickle as pkl
from sklearn.feature_extraction.text import  TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.decomposition import TruncatedSVD
jieba.load_userdict("../dict.txt.big") 

from quantify_judgement import getGuiltyNum


# In[2]:


def jieba_tokenize(text):
    return  [t for t in jieba.lcut(text) if re.match("^[\u4e00-\u9fa5]",t)] 


# In[76]:


tfidf_vectorizer = pkl.load(open("../tfidf/tfidf_vectorizer.pkl" ,'rb'))
# ix2Squid = pkl.load(open("../dataset/ix2Squid.pkl" ,'rb'))

conn = psycopg2.connect(database="law1", user="datac1", password="datac15543", host="localhost", port="5432")
print("Opened database successfully")
cur = conn.cursor()


# In[77]:


testReasonFact = []
rawData = []
for i in range(1252,0,-1):
    cur.execute("""SELECT sqlid,main,reasonfact FROM jdata_features WHERE sqlid IN (SELECT sqlid FROM jdata_meta WHERE cat = 'M' and parser_done = 1 and sqlid >= %d and sqlid < %d) """ % ((i-1)*10000,i*10000))
    rows = cur.fetchall()
    for row in rows:
        #print(row)
        guiltyNum = getGuiltyNum(row[0],conn)
        if not np.isnan(guiltyNum) :
            testReasonFact.append(row[1])
            rawData.append([row[0],getGuiltyNum(row[0],conn)])
        #sqlidRsts.append([row[0],random.randint(0,1200)])
    print(i,len(testReasonFact))


# In[31]:


tfidf_test_matrix = tfidf_vectorizer.transform(testReasonFact)

print(tfidf_test_matrix.shape)

#print(sqlidRsts)


# In[32]:


clf = TruncatedSVD(n_components=2)

#pca = PCA(n_components=2)
pca_matrix = clf.fit_transform(tfidf_test_matrix)

#print(pca_matrix[:,0])


# In[71]:


sqlidRsts = [[t[0],t[1]] for t in rawData]
print(len(sqlidRsts))
for k in range(3,13):
    #print("k = %d" % k)
    
    #fig = plt.figure()
    
    # title = "Scatter for k=%d" % k
    # colors =  plt.cm.tab20( (20/k * np.arange(k)).astype(int) )
    
    # patch = []
    # for z in range(0,k):
    #     patch.append(mpatches.Patch(color=colors[z], label = z))
    # plt.legend(handles=patch)
    # plt.title(title)

    km = KMeans(n_clusters=k, init='k-means++', max_iter=300, n_init=5,verbose=0)

    result = km.fit_predict(tfidf_test_matrix)
    
    # plt.scatter(pca_matrix[:,0],pca_matrix[:,1],c=colors)
    # #plt.show()
    # fig.savefig("img/PCA_%d.png" % k,bbox_inches='tight')
    print(len(result))
    for i in range(0,len(result)):
        sqlidRsts[i].append(result[i])


# In[72]:


NPsqlidRsts = [t for t in sqlidRsts if not np.isnan(t[1])]
#print(NPsqlidRsts)

# In[74]:

f = open("cluster_rst.txt",'w')

for k in range(3,13):
    f.write("k = %d\n" % k)
    f.write("Label\tMean\tSTD\tCount\n")
    rst = np.array([t[k-1] for t in NPsqlidRsts])
    for l in range(0,k):
        rstL = np.array( [ NPsqlidRsts[i][1] for i in range(0,len(rst)) if rst[i] == l])
        if len(rstL) > 0 :
            f.write("%d\t%f\t%f\t%d\n" % (l,rstL.mean(),rstL.std(),len(rstL)))
        else :
            f.write("%d\t%f\t%f\t%d\n" % (l,-1,-1,len(rstL)))
    f.write("\n")

