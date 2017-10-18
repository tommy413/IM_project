# coding: utf-8
import psycopg2

conn = psycopg2.connect(database="law1", user="datac1", password="datac15543", host="localhost", port="5432")
print("Opened database successfully")

cur = conn.cursor()

def update_set(name,nameset,nameFile):
	name = name.strip()
	if name not in nameset and name != "":
		nameFile.write("%s\t%d\n" % (name,len(nameset) + 1))
		nameset.add(name)
	return nameset

judgeSet = set()
judgeF = open("judge_dict.txt.2",'w')

defendantSet = set()
defendantF = open("defendant_dict.txt.2",'w')

accuserSet = set()
accuserF = open("accuser_dict.txt.2",'w')

claimSet = set()
claimF = open("claim_dict.txt.2",'w')

agentSet = set()
agentF = open("agent_dict.txt.2",'w')

advocateSet = set()
advocateF = open("advocate_dict.txt.2",'w')

helperSet = set()
helperF = open("helper_dict.txt.2",'w')

for i in range(1,1252):
	cur.execute("""SELECT judge,defendant,accuser,claim,agent,advocate,helper FROM jdata_features WHERE sqlid IN (SELECT sqlid FROM jdata_meta WHERE sqlid >= %d and sqlid < %d and parser_done = 1 )""" % ((i-1)*1000,i*1000))
	rows = cur.fetchall()

	for row in rows:
		judgeSet = update_set(row[0],judgeSet,judgeF)
		defendantSet = update_set(row[1],defendantSet,defendantF)
		accuserSet = update_set(row[2],accuserSet,accuserF)
		claimSet = update_set(row[3],claimSet,claimF)
		agentSet = update_set(row[4],agentSet,agentF)
		advocateSet = update_set(row[5],advocateSet,advocateF)
		helperSet = update_set(row[6],helperSet,helperF)

	print(i)
	print(len(judgeSet))
	print(len(defendantSet))
	print(len(accuserSet))
	print(len(claimSet))
	print(len(agentSet))
	print(len(advocateSet))
	print(len(helperSet))
	print("#######################################")
