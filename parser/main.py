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
            fread = open(path+'/'+f ,'r')
            for i in range(5):
                lines = fread.readline()
            content = fread.read()
            main = content.find('主文')
            content = content[main:]
            fact = content.find('事實')
            reason = content.find('理由')
            mainContent = ''
            if (reason-fact) == 3:
                if content[fact-2:fact] == '犯罪':
                    mainContent = content[2:fact-2]
                else:
                    mainContent = content[2:fact]
            elif reason > fact:
                if fact != -1:
                    mainContent = content[2:fact]
                else:
                    mainContent = content[2:reason]
            elif fact > reason:
                if reason != -1:
                    mainContent = content[2:reason]
                else:
                    mainContent = content[2:fact]
            print (f)
            print (mainContent)
