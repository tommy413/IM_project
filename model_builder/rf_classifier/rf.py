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
import sys,os
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


def jieba_tokenize(text):
    return  [t for t in jieba.lcut(text) if re.match("^[\u4e00-\u9fa5]",t)] 

def split_data(X,Y,split_ratio):
    indices = np.arange(X.shape[0])  
    np.random.shuffle(indices) 
    X = np.array(X)
    Y = np.array(Y)

    X_data = X[indices]
    Y_data = Y[indices]

    num_validation_sample = int(split_ratio * X_data.shape[0] )

    X_train = X_data[num_validation_sample:]
    Y_train = Y_data[num_validation_sample:]

    X_val = X_data[:num_validation_sample]
    Y_val = Y_data[:num_validation_sample]

    return (X_train,Y_train),(X_val,Y_val)

def RMSE(pred,est):
    se = 0.0
    for i in range(0,len(pred)):
        se = se + (pred[i]-est[i]) * (pred[i]-est[i])
    return np.sqrt(se/len(pred))

def acc(pred,est):
    correct = 0
    for i in range(0,len(pred)):
        if pred[i] == est[i] :
            correct = correct + 1
    return float(correct)/len(pred)
# In[76]:

## remember change version if change dataset
version = 1
tfidf_vectorizer_name = "tfidf_vectorizer"

tfidf_vectorizer = pkl.load(open("../tfidf/%s.pkl" % tfidf_vectorizer_name,'rb'))
# ix2Squid = pkl.load(open("../dataset/ix2Squid.pkl" ,'rb'))

conn = psycopg2.connect(database="law1", user="datac1", password="datac15543", host="localhost", port="5432")
print("Opened database successfully")
cur = conn.cursor()


# parameters
begin = int(sys.argv[1])
end = int(sys.argv[2])
n_components = int(sys.argv[3])
n_estimators = int(sys.argv[4])
feature_matrix_name = "%d_%d_tfidf_%s_%d.pkl" % (begin,end,tfidf_vectorizer_name,version)

if not os.path.isfile(feature_matrix_name):
    testReasonFact = []
    label = []
    for i in range(begin,end):
        cur.execute("""SELECT sqlid,reasonfact FROM jdata_features WHERE sqlid IN (SELECT sqlid FROM jdata_meta WHERE cat = 'M' and parser_done = 1 and sqlid >= %d and sqlid < %d) """ % ((i-1)*10000,i*10000))
        rows = cur.fetchall()
        for row in rows:
            #print(row)
            guiltyNum = getGuiltyNum(row[0],conn)
            if not np.isnan(guiltyNum) :
                testReasonFact.append(row[1])
                label.append(int(guiltyNum))
            #sqlidRsts.append([row[0],random.randint(0,1200)])
        print(i,len(testReasonFact))

    feature_matrix = tfidf_vectorizer.transform(testReasonFact)
    pkl.dump(feature_matrix, open("%s.pkl" % (feature_matrix_name) ,'wb'), pkl.HIGHEST_PROTOCOL)

else :
    feature_matrix = pkl.load(open(feature_matrix_name ,'rb'))

print(feature_matrix.shape)

#print(sqlidRsts)


# In[32]:


svd = TruncatedSVD(n_components=n_components)

#pca = PCA(n_components=2)
feature_matrix = svd.fit_transform(feature_matrix)



print(feature_matrix.shape)
#print(pca_matrix[:,0])

(X_train,Y_train),(X_val,Y_val) = split_data(feature_matrix,label,0.2)

print("train")
print("mean : %f" % Y_train.mean())
print("std : %f" % Y_train.std())
print("median : %f" % Y_train.median())
print("max : %f" % Y_train.max())
print("min : %f" % Y_train.min())
print("val")
print("mean : %f" % Y_val.mean())
print("std : %f" % Y_val.std())
print("median : %f" % Y_val.median())
print("max : %f" % Y_val.max())
print("min : %f" % Y_val.min())
# print(X_train.shape)
# print(X_val.shape)

# In[72]:

rf = RandomForestClassifier(n_estimators = n_estimators, max_depth = 10,verbose = 1)

rf.fit(X_train,Y_train)

print(rf.feature_importances_)

pkl.dump(svd, open("svd_%d_%d_%d_%d.pkl" % (begin,end,n_components,n_estimators) ,'wb'), pkl.HIGHEST_PROTOCOL)
pkl.dump(rf, open("rf_%d_%d_%d_%d.pkl" % (begin,end,n_components,n_estimators) ,'wb'), pkl.HIGHEST_PROTOCOL)

rst = rf.predict(X_val)

f = open("rf_rst.txt",'a')

rmse = RMSE(rst,Y_val)

acc = acc(rst,Y_val)

print(rmse,acc)

f.write("%d,%d,%d,%d\t%f\t%f\n" % (begin,end,n_components,n_estimators,rmse,acc))
