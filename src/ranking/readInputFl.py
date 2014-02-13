'''
Created on Jan 29, 2011

@author: Christie
Contains the code to read in an input file and produce
a map of the profiles inside it.
A profile consists of 

A set of (user) profiles for a particular topic 
represents the set of different "types" of users.

'''
from utils import utils
""" first, read in the files and compute a map of 
    profile-->set of reldocs
    profile format: ignore anything in #'s.
    then topic profile wt did1:rel1 ...etc.
    returns three dictionaries: the first maps each profileId in the file
    to its weight (where weights are required to be >=0)
    the second maps profiles to sets of (docId, rel) pairs,
    and the 3rd is for convenience and maps profiles to docs (rather than tuples)
"""
def readInputFl (inputFile, topicId): 
    with open(inputFile) as f:
        docSet = set();
        profsToWts = dict();
        profsToDocsRels = dict();
        profsToDocs = dict();
        for line in f:
            (notComment,ll) = utils.stripComments(line)
            if notComment:
                strlst = ll.split(None)
                if len(strlst)<3:
                    raise( 'file format error: file length ',\
                    len(strlst), ' correct format <topicid> <profileid> ',\
                    '<profileweight> <docid1>:rel1 <docid2>:rel2...')
                if strlst[0] != str(topicId):
                        raise Exception('incorrect topicId: input '\
                                        +topicId, 'this ',strlst[0])
                pid = strlst[1].strip()
                if pid in profsToWts:
                    raise Exception('profile appears more than once. ')
                if (not strlst[2].isnumeric()) or float(strlst[2])<0:
                    raise Exception('profile weight nonnumeric or outside'\
                                    ' allowable range (>0), wt:',strlst[2])
                profsToWts[pid] = float(strlst[2])
                drels = dict();
                dsOnly = set();
                for drel in strlst[3:len(strlst)]:
                    splits = drel.split(':');
                    if(len(splits)!=2):
                        raise Exception('wrong # for docid str  ',drel)
                    docid=splits[0].strip();
                    if (not splits[1].strip().isnumeric()):
                        raise Exception('document relevance must be numeric.')
                    docrel = float(splits[1].strip());
                    if (docrel >1 or docrel<0):
                        raise Exception('doc relevance outside range 0 to 1:',docrel)
                    #if the relevance is >0, add it to the document set for this profile.
                    if (docrel>0):
                        drels[docid] =docrel
                        dsOnly.add(docid)
                    #in any case, add the document to the set of all documents.
                    docSet.add(docid)
                profsToDocsRels[pid] = drels;
                profsToDocs[pid]=dsOnly;
        f.close();
        profileSet = ProfileSet(topicId, profsToWts, profsToDocsRels, 
                                profsToDocs, docSet)
        return profileSet
class ProfileSet:
    def __init__(self, topicId, profsToWts, profsToDocsRels, 
                                profsToDocs, docSet):
        self.topicId = topicId
        self.profsToWts = profsToWts;
        self.profsToDocsRels=profsToDocsRels;
        self.profsToDocs = profsToDocs;
        self.docSet = docSet;
        return
    
    def getDocSet(self):
        return self.docSet
    
    def getDocRelMap(self,profile):
        if profile in self.profsToDocsRels:
            return self.profsToDocsRels[profile]
        return None
    
    def getProfToDocMap(self):
        return self.profsToDocs
    
    def getProfToDocVal(self, profile, doc):
        if profile in self.profsToDocsRels:
            if doc in self.profsToDocsRels[profile]:
                val = (self.profsToDocsRels[profile])[doc]
                return val
        return 0
    
    def getCandDocSet(self, profile):
        if profile in self.profsToDocs:
            return self.profsToDocs[profile]
        return None
    
    def _getWt(self, profile):
        if profile in self.profsToWts:
            return self.profsToWts[profile]
        return None
    '''Calculates the probability of each profile given the current path.
    @return a map of profile-->prob(profile) given path
    '''
    def getProbProfilesGivenClicks(self, prClGivenRel,prClGivenNonrel,path):        
        totalWt = sum(self.profsToWts.values())
        profsToRoughProbs = dict()
        probPath = 0
        for (prof,docsToRels) in self.profsToDocsRels.items():
            #initialize as probability of profile
            #pr(profile and path) = pr(path | profile) pr(profile)
            probProfAndPath = self._getWt(prof)/totalWt
            for (d,c) in path:
                #what is the probability of a match with this 
                #profile's rel/nonrel given the action?
                rel = docsToRels[d] if d in docsToRels else 0
                if c :
                    #prob(rel|click) = pr(rel and click)/pr(click)
                    prMatchGivenPr = rel*prClGivenRel+(1-rel)*prClGivenNonrel
                else:
                    #prob(nonrel|no click)= pr(nonrel and no click)/pr(no click)
                    prMatchGivenPr = rel*(1-prClGivenRel)+(1-rel)*(1-prClGivenNonrel)
                probProfAndPath= probProfAndPath*prMatchGivenPr
                
            profsToRoughProbs[prof]=probProfAndPath
            probPath = probPath+probProfAndPath
        profsToProbs = [(prof,utils.safeDiv(prob,probPath))\
                        for (prof,prob)in profsToRoughProbs.items()]
        return (profsToProbs, probPath)
    '''
    get the probability that the profile matches the click/skip
    '''
    def getProbMatchGivenPr(self, pr, prClGivenRel, prClGivenNonrel, cl, d):
        docsToRels = self.getDocRelMap(pr)
        rel = docsToRels[d] if d in docsToRels else 0
        if cl :
            #prob(rel|click) = pr(rel and click)/pr(click)
            prMatchGivenAction = rel*prClGivenRel+(1-rel)*prClGivenNonrel
        else:
            #prob(nonrel|no click)= pr(nonrel and no click)/pr(no click)
            prMatchGivenAction = rel*(1-prClGivenRel)+(1-rel)*(1-prClGivenNonrel)
        return prMatchGivenAction
    
    '''
    also read in all profiles and their weights and produce a list:
    profileId:weight+accumWeight
    '''
    def _getAccumWeightLst(self):
        #profsToWts: dictionary mapping profileId-->(double)wt.
        wtsLst = [];
        currWt = 0;
        for pr in self.profsToWts.keys():
            wt = self.profsToWts[pr];
            currWt = currWt+wt;
            wtsLst.append((pr,currWt))
        return wtsLst
