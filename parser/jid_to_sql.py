import sys
import time
import os
import datetime
from datetime import timedelta
import psycopg2

conn = psycopg2.connect(database="law1", user="datac1", password="datac15543", host="ci.lu.im.ntu.edu.tw", port="5432")
conn.set_session(autocommit=True)

def id_convert(conn,begindate,enddate):
	db = conn.cursor()
	for i in range(int((enddate-begindate).days)+1):
		idmap = dict()
		single_day = begindate+timedelta(i)
		day_str = str(single_day.date().strftime('%Y%m%d'))

		query = "SELECT jid from jdata where jid Like '%s' FOR UPDATE" % ("%M,%"+day_str+"%")
		db.execute(query)
		print(query)
		rows = db.fetchall()

		for row in rows:
			jid = row[0]
			id_list = row[0].split(',')
			num = idmap.get(id_list[0],0)
			idmap[id_list[0]] = num + 1
			num_str = str(num).zfill(3)
			sqlid = id_list[0]+id_list[4]+num_str
			
			query = "UPDATE jdata SET sqlid = \'%s\' where jid = '%s'" % (sqlid,jid)
			db.execute(query)
			print(query)
			conn.commit()

		#check
		# query = "SELECT jid,sqlid from jdata where jid Like '%s'" % ("%M,%"+day_str+"%")
		# print(query)
		# db.execute(query)
		# rows = db.fetchall()

		# f = open("sqlid.txt",'a')
		# for row in rows:
		# 	print(row[0]+","+row[1]+"\n")
		# f.close()
	return

begindate = datetime.datetime(int(sys.argv[1][:4]),int(sys.argv[1][4:6]),int(sys.argv[1][6:]))
enddate = datetime.datetime(int(sys.argv[2][:4]),int(sys.argv[2][4:6]),int(sys.argv[2][6:]))
id_convert(conn,begindate,enddate)


