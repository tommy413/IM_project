import os
import re

parserList = os.listdir('.')
parserList.remove('get_paper.py')
parserList.remove('line.py')
parserList.remove('main.py')
parserList.remove('reason_judge.py')
parserList.remove('accu_defe.py')

#forMAC
parserList.remove('.DS_Store')

for f in parserList:
    courtList = os.listdir(f)
    #forMAC
    courtList.remove('.DS_Store')
    for g in courtList:
        path = f+'/'+g

        files = os.listdir(path)
        #forMAC
        files.remove('.DS_Store')

        for f in files:
            fread = open(path+'/'+f ,'r')
            content = fread.read()

        #accuser & defendant
        accuser = ''
        defendant = ''
        advocate = ''
        accuser_pat = '公訴人|聲請人|原告'
        accuser_match = re.findall(accuser_pat,content)
        defendant_pat = '被告人|受刑人|被告|具保人|上訴人|自訴人'
        defendant_match = re.findall(defendant_pat,content)
        defendant_end_pat = '上列|主文'
        defendant_end_match = re.findall(defendant_end_pat,content)

        if len(defendant_match) > 0:
            defendantBeg = content.find(defendant_match[0])
            defendantEnd = defendantBeg + len(defendant_match[0])
            if len(defendant_end_match) > 0:
                defendantNameEnd = content.find(defendant_end_match[0])
                defendant = content[defendantEnd:defendantNameEnd]

            advocate_pat = '辯護人'
            choose_pat = '指定|選任'
            advocate_match = re.findall(advocate_pat, defendant)
            choose_match = re.findall(choose_pat, defendant)
            if len(advocate_match) > 0:
                advocateBeg = defendant.find(advocate_match[0])
                advocateEnd = advocateBeg + len(advocate_match[0])
                advocate = defendant[advocateEnd:]
                defendant = defendant[:advocateBeg]
                if len(choose_match) > 0:
                    chooseBeg = defendant.find(choose_match[0])
                    defendant = defendant[:chooseBeg]
            helper_pat = '輔佐人'
            helper_match = re.findall(helper_pat, defendant)
            if len(helper_match) > 0:
                helperBeg = defendant.find(helper_match[0])
                helperEnd = helperBeg + len(helper_match[0])
                helper = defendant[helperEnd:]
                defendant = defendant[:helperBeg]

        if len(accuser_match) > 0:
            accuserEnd = content.find(accuser_match[0]) + len(accuser_match[0])
            accuser = content[accuserEnd:defendantBeg]
            if accuser == '即':
                accuser = defendant
            agent_pat = '代理人'
            agent_match = re.findall(agent_pat, accuser)
            if len(agent_match) > 0:
                agentBeg = accuser.find(agent_match[0])
                agentEnd = agentBeg + len(agent_match[0])
                agent = accuser[agentEnd:]
                accuser = accuser[:agentBeg]

        if len(accuser_match) != 0:
            print (accuser_match[0] + ": " + accuser)
            if len(agent_match) != 0:
                print (accuser_match[0] + agent_match[0] + ": " + agent)
        if len(defendant_match) != 0:
            print (defendant_match[0] + ": " + defendant)
            if len(helper_match) != 0:
                print (defendant_match[0] + helper_match[0] + ": " + helper)
        if len(advocate_match) != 0:
            print (advocate_match[0] + ": " + advocate)
