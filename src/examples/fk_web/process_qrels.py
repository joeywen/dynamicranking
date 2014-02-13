'''
Created on Feb 2, 2011

@author: Christie


@author: Christie
processes qrel file (which is in form 22 4 clueweb09-en0127-93-14622 1)
to input data form, which has the following requirements:
--file name = topic name
--each line contains one profile
--format of line is topicid profileid profilewt docid: rel docid: rel etc.
'''
import os.path
def processTrecFl(inFl = 'qrels_clueweb.txt', outDir='web_input'):
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    with open(inFl) as rd:
        currLine = rd.readline()
        currTopic = None
        dd = dict()
        docs = set()
        while currLine != None and len(currLine)>0:
            (topicId, profileId, docId, isRel)= currLine.strip().split(None)
            if currTopic == None:
                currTopic = topicId
            if topicId!=currTopic:
                with open(os.path.join(outDir,currTopic+'.txt'),'w') as wr:
                    #for the first line, write them all out, relevant or no.
                    doNonrels = True
                    pMax = max([int(x) for x in dd.keys()])
                    for i in range(pMax):
                        pr = str(i+1)
                        ll = []
                        if pr in dd:
                            pDocs = dd[pr]
                            
                            if doNonrels:
                                doNonrels = False
                                for d in docs:
                                    if d in pDocs:
                                        ll.append(d+':1')
                                    else:
                                        #pass
                                        ll.append(d+':0')
                            else:
                                for pd in pDocs:
                                    ll.append(pd+':1')
                        wr.write(currTopic+' '+str(pr)+' '+'1'+' '+" ".join(ll)+'\n')
                    wr.close()
                currTopic = topicId
                dd = dict()
                docs = set()
                
            docs.add(docId)
            if (isRel=='1'):
                if not profileId in dd:
                    dd[profileId] = set();
                dd[profileId].add(docId)
            currLine = rd.readline()
    with open(os.path.join(outDir,currTopic+'.txt'),'w') as wr:
        #for the first line, write them all out, relevant or no.
        doNonrels = True
        for (pr, pDocs) in dd.items():
            ll = []
            if doNonrels:
                doNonrels = False
                for d in docs:
                    if d in pDocs:
                        ll.append(d+':1')
                    else:
                        ll.append(d+':0')
                        
            else:
                for pd in pDocs:
                    ll.append(pd+':1')
            wr.write(currTopic+' '+str(pr)+' '+'1'+' '+" ".join(ll)+'\n')
        wr.close()
