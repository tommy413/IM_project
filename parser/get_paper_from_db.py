# -*- coding: utf8 -*-
from BeautifulSoup import BeautifulSoup
import sys
import os
import datetime
from datetime import timedelta
import psycopg2
import logging

conn = psycopg2.connect(database="law1", user="datac1", password="datac15543", host="ci.lu.im.ntu.edu.tw", port="5432")

def parse(paperid,html):
	info = ""
	paper = ""
	try {
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
	}catch (Exception e){
		logging.ERROR(paperid+"_parse_error_"+e)
	}
	return paper

def DB_Output(conn,paperid,paper):
	try {
		db = conn.cursor()
		db.execute("SELECT COUNT(id) from raw_html where id = \'%s\'" % (paperid))
		count = db.fetchall()[0][0]
		if count == 0 :
			query = "INSERT INTO HTMLDATA (ID,CONTENT) VALUES (\'%s\' , \'%s\')" % (paperid,paper)
			
		else :
			query = "UPDATE HTMLDATA SET CONTENT = \'%s\' " % (paper)
			
	}catch (Exception e){
		logging.ERROR(paperid+"_query_error_"+e)
	}
	try{
		db.execute(query)
		conn.commit()
		if count == 0:
			logging.INFO(paperid+" inserted")
		else :
			logging.INFO(paperid+" updateed")
	}catch{Exception e){
		logging.ERROR(paperid+"_commit_error_"+e)
	}
	return

papertype = sys.argv[1]
begindate = datetime.datetime(int(sys.argv[2][:4]),int(sys.argv[2][4:6]),int(sys.argv[2][6:]))
enddate = datetime.datetime(int(sys.argv[3][:4]),int(sys.argv[3][4:6]),int(sys.argv[3][6:]))
if not os.path.exists("log"):
		os.makedirs("log")
logging.basicConfig(filename="log/%s_%s_%s.log" % (sys.argv[1],sys.argv[2],sys.argv[3]), level=logging.INFO )
db = conn.cursor()

for i in range(int((enddate-begindate).days)+1):
	single_day=begindate+timedelta(i)
 	queryid = papertype+str(single_day.date().strftime('%Y%m%d'))
 	
 	query = "SELECT id,casehtml from raw_html where id Like \'"+queryid+"%\'"
 	# query = "SELECT id,casehtml from raw_html where id = 'TPDM20170301044' "
	db.execute(query)
	rows = db.fetchall()

	for html in rows:
		doc = html[1]
		paperid = html[0]
		paper = parse(paperid,doc)
		DB_Output(conn,paperid,paper)
	logging.INFO(queryid + " Complete.")
conn.close()