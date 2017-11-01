
# coding: utf-8

# In[12]:


import numpy as np
import re
import psycopg2
import pandas as pd
import jieba
import jieba.analyse
import jieba.posseg as pseg


# In[386]:
def update_pair(sqlid,conn):

    cur = conn.cursor()

    cur.execute("""SELECT sqlid,main FROM jdata_features WHERE sqlid = %d;""" % sqlid)
    rows = cur.fetchall()


    # In[387]:



    # sample_df.head(50)


    # In[377]:


    for row in rows:
        if (row[1][:3] == "原判決") :
            continue;
        #print(row[0])
        test_str = row[1]
        sentences = re.split('。',test_str)
        sentences = [t for t in sentences if t != "" ]

        no_guilty_words = ["無罪","駁回","撤銷","不受理","免訴"]
        guilty_words = ["月","年","元","天","勞務","徒刑","褫奪公權"]

        guilty_sens = []
        sens_flag = 0
        for sens in sentences :
            sens_flag = 0
            for w in guilty_words :
                if (sens.find(w) >= 0 and sens_flag == 0) :
                    guilty_sens.append(sens)
                    sens_flag = 1
        # print(guilty_sens)

        laws_words_pattern = "從事.+|無故.+|未.+|以.+之事|連續.+|意圖.+|行使.+|犯.+[罪|規定]|違反.+[罪|規定]|依.+[法|條例|罪|規定]|[販賣|持有]第[一二三四、]{+}級毒品"
        judgements_words_pattern = "處.+|應.+|緩刑.+"
        total_words_pattern = "均.+"
        add_law_pattern = "又.+"
        final_judgement_pattern = "應執行.+"

        guilty_pairs = []
        law_str = ""
        for sens in guilty_sens:
            last_law = law_str
            law_str = ""
            judgement_strs = []
            total_flag = 0
            add_flag = 0
            sens_semicolon = re.split('；|，',sens)
            last_sen = 0
            for semi_sens in sens_semicolon :
        #         print(semi_sens)
                if (len(re.findall(laws_words_pattern,semi_sens)) > 0) :
                    total_flag = 0
                    add_flag = 0
                    last_sen = 1
                    law_str = re.findall(laws_words_pattern,semi_sens)[0]
                elif (len(re.findall(judgements_words_pattern,semi_sens)) > 0):
                    total_flag = 0
                    add_flag = 0
                    last_sen = 2
                    count = len(re.findall("、",semi_sens))
                    judgement_strs = judgement_strs + [re.findall(judgements_words_pattern,semi_sens)[0] for i in range(0,count+1)]
                elif (len(re.findall(total_words_pattern,semi_sens)) > 0):
                    total_flag = 1
                    add_flag = 0
                    last_sen = 2
                    judgement_strs = [ t + "," + re.findall(total_words_pattern,semi_sens)[0] for t in judgement_strs]
                elif (len(re.findall(add_law_pattern,semi_sens)) > 0):
                    total_flag = 0
                    add_flag = 1
                    last_sen = 1
                    if law_str != "" :
                        law_str = law_str + "," + semi_sens
                    else :
                        law_str = semi_sens[1:]
                else :
                    if total_flag == 1 :
                        judgement_strs = [ t + "," + semi_sens for t in judgement_strs]
                    elif add_flag == 1 :
                        law_str = law_str + "," + semi_sens
                    else :
                        if last_sen == 2 :
                            if len(judgement_strs) > 0 :
                                judgement_strs[-1] = judgement_strs[-1] + "," + semi_sens
                        elif last_sen == 1 :
                            if law_str != "" :
                                law_str = law_str + "," + semi_sens
                            else :
                                law_str = semi_sens[1:]
                            
            for j_str in judgement_strs :
                if (law_str == "") :
                    law_str = last_law
                guilty_pairs.append((law_str,j_str))

        guilty_pairs = [t for t in guilty_pairs if t != "" ]
        # print(guilty_pairs)

        no_guilty_sens = []
        sens_flag = 0
        for sens in sentences :
            sens_flag = 0
            for w in no_guilty_words :
                if (sens.find(w) >= 0 and sens_flag == 0) :
                    no_guilty_sens.append(sens)
                    sens_flag = 1
        # print(no_guilty_sens)

        laws_words_pattern = "從事.+|無故.+|未.+|以.+之事|連續.+|意圖.+|行使.+|犯.+[罪|規定]|違反.+[罪|規定]|依.+[法|條例|罪|規定]|[販賣|持有]第[一二三四、]{+}級毒品"
        judgements_words_pattern = "無罪|駁回|撤銷|不受理|免訴"
        add_law_pattern = "又.+"

        no_guilty_pairs = []
        law_str = ""
        for sens in no_guilty_sens:
            last_law = law_str
            law_str = ""
            judgement_strs = []
            add_flag = 0
            sens_semicolon = re.split('；|，',sens)
            last_sen = 0
            for semi_sens in sens_semicolon :
        #         print(semi_sens)
                if (len(re.findall(laws_words_pattern,semi_sens)) > 0) :
                    add_flag = 0
                    last_sen = 1
                    law_str = re.findall(laws_words_pattern,semi_sens)[0]
                elif (len(re.findall(judgements_words_pattern,semi_sens)) > 0):
                    add_flag = 0
                    last_sen = 2
                    count = len(re.findall("、",semi_sens))
                    judgement_strs = judgement_strs + [re.findall(judgements_words_pattern,semi_sens)[0] for i in range(0,count+1)]
                elif (len(re.findall(add_law_pattern,semi_sens)) > 0):
                    add_flag = 1
                    last_sen = 1
                    if law_str != "" :
                        law_str = law_str + "," + semi_sens
                    else :
                        law_str = semi_sens[1:]
                else :
                    if add_flag == 1 :
                        law_str = law_str + "," + semi_sens
                    else :
                        if last_sen == 2 :
                            if len(judgement_strs) > 0 :
                                judgement_strs[-1] = judgement_strs[-1] + "," + semi_sens
                        elif last_sen == 1 :
                            if law_str != "" :
                                law_str = law_str + "," + semi_sens
                            else :
                                law_str = semi_sens[1:]
                            
            for j_str in judgement_strs :
                if (law_str == "") :
                    law_str = last_law
                no_guilty_pairs.append((law_str,j_str))

        no_guilty_pairs = [t for t in no_guilty_pairs if t != "" ]
        # print(no_guilty_pairs)

        cur.execute(""" DELETE FROM law_judgement WHERE Sqlid = %s ;""" % (row[0]))
        conn.commit()
        for t in guilty_pairs:
            cur.execute("""INSERT INTO law_judgement (sqlid,reason,judgement)VALUES (%s,'%s','%s');""" % (row[0],t[0].replace('\'',"\'\'"),t[1].replace('\'',"\'\'")))
            conn.commit()
        for t in no_guilty_pairs:
            cur.execute("""INSERT INTO law_judgement (sqlid,reason,judgement)VALUES (%s,'%s','%s');""" % (row[0],t[0].replace('\'',"\'\'"),t[1].replace('\'',"\'\'")))
            conn.commit()

    return

