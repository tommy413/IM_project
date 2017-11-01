import sys
import time
import os
import datetime
from datetime import timedelta
import psycopg2

def PrintQuery(query):
	conn = psycopg2.connect(database="law1", user="datac1", password="datac15543", host="ci.lu.im.ntu.edu.tw", port="5432")
	conn.set_session(autocommit=True)
	db = conn.cursor()

	print(query+"\n")
	db.execute(query)
	rows = db.fetchall()

	for row in rows:
		print(row)
		print("\n")
	return

QueryList = ["Select * from alldata where (caseid like '%,聲判,%') and (court like '%M') limit 5;"]

for query in QueryList:
	PrintQuery(query)

