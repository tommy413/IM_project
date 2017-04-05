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
    fread = open(f ,'r')
    for i in range(5):
        lines = fread.readline()
    content = fread.read()
    main = content.find('主文')
    fact = content.find('事實')
    reason = content.find('理由')
    mainContent = ''
    if (reason-fact) == 3:
        if content[fact-2:fact] == '犯罪':
            mainContent = content[main+2:fact-2]
        else:
            mainContent = content[main+2:fact]
    elif reason > fact:
        if fact != -1:
            mainContent = content[main+2:fact]
        else:
            mainContent = content[main+2:reason]
    elif fact > reason:
        if reason != -1:
            mainContent = content[main+2:reason]
        else:
            mainContent = content[main+2:fact]
    print (f)
    print (mainContent)
