# -*- coding: utf8 -*-
from BeautifulSoup import BeautifulSoup
import sys
import csv
import time
import os
import datetime
from datetime import timedelta
import psycopg2
import logging

conn = psycopg2.connect(database="law1", user="datac1", password="datac15543", host="ci.lu.im.ntu.edu.tw", port="5432")
conn.set_session(autocommit=True)

def parse(paperid,html):
	info = ""
	paper = ""
	try:
		soup = BeautifulSoup(doc)
		paper = str(soup.title.string)+"\r\n"
		if "不合法，請洽網管人員" in paper:
			logging.error("%s_ip_block\r\n")
			return "block"
		
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
		logging.error("%s_parse_error : %s\r\n" % (paperid,e) )
		return "error"
	else :
		if "裁判全文" not in paper:
			logging.error("%s_data_error : without paper\r\n" % (paperid) )
			return "empty"
		else :
			return paper

def DB_Output(conn,paperid,paper):
	paper = paper.replace("'","''")
	db = conn.cursor()
	db.execute("SELECT COUNT(id) from htmldata where id = \'%s\'" % (paperid))
	count = int(db.fetchall()[0][0])
	if count == 1 :
		query = "UPDATE htmldata SET content = \'%s\' where id = \'%s\'" % (paper,paperid)
	else :
		query = "INSERT INTO htmldata (id,content) VALUES (\'%s\' , \'%s\')" % (paperid,paper)
		
	try:
		db.execute(query)
		conn.commit()
	except Exception as e:
		logging.error("%s_commit_error : %s\r\n" % (paperid,e))
		return True
	else:
		if count == 1:
			logging.info("%s updated\r\n" % paperid)
		else :
			logging.info("%s inserted\r\n" % paperid)
		return False

papertype_list = []
if sys.argv[1]=="-c":
	papertype_list = [sys.argv[2]]
if sys.argv[1]=="-f":
	papertype_list = list(csv.reader(open(sys.argv[2],'r')))[0]

begindate = datetime.datetime(int(sys.argv[3][:4]),int(sys.argv[3][4:6]),int(sys.argv[3][6:]))
enddate = datetime.datetime(int(sys.argv[4][:4]),int(sys.argv[4][4:6]),int(sys.argv[4][6:]))
db = conn.cursor()

# logging.basicConfig(level = logging.ERROR ,format='%(asctime)s: %(levelname)s - %(message)s')
formatter = logging.Formatter('%(asctime)s: %(levelname)s - %(message)s')
logging.getLogger('').setLevel(logging.INFO)

for papertype in papertype_list:
	for i in range(int((enddate-begindate).days)+1):
		single_day=begindate+timedelta(i)
		if not os.path.exists("log/%s" % papertype):
			os.makedirs("log/%s" % papertype)
		logfile_filehandler = logging.FileHandler("log/%s/%s.log" % (papertype,str(single_day.date().strftime('%Y%m%d'))))
		logfile_filehandler.setLevel(logging.INFO)
		logfile_filehandler.setFormatter(formatter)
		logging.getLogger('').addHandler(logfile_filehandler)

	 	queryid = papertype+str(single_day.date().strftime('%Y%m%d'))
	 	
	 	query = "SELECT id,casehtml from raw_html where id Like \'"+queryid+"%\'"
		db.execute(query)
		rows = db.fetchall()
		ip_block = []
		empty_html = []
		parser_error = []

		for html in rows:
			doc = html[1]
			paperid = html[0]
			paper = parse(paperid,doc)
			if paper == "error":
				parser_error.append(paperid)
				continue
			if paper == "block":
				ip_block.append(paperid)
				continue
			if paper == "empty":
				empty_html.append(paperid)
				continue
			flag = DB_Output(conn,paperid,paper)
			if flag==True :
				error_list.append(paperid)
		logging.info(str(queryid) + " Complete.\r\n")
		logging.error("Empty_List : \r\n%s\r\n" % str(empty_html))
		logging.error("Block_List : \r\n%s\r\n" % str(ip_block))
		logging.error("Error_List : \r\n%s\r\n" % str(parser_error))
		logging.getLogger('').removeHandler(logfile_filehandler)
		logfile_filehandler.close()

conn.close()
