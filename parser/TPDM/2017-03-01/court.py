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
    for i in range(0):
        lines = fread.readline()
    content = fread.read()
    court_place = content.find('法院')
    court = content[0:court_place+2]
    print (court)
