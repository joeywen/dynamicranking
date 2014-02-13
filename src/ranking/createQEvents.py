'''
Created on Jan 29, 2011

@author: Christie
Produces a set of "user profiles" for a particular
topic based on the "profile weight", where the weight is
defined as essentially a potential; a probability value which
might not sum to 1 (can be scaled).
NOTE: relevance is between 0 and 1; for graded relevance with nondeterministic
users, the probability of a click= rel*prClGivenRel +(1-rel)*prClGivenNonrel

However, several of the utilitiy functions require binary relevance values.
Utilizes readInputFl.
'''
import random
import tempfile
import shutil
import os.path
from ranking import readInputFl
import utils.errorWr
import utils.flExts
'''
'''
def createQEvents(inputDir, outputDir,
                  numQEvents=10,prClickIfRel=1, 
                  prClickIfNotRel=0,verbosity=1):
    try:
        if (not os.path.isdir(outputDir)):
            os.mkdir(outputDir)
        for fl in os.listdir(inputDir):
            flpath = os.path.join(inputDir, fl)
            if (not fl.startswith('.')) and not os.path.isdir(flpath) \
                    and fl.endswith(utils.flExts.inputExt):
                (topicId,_,_)=fl.partition(utils.flExts.inputExt)
                outfl=os.path.join(outputDir,topicId+utils.flExts.qeExt)
                createTopicQEvents(topicId, flpath, outfl, numQEvents, 
                            prClickIfRel,prClickIfNotRel, verbosity)
    except:
        utils.errorWr.wrErr(True)

'''
Creates a set of query events in the specified saveFile.
A query event represents a particular instance of a user who
performs the specified search.  
'''
def createTopicQEvents(topicId, inputFl,saveFile,
                  numQEvents=10,prClickGivenRel=1, 
                  prClickGivenNonrel=0,verbosity=2):
    #create temporary file 
    tmpF = tempfile.NamedTemporaryFile('r+',delete=False);
    #get profiles and their respective relevant docs
    profileSet =readInputFl.readInputFl(inputFl, topicId);
    
    #make the prsToWeights into a list for actual use.
    accumWtLst =profileSet._getAccumWeightLst()
    
    for i in range(numQEvents):
        randint = random.getrandbits(16);
        #choose a profile according to wt distribution
        #generate random instanceId:topic,profile, and random int appended.
        profile = _getRandomProfile(accumWtLst)
        
        #generating instanceId: large random integer.
        instId = str(topicId)+str(profile)+str(i)+str(randint)
        allDocs = set(profileSet.getDocSet())
        #get clickset.
        relDocs = profileSet.getDocRelMap(profile)
        nonrelDocs = allDocs.difference(profileSet.getCandDocSet(profile))
        clickset = _getClickset(relDocs,nonrelDocs,
                               prClickGivenRel,prClickGivenNonrel)
        #write out <topic> <profile> <clicked>
        clickStr = ' '.join(clickset)
        tmpF.write(instId+' '+topicId+' '+profile+':'+clickStr+' \n')
    #probably need buffered writer.
    tmpF.flush()
    tmpF.close()
    shutil.move(tmpF.name, saveFile);
    if (os.path.exists(tmpF.name)):
        os.remove(tmpF.name)
    return saveFile



#(note that the other file is needed IFF the users are not
#deterministic; if they are, then only need to look at rel documents.
#if it is needed, create a set/list of nonrelDocs.
#all that we care about for this file is the first 2 cols.



#pick a random number from 0 to accumWeight, then walk over the
#list to find the correct location (this could be sped up with a
#binary search, but since there are so few profiles, why bother?)
def _getProfile(wtsLst,wt):
    if wt< 0 or wt > (wtsLst[len(wtsLst)-1])[1]:
        raise Exception('wt is outside wtsLst range.')
    for (pr, pWt) in wtsLst:
        if pWt>=wt:
            return pr;
def _getRandomProfile(wtsLst):
    wtMax =(wtsLst[len(wtsLst)-1])[1];
    r = random.uniform(0,wtMax);
    return _getProfile(wtsLst,r)
    
#for each relevant doc, either copy it over if deterministic or
#flip a coin
#CURRENT ASSUMPTION: graded relevances are between 0 and 1.
#returns a sparse set of documents which were clicked.
def _getClickset(relDocs, nonrelDocs, prClGivenRel, prClGivenNonrel):
    clickset = set();
    #first go thru all of the relevant ones.
    for (did,rel) in relDocs.items():
        if did in clickset:
            raise Exception ('one docid has occurred twice; incorrect format.')
        prClick = rel*prClGivenRel + (1-rel)*prClGivenNonrel;
        r=random.random();
        if(r<=prClick):
            clickset.add(did);
            
    #go thru all nonrelevant ones if prClGivenNonrel>0
    if prClGivenNonrel>0:
        for did in nonrelDocs:
            if did in clickset:
                raise Exception ('one docid has occurred twice; incorrect format.')
            r = random.random();
            if (r<=prClGivenNonrel):
                clickset.add(did);
    return clickset;
        
