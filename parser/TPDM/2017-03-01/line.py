import os

files = []
removeList = []
for f in os.listdir('.'):
    if os.path.isfile(f):
        files.append(f)
for i in range(len(files)):
    f = files[i]
    if f.find('.txt') < 0:
        removeList.append(f)
for f in removeList:
    files.remove(f)


for f in files:
    print (f)
    fread = open(f ,'r')
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
