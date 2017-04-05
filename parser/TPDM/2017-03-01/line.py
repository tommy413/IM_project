fread = open('0.txt' ,'r')
for i in range(4):
    content = fread.readline()
    if content[0:6] == '【裁判字號】':
        content = content.replace('【裁判字號】','').replace('\n','')
        print (content)
    if content[0:6] == '【裁判日期】':
        content = content.replace('【裁判日期】','').replace('\n','')
        print (content)
    if content[0:6] == '【裁判案由】':
        content = content.replace('【裁判案由】','').replace('\n','')
        print (content)
