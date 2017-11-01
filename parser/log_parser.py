import sys
import os
import csv

def str_to_list(inputstr):
	inputstr = inputstr[1:-2]
	inputstr = inputstr.replace('\'','').replace(' ','')
	idlist = inputstr.split(",")
	idlist = [x for x in idlist if x]
	return idlist

def file_to_list(log_path):
	log_file = open(log_path,'r')
	log_str = log_file.read()
	logs = log_str.split("\n")
	logs = [x for x in logs if x]
	log_file.close()
	return logs

parser_error_list = ["parser_error"]
ip_block_list = ["ip_block"]
empty_html_list = ["empty_html"]

path =  "log"

for dirPath, dirNames, fileNames in os.walk(path):
	for f in fileNames:
		print os.path.join(dirPath, f)
		path_logs = file_to_list(os.path.join(dirPath, f))
		if path_logs[-5] :
			parser_error_list = parser_error_list + str_to_list(path_logs[-5])
		if path_logs[-3] :
			ip_block_list = ip_block_list + str_to_list(path_logs[-3])
		if path_logs[-1] :
			empty_html_list = empty_html_list + str_to_list(path_logs[-1])

out = open("log_error_list.csv",'w')
csvw = csv.writer(out)
csvw.writerow(parser_error_list)
csvw.writerow(ip_block_list)
csvw.writerow(empty_html_list)
out.close()