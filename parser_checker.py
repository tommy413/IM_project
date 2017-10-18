import psycopg2
import re
import sys
import datetime
from datetime import timedelta

def namecheck(test):
	testes = test.split("####")
	pattern = '^[\u4e00-\u9fa5]{2,5}|^[a-zA-Z\' ]+'
	matches = [re.match(pattern,t) for t in testes]
	matches = [t for t in matches if t != ""]
	return len(testes) == len(matches)

def emptycheck(test):
	testes = test.replace("####","")
	if (testes == "" or testes == "None") :
		return False
	return True

conn = psycopg2.connect(database="law1", user="datac1", password="datac15543", host="127.0.0.1", port="5432")
print ("Opened database successfully")

cur = conn.cursor()

# start = datetime.datetime(int(sys.argv[1][:4]),int(sys.argv[1][4:6]),int(sys.argv[1][6:]))
# end = datetime.datetime(int(sys.argv[2][:4]),int(sys.argv[2][4:6]),int(sys.argv[2][6:]))


# fCourt = open('court.txt', 'r')
# courtStr = fCourt.read()
# courtList = courtStr.split('\n')
# courtList = ["TPC","TPS","TPH","IPC","TCH","TNH","KSH","HLH","TPD","SLD","PCD","ILD","KLD","TYD","SCD","LD","TCD","CHD","NTD","ULD","CYD","TND","KSD","CTD","HLD","TTD","PTD","PHD","KMH","KMD","LCD","KSY"]
columnList = ["sqlid","main","reasonfact","claim","judge","accuser","agent","defendant","advocate","helper"]
count = 0;
success = 0;

# for i in courtList:
# 	for y in range(int((end-start).days)+1):
# 		theDay = start + timedelta(y)
# 		datestr = str(theDay.date().strftime('%Y-%m-%d'))
for i in range(1,1252):

	cur.execute("""SELECT sqlid,main,reasonfact,judge,defendant,accuser,claim,agent,advocate,helper FROM jdata_features WHERE sqlid IN (SELECT sqlid FROM jdata_meta WHERE cat = 'M' and sqlid >= %d and sqlid < %d) """ % ((i-1)*1000,i*1000))
	rows = cur.fetchall()
# print(i,datestr,len(rows))

	for row in rows:
		print(row[0])
		# if emptycheck(row[9]) == False:
		# 	continue;
		# cur.execute("""SELECT jfull FROM jdata WHERE sqlid = '%s' """ % row[0])
		# jfull = cur.fetchall()
		count = count + 1
		flag = True
		for i in range(1,5):
			if emptycheck(row[i]) == False:
				flag = False
				# print(str(row[0]) + " Empty : " + columnList[i] + " : " + row[i])
		for i in range(3,10):
			if namecheck(row[i]) == False:
				flag = False
			
		cur.execute("""SELECT jid FROM jdata WHERE sqlid = '%s' """ % row[0])
		jid = cur.fetchall()
		if flag == True:
			# print(str(jid[0]) + " Done : " + str(row[0]))
			cur.execute("""UPDATE jdata_meta SET parser_done = '1' WHERE sqlid = '%s' """ % row[0])
			conn.commit()
			success = success + 1
			print(str(jid[0]) + " Success : " + str(row[0]))
		else :
			cur.execute("""UPDATE jdata_meta SET parser_done = '0' WHERE sqlid = '%s' """ % row[0])
			conn.commit()
			print(str(jid[0]) + " Fail : " + str(row[0]))
print(count)
print(success)
print(success/count)