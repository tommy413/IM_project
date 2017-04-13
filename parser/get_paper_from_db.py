# coding: utf8
from BeautifulSoup import BeautifulSoup
import sys
import os

crawl_path = "../crawler/downloaded/" 
path = sys.argv[1] + "/"
for i in range(int(sys.argv[2]),int(sys.argv[3])+1,1):
	foldername = str(i)[:4] + "-" + str(i)[4:6] + "-" + str(i)[6:]
	fileList = os.listdir(crawl_path+path+foldername)
	if not os.path.exists(path+foldername) :
		os.makedirs(path+foldername)
	for f in fileList:
		if "-h" in f:
			continue
		filename = path+foldername+"/"+f
		input_file = open(crawl_path+filename,'r')
		output_file = open(filename[:-5]+".txt",'w')

		soup = BeautifulSoup(input_file)
		output_file.write(str(soup.title.string)+"\r\n")
		body = soup.body
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
									output_file.write(info.encode("utf8")+"\r\n")
							if "裁判全文" in info.encode("utf8"):
								break
						paper = str(td.pre.string).replace('	','').replace(' ','').replace(' ','').replace('\t','').replace('　','')
						output_file.write(paper)
						flag = 1
		input_file.close()
		output_file.close()