import os
import re

parserList = os.listdir('.')
parserList.remove('get_paper.py')
parserList.remove('line.py')
parserList.remove('main.py')
parserList.remove('reason_judge.py')
parserList.remove('accu_defe.py')
parserList.remove('all.py')
parserList.remove('get_paper_from_db.py')

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
            print(f)

            #accuser & defendant
            accuser = ''
            defendant = ''
            advocate = ''
            helper = ''
            agent = ''
            accuserList = []
            defendantList = []
            advocateList = []
            helperList = []
            agentList = []
            accuser_pat = '公訴人|聲請人|原告'
            accuser_match = re.findall(accuser_pat,content)
            defendant_pat = '被告人|受刑人|被告|具保人|上訴人|自訴人'
            defendant_match = re.findall(defendant_pat,content)
            defendant_end_pat = '上列|主文'
            defendant_end_match = re.findall(defendant_end_pat,content)

            advocate_match = ''
            helper_match = ''
            agent_match = ''
            also_match = ''
            also_match_two = ''
            also_accuser_match = ''

            # 被告
            if len(defendant_match) > 0:
                defendantBeg = content.find(defendant_match[0])
                defendantEnd = defendantBeg + len(defendant_match[0])
                if len(defendant_end_match) > 0:
                    defendantNameEnd = content.find(defendant_end_match[0])
                    defendant = content[defendantEnd:defendantNameEnd-1]

                # 即其他稱號
                also_pat = '\n即\n'
                also_match = re.findall(also_pat,defendant)
                if len(also_match)!=0:
                    alsoBeg = defendant.find('\n即\n')
                    alsoEnd = alsoBeg+3
                    defendant = defendant[alsoEnd:]
                also_pat_two = '\n即'
                also_match_two = re.findall(also_pat_two,defendant)
                if len(also_match_two)!=0:
                    alsoBeg_two = defendant.find('\n即')
                    alsoEnd_two = alsoBeg_two+2
                    defendant = defendant[alsoEnd_two:]

                # 辯護人
                advocate_pat = '辯護人'
                choose_pat = '指定|選任'
                advocate_match = re.findall(advocate_pat, defendant)
                choose_match = re.findall(choose_pat, defendant)
                if len(advocate_match) > 0:
                    advocateBeg = defendant.find(advocate_match[0])
                    advocateEnd = advocateBeg + len(advocate_match[0])
                    advocate = defendant[advocateEnd:]
                    defendant = defendant[:advocateBeg-1]
                    if len(choose_match) > 0:
                        chooseBeg = defendant.find(choose_match[0])
                        defendant = defendant[:chooseBeg-1]
                # 輔佐人
                helper_pat = '輔佐人'
                helper_match = re.findall(helper_pat, defendant)
                if len(helper_match) > 0:
                    helperBeg = defendant.find(helper_match[0])
                    helperEnd = helperBeg + len(helper_match[0])
                    helper = defendant[helperEnd:]
                    defendant = defendant[:helperBeg-1]
            # 原告
            if len(accuser_match) > 0:
                accuserEnd = content.find(accuser_match[0]) + len(accuser_match[0])
                accuser = content[accuserEnd:defendantBeg]

                also_accuser_pat = '\n即'
                also_accuser_match = re.findall(also_accuser_pat,accuser)
                # if len(also_accuser_match)!=0:

                # 原告即被告
                if accuser == '\n即':
                    accuser = defendant
                else:
                    accuserEnd = content.find(accuser_match[0]) + len(accuser_match[0])
                    accuser = content[accuserEnd:defendantBeg-1]

                    # 即其他稱號
                    if len(also_accuser_match)!=0:
                        alsoAccuBeg = accuser.find('\n即')
                        alsoAccuEnd = alsoAccuBeg+2
                        accuser = accuser[alsoAccuEnd:]

                    # 原告代理人
                    agent_pat = '代理人'
                    agent_match = re.findall(agent_pat, accuser)
                    if len(agent_match) > 0:
                        agentBeg = accuser.find(agent_match[0])
                        agentEnd = agentBeg + len(agent_match[0])
                        agent = accuser[agentEnd:]
                        accuser = accuser[:agentBeg-1]


            accuserList = accuser.split('\n')
            helperList = helper.split('\n')
            defendantList = defendant.split('\n')
            agentList = agent.split('\n')
            advocateList = advocate.split('\n')

            if len(accuser_match) != 0:
                print (accuser_match[0] + ": ", accuserList)
                if len(agent_match) != 0:
                    print (accuser_match[0] + agent_match[0] + ": ",  agentList)
            if len(defendant_match) != 0:
                print (defendant_match[0] + ": ", defendantList)
                if len(helper_match) != 0:
                    print (defendant_match[0] + helper_match[0] + ": ", helperList)
            if len(advocate_match) != 0:
                print (advocate_match[0] + ": ", advocateList)
