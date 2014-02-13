'''
Created on Feb 2, 2011

@author: Christie
'''
'''
Created on Aug 29, 2010

@author: Christie
processes qrel file (which is in form 307    FT921-12215    00000000000000000000000)
to input data form, which has the following requirements:
--file name = topic name
--each line contains one profile
--format of line is topicid profileid profilewt docid: rel docid: rel etc.
'''
import os.path
def processTrecFl(inFl = 'qrels_interactive_full', outDir='interactive_input'):
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    with open(inFl) as rd:
        currLine = rd.readline()
        currTopic = None
        dd = dict()
        docs = set()
        while currLine != None and len(currLine)>0:
            (topicId, docId, profiles)= currLine.strip().split(None)
            if currTopic == None:
                currTopic = topicId
            if topicId!=currTopic:
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
                                    #pass
                                    ll.append(d+':0')
                        else:
                            for pd in pDocs:
                                ll.append(pd+':1')
                        wr.write(currTopic+' '+str(pr)+' '+str(len(pDocs))+' '+" ".join(ll)+'\n')
                    wr.close()
                currTopic = topicId
                dd = dict()
                docs = set()
                
            docs.add(docId)
            for i in range(len(profiles)):
                if (profiles[i]=='1'):
                    if not (i+1) in dd:
                        dd[i+1]=set()
                    dd[i+1].add(docId)
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
            wr.write(currTopic+' '+str(pr)+' '+str(len(pDocs))+' '+" ".join(ll)+'\n')
        wr.close()
