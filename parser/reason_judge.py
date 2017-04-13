import os
import re

parserList = os.listdir('.')
parserList.remove('get_paper.py')
parserList.remove('line.py')
parserList.remove('main.py')
parserList.remove('reason_judge.py')
parserList.remove('all.py')

parserList.remove('accu_defe.py')

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
            fread = open(path+'/'+f ,'r')
            content = fread.read()
            main = content.find('主文')
            content = content[main:]
            fact = content.find('事實')
            reason = content.find('理由')
            reasontype = -1
            if (reason-fact) == 3:
                content = content[reason:]
                reasontype = 1
            elif reason > fact:
                if fact != -1:
                    content = content[fact:]
                    reasontype = 2
                else:
                    content = content[reason:]
                    reasontype = 3
            elif fact > reason:
                if reason != -1:
                    content = content[reason:]
                    reasontype = 3
                else:
                    content = content[fact:]
                    reasontype = 2
            pattern = '中華民國\d+年\d+月\d+日.*第.+庭.*法官.+?原本無'
            match = re.findall(pattern,content)
            print (f)
            #reason
            reasonContent = ''
            reasonList = []
            if len(match) > 0:
                reasonEnd = content.find(match[0])
                reasonContent = content[:reasonEnd]
                '''
                if reasontype == 1:
                    reasonContent = content[:reasonEnd]
                elif reasontype == 2:
                    reasonContent = content[:reasonEnd]
                elif reasontype == 3:
                    reasonContent = content[:reasonEnd]
'''
                getreasonList = '(實一、|由一、|。二、|。三、|。四、|。五、|。六、|。七、|。八、|。九、|。十、)'
                numList = re.findall(getreasonList,reasonContent)
                for i in range(len(numList)-1):
                    start = reasonContent.find(numList[i])+1
                    end = reasonContent.find(numList[i+1])+1
                    reasonList.append(reasonContent[start:end])
                    reasonContent = reasonContent[end-1:]
                start = reasonContent.find(numList[len(numList)-1])+1
                reasonList.append(reasonContent[start:])
                print (reasonList)
            else:
                print (reasonList)
            #judge
            judgeList = []
            if len(match) > 0:
                judgeContent = match[0]
                judge = judgeContent.find('法官')
                if judgeContent.find('以上') >= 0:
                    judgeEnd = judgeContent.find('以上')
                else:
                    judgeEnd = judgeContent.find('上')
                judgeContent = judgeContent[judge+2:judgeEnd]
                judgeList = judgeContent.split('法官')
                print (judgeList)
            else:
                print (judgeList)
