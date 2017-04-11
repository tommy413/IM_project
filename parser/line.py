import os

parserList = os.listdir('.')
parserList.remove('get_paper.py')
parserList.remove('line.py')
parserList.remove('main.py')
parserList.remove('reason.py')
#forMAC
parserList.remove('.DS_Store')


for f in parserList:
    courtList = os.listdir(f)
    #forMAC
    courtList.remove('.DS_Store')
    for g in courtList:
        path = f+'/'+g
        files = os.listdir(path)
        #forMAC
        files.remove('.DS_Store')


        for f in files:
            print (f)
            fread = open(path+'/'+f ,'r')
            for i in range(4):
                content = fread.readline()
                if content.find('法院') > 0:
                    content = content[:content.find('法院')+2]
                    print (content)
                if content[0:6] == '【裁判字號】':
                    content = content.replace('【裁判字號】','').replace('\n','')
                    print (content)
                if content[0:6] == '【裁判日期】':
                    content = content.replace('【裁判日期】','').replace('\n','')
                    print (content)
                if content[0:6] == '【裁判案由】':
                    content = content.replace('【裁判案由】','').replace('\n','')
                    print (content)
