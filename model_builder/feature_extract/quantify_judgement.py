
# coding: utf-8

# In[4]:


import numpy as np
import re
import psycopg2
import pandas as pd
import jieba
import jieba.analyse


# In[34]:


chs_arabic_map = {u'零':0, u'一':1, u'二':2, u'三':3, u'四':4,
        u'五':5, u'六':6, u'七':7, u'八':8, u'九':9,
        u'十':10, u'百':100, u'千':10 ** 3, u'万':10 ** 4,
        u'〇':0, u'壹':1, u'貳':2, u'參':3, u'肆':4,
        u'伍':5, u'陸':6, u'柒':7, u'捌':8, u'玖':9,
        u'拾':10, u'佰':100, u'仟':10 ** 3, u'萬':10 ** 4,
        u'亿':10 ** 8, u'億':10 ** 8, u'幺': 1,
        u'０':0, u'１':1, u'２':2, u'３':3, u'４':4,
        u'５':5, u'６':6, u'７':7, u'８':8, u'９':9,u'廿':20,u'卅':30}

def convertChineseDigitsToArabic(chinese_digits, encoding="utf-8"):
#     if isinstance (chinese_digits, str):
#         chinese_digits = chinese_digits.decode(encoding)

    result  = 0
    tmp     = 0
    hnd_mln = 0
    for count in range(len(chinese_digits)):
        curr_char  = chinese_digits[count]
        curr_digit = chs_arabic_map.get(curr_char, None)
        # meet 「亿」 or 「億」
        if curr_digit == 10 ** 8:
            result  = result + tmp
            result  = result * curr_digit
            # get result before 「亿」 and store it into hnd_mln
            # reset `result`
            hnd_mln = hnd_mln * 10 ** 8 + result
            result  = 0
            tmp     = 0
        # meet 「万」 or 「萬」
        elif curr_digit == 10 ** 4:
            result = result + tmp
            result = result * curr_digit
            tmp    = 0
        # meet 「十」, 「百」, 「千」 or their traditional version
        elif curr_digit >= 10:
            tmp    = 1 if tmp == 0 else tmp
            result = result + curr_digit * tmp
            tmp    = 0
        # meet single digit
        elif curr_digit is not None:
            tmp = tmp * 10 + curr_digit
        else:
            return result
    result = result + tmp
    result = result + hnd_mln
    return result


# In[5]:


conn = psycopg2.connect(database="law1", user="datac1", password="datac15543", host="ci.lu.im.ntu.edu.tw", port="5432")
print ("Opened database successfully")

cur = conn.cursor()


# In[6]:


cur.execute("""SELECT sqlid,judgement FROM law_judgement limit 57""")
rows = cur.fetchall()


# In[7]:


sample_df = pd.DataFrame(rows)
sample_df.head(57)


# In[36]:


test_str = sample_df[1][50]
print(test_str)


# In[37]:


num_judgements_words_pattern = "有期徒刑.{1,8}[年|月]"
est_judgements_words_pattern = "無期徒刑|死刑"
no_guilty_words_pattern = "無罪|駁回|撤銷|不受理|免訴"


# In[38]:


nums = re.findall(num_judgements_words_pattern,test_str)
ests = re.findall(est_judgements_words_pattern,test_str)
no_guiltys = re.findall(no_guilty_words_pattern,test_str)

print(nums)
print(ests)
print(no_guiltys)


# In[41]:


numbers = []
if (len(nums) > 0):
    num_str = nums[-1].replace("有期徒刑","")
    years = ""
    months = ""
    
    if (num_str.find("年") > 0):
        years = num_str.split("年")[0]
        num_str = num_str.split("年")[1]
    if (num_str.find("月") > 0):
        months = num_str.split("月")[0]
    
    res = convertChineseDigitsToArabic(years) * 12 + convertChineseDigitsToArabic(months)
    print(res)
    
    numbers.append(res)


# In[42]:


if (len(ests) > 0):
    for s in ests :
        if (s.find("無期徒刑")):
            numbers.append(50*12)
        if (s.find("死刑")):
            numbers.append(100*12)


# In[43]:


for s in no_guiltys:
    numbers.append(0)


# In[45]:


print(np.array(numbers).mean())

