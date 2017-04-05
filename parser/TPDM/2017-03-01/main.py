fread = open('37.txt' ,'r')
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
print (mainContent)
