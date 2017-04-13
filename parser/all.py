import os
import re

def getLine(lineContent):
    index = ''
    if lineContent.find('法院') > 0:
        pattern = '\D\d+號$'
        match = re.findall(pattern,lineContent)
        lineContent = lineContent[:lineContent.find('法院')+2]
        print (lineContent)
        index = (match[0])[1:]
    elif lineContent[0:6] == '【裁判字號】':
        lineContent = lineContent.replace('【裁判字號】','').replace('\n','')
        print (lineContent)
    elif lineContent[0:6] == '【裁判日期】':
        lineContent = lineContent.replace('【裁判日期】','').replace('\n','')
        print (lineContent)
    elif lineContent[0:6] == '【裁判案由】':
        lineContent = lineContent.replace('【裁判案由】','').replace('\n','')
        print (lineContent)
    return index



def getMain(mainContent):
    main = mainContent.find('主文')
    mainContent = mainContent[main:]
    fact = mainContent.find('事實')
    reason = mainContent.find('理由')
    main = ''
    if (reason-fact) == 3:
        if mainContent[fact-2:fact] == '犯罪':
            main = mainContent[2:fact-2]
            print (main)
            mainContent = mainContent[reason:]
        else:
            main = mainContent[2:fact]
            print (main)
            mainContent = mainContent[reason:]
    elif reason > fact:
        if fact != -1:
            main = mainContent[2:fact]
            print (main)
            mainContent = mainContent[fact:]
        else:
            main = mainContent[2:reason]
            print (main)
            mainContent = mainContent[reason:]
    elif fact > reason:
        if reason != -1:
            main = mainContent[2:reason]
            print (main)
            mainContent = mainContent[reason:]
        else:
            main = mainContent[2:fact]
            print (main)
            mainContent = mainContent[fact:]
    return mainContent

def getReasonJudge(reasonjudgeContent):
    pattern = '中華民國\d+年\d+月\d+日.*第.+庭.*法官.+?原本無'
    match = re.findall(pattern,reasonjudgeContent)
    #reason
    reasonContent = ''
    reasonList = []
    if len(match) > 0:
        reasonEnd = reasonjudgeContent.find(match[0])
        reasonContent = content[:reasonEnd]
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


parserList = os.listdir('.')
parserList.remove('get_paper.py')
parserList.remove('line.py')
parserList.remove('main.py')
parserList.remove('reason_judge.py')
parserList.remove('all.py')
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
            peopleIndex = ''
            for i in range(4):
                content = fread.readline()
                #getLine
                if i == 0:
                    peopleIndex = getLine(content)
                else:
                    getLine(content)
#            print (peopleIndex)
            content = fread.read()
            #getPeople
            #content = getPeople(content,peopleIndex)
            #getMain
            content = getMain(content)
            #getReasonJudge
            getReasonJudge(content)
            fread.close()
