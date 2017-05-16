# -*- coding: utf8 -*-
from BeautifulSoup import BeautifulSoup
import sys
import time
import os
import datetime
from datetime import timedelta
import psycopg2
import logging

conn = psycopg2.connect(database="law1", user="datac1", password="datac15543", host="ci.lu.im.ntu.edu.tw", port="5432")

def parse(paperid,html):
	info = ""
	paper = ""
	try:
		soup = BeautifulSoup(doc)
		paper = str(soup.title.string)+"\r\n"
		
		body = soup.body
		if 'NoneType' not in str(type(soup.body)):
			tables = body.findAll("table")
			flag = 0
			for table in tables:
				for tr in table.findAll("tr"):
					for td in tr.findAll("td"):
						if 'NoneType' not in str(type(td.pre)) and flag == 0:
							for tr_out in table.findAll("tr"):
								if 'NoneType' not in str(type(tr_out.td.span)):
									info = str(tr_out.td.span.string).decode("utf8")
									info = info.replace("&nbsp;","").replace("None","")
									if u"筆 / 現在第" not in info:
										paper = paper + info.encode("utf8")+"\r\n"
								if "裁判全文" in info.encode("utf8"):
									break
							paper = paper + str(td.pre.string).replace('	','').replace(' ','').replace(' ','').replace('\t','').replace('　','')
							flag = 1
	except Exception as e:
		logging.error("%s_parse_error_%s\r\n" % (paperid,e) )
		return "error"
	return paper

def DB_Output(conn,paperid,paper):
	
	db = conn.cursor()
	db.execute("SELECT COUNT(id) from raw_html where id = \'%s\'" % (paperid))
	count = int(db.fetchall()[0][0])
	if count == 0 :
		query = "INSERT INTO HTMLDATA (ID,CONTENT) VALUES (\'%s\' , \'%s\')" % (paperid,paper)
	else :
		query = "UPDATE HTMLDATA SET CONTENT = \'%s\' " % (paper)
		
	try:
		db.execute(query)
		conn.commit()
	except Exception as e:
		logging.error("%s_commit_error_%s\r\n" % (paperid,e))
		return True
	else:
		if count == 0:
			logging.info("%s inserted\r\n" % paperid)
		else :
			logging.info("%s updated\r\n" % paperid)
		return False

papertype = sys.argv[1]
begindate = datetime.datetime(int(sys.argv[2][:4]),int(sys.argv[2][4:6]),int(sys.argv[2][6:]))
enddate = datetime.datetime(int(sys.argv[3][:4]),int(sys.argv[3][4:6]),int(sys.argv[3][6:]))
if not os.path.exists("log"):
	os.makedirs("log")
logging.basicConfig(filename="log/%s_%s_%s.log" % (sys.argv[1],sys.argv[2],sys.argv[3]), level=logging.INFO)
db = conn.cursor()

for i in range(int((enddate-begindate).days)+1):
	single_day=begindate+timedelta(i)
 	queryid = papertype+str(single_day.date().strftime('%Y%m%d'))
 	
 	query = "SELECT id,casehtml from raw_html where id Like \'"+queryid+"%\'"
 	# query = "SELECT id,casehtml from raw_html where id = 'TPDM20170301044' "
	db.execute(query)
	rows = db.fetchall()
	error_list = []

	for html in rows:
		doc = html[1]
		paperid = html[0]
		paper = parse(paperid,doc)
		if paper == "error":
			continue
		if DB_Output(conn,paperid,paper) :
			error_list.append(paperid)
	logging.info(str(queryid) + " Complete.\r\n")
	logging.info("Error_List : \r\n%s\r\n" % str(error_list))
conn.close()