'''
Created on Jan 29, 2011

@author: Christie

Uses the qe file (produced previously) and the input file
to run the chosen algorithms and produce a path for each query event.

uses calcUtilities.getDocsetUtil 
and readInputFl's readInputFl,getDocSet,

'''

import tempfile
import shutil
import os.path
import utils.utils
import ranking.readInputFl
import ranking.calcUtilities
import utils.errorWr

def createPaths(inputDir, qEventDir, outputDir, 
                utilityMetric=['DCG'],algorithmType=['SM','DM'],
                cutoff=10, prClickIfRel=1, 
                prClickIfNotRel=0, verbosity=1):
    try:
        if not os.path.exists(outputDir):
            os.mkdir(outputDir)
        for fl in os.listdir(inputDir):
            inputFl = os.path.join(inputDir, fl)
            if (not fl.startswith('.') and not os.path.isdir(inputFl)\
                and fl.endswith(utils.flExts.inputExt)):
                (topicId, _,_)=fl.partition(utils.flExts.inputExt)
                
                qeFl = os.path.join(qEventDir, topicId+utils.flExts.qeExt)
                
                for alg in algorithmType:
                    for um in utilityMetric:
                        outputFl = os.path.join(outputDir, topicId+'_'+alg+'_'+um+\
                                                utils.flExts.pathExt)
                        createTopicPaths(inputFl, qeFl, outputFl, topicId,
                                 um, alg, cutoff, prClickIfRel,
                                 prClickIfNotRel, verbosity)
    except:
        utils.errorWr.wrErr(True)
'''
Given the input file and the qEvents file, calculates paths
and writes out results in outputPathFl.
'''
def createTopicPaths(inputFl,qEventsFl,outputPathFl,
                topicId,utilityMetric='DCG',algorithmType='DM',
                cutoff=10, prClickIfDocRel=1, 
                prClickIfDocNotRel=0, verbosity=2):
    if verbosity>=2:
        print('Getting path function for topic '+topicId
                  + ' for '+repr(utilityMetric)
                  +' and '+repr(algorithmType)
                  +' with input file '+repr(inputFl)+'\n')
        
    profileSet =ranking.readInputFl.readInputFl(inputFl, topicId)
    candidateSet = profileSet.getDocSet()
    
    predRelsFun = lambda candDocs, currPath: _predictRelsFK(
                prClickIfDocRel, prClickIfDocNotRel, 
                profileSet,candDocs, currPath)
    
    pathFunction = lambda clickset, profile: _getPath(utilityMetric, 
                            algorithmType, predRelsFun,
                            candidateSet, clickset, cutoff)
    if verbosity>=2:
        print('Path function created. Evaluating on query events in '
                  +repr(qEventsFl)+'...')
    qesToPath(qEventsFl, topicId, pathFunction, 
                            outputPathFl)
    if verbosity>=2:
        print('Paths created in '+repr(outputPathFl)+'.\n')
    return
'''Given a path function, evaluates queryHist file and writes out 
    the result. (note that pathFunction may have used a partialPath)
'''
def qesToPath(qEventsFl,topicId, pathFunction, outputFl,verbosity=2):
    with tempfile.NamedTemporaryFile('r+',delete= False)as tmpF:
        utils.utils.deleteOnExit(tmpF.name)
        #read in the qEvents file, line by line.
        with open(qEventsFl) as qef:
            #for each query event
            for line in qef:
                (notComment, ll)= utils.utils.stripComments(line);
                path = []
                if notComment:
                    (prefix,clickstr)=ll.split(':')
                    (instId,topicId,profile)=prefix.split(None)
                    clickset = set(clickstr.split(None))
                    path = pathFunction(clickset,profile.strip())
                    path = [path] if type(path)!=list else path
                    pathstr = ' '.join([d+':'+str(1 if c else 0) 
                                        for(d,c)in path])    
                    tmpF.write(instId+' '+topicId+' '+profile+
                               ' '+pathstr+'\n')
                    tmpF.flush()
                    if(verbosity>=3):
                        print('done '+instId)
            qef.close()
        tmpF.flush()
        tmpF.close()
        shutil.move(tmpF.name,outputFl)
        if (os.path.exists(tmpF.name)):
            os.remove(tmpF.name)
    return outputFl

'''Get the path using the predictDocRelsFun (different than the training,
    which produces a random path--doesn't use a "best" function.)
'''
def _getPath(metric, docChoiceType, predictDocRelsFun,candDocsSet,
            userClickBehaviorSet,cutoff,partialPath=None, verbosity=2):

    candDocs = set(candDocsSet);
    path = [] if partialPath==None else partialPath
    while len(path)<cutoff and len(candDocs)>0:
        bds = _getBestDoc(docChoiceType, predictDocRelsFun,
                            path, candDocs,cutoff,metric,
                            verbosity=verbosity)
        
        dlst = [(bds)] if type(bds) != list else bds
        for (d,u) in dlst:
            path.append((d,d in userClickBehaviorSet))
            candDocs.remove(d)
    path = path[0:cutoff]
    return path

'''Gets the best doc (or docs... depends on type.)
    @param algType the algorithm to use (SM, DM, DL)
    @param predictDocRelsFun the function to use to evaluate relevance
    @param currPath the current path
    @param candDocsSet the set of documents to choose the next best
        document from.
    @param cutoff the length of the ranking to produce (used in
        estimating utilities in DL)
    @param metric the metric to use to calculate, e.g. DCG; this is
        used for DL.
    
    To add a new doc type, add another "elif" statement here.
'''
def _getBestDoc(algType, predictDocRelsFun, currPath,
               candDocsSet, cutoff, metric,verbosity=2):
    
    #whatever happens, we'll need the relevances of
    #the first document set.
    docsRelsMap = dict(predictDocRelsFun(candDocsSet,currPath).items())
    if algType == 'SM' :
        #the false here says that the utilities returned can be
        #proportional to the probability of relevance rather than
        #actually getting the probability of relevance.
        utilsList = ranking.calcUtilities.getDocsetUtil(metric, False,
                      currPath,candDocsSet,
                      docsRelsMap, cutoff)
        utilsList.sort(key=lambda x: x[1],reverse=True)
        return utilsList[0:cutoff-len(currPath)]
    elif algType == 'DM' :
        utilsList = ranking.calcUtilities.getDocsetUtil(metric, False,
                      currPath,candDocsSet,
                      docsRelsMap, cutoff)
        retDoc = max(utilsList, key=lambda x: x[1])
        return [retDoc]
    elif algType == 'DL':
        metricFun = ranking.calcUtilities.getMetricFunction(metric)
        tempPath = [x for (x,_) in currPath]
        
        #utilsList = ranking.calcUtilities.getDocsetUtil(metric, True,
        #              currPath,candDocsSet,
        #              docsRelsMap, cutoff)
        bestDoc = None
        
        #for(candDoc, estRel) in utilsList:
        for candDoc in candDocsSet:
            estRel = docsRelsMap[candDoc]
            if (estRel>0 or bestDoc is None):
                
                predCandDocsSet = set(candDocsSet)
                
                predClickLst = currPath+[(candDoc,True)]
                predClDocsToRels = predictDocRelsFun(
                                                     predCandDocsSet,
                                                     predClickLst)
                predCandDocsSet.remove(candDoc)
                utilsClList = ranking.calcUtilities.getDocsetUtil(metric,False,
                                predClickLst,predCandDocsSet,
                                predClDocsToRels,cutoff)
                utilsClList.sort(key = lambda x:x[1],reverse=True)
                utilsClList = utilsClList[0:cutoff-len(predClickLst)]
                clList = list(tempPath)
                clList.append(candDoc)
                clList.extend([x for (x,_) in utilsClList])
                clUtil = metricFun(clList, predClDocsToRels,cutoff)
                #clUtil = sum(val for (_,val) in utilsClList)
                predSkipLst = currPath+[(candDoc,False)]
                predSkDocsToRels = predictDocRelsFun(
                                                     predCandDocsSet,
                                                     predSkipLst)
                utilsSkList = ranking.calcUtilities.getDocsetUtil(metric,True,
                                predSkipLst,predCandDocsSet,
                                predSkDocsToRels,cutoff)
                utilsSkList.sort(key = lambda x:x[1],reverse=True)
                utilsSkList = utilsSkList[0:cutoff-len(predSkipLst)]
                skList = list(tempPath)
                skList.append(candDoc)
                skList.extend([x for (x,_) in utilsSkList])
                #skUtil = sum(val for (_,val) in utilsSkList)
                skUtil = metricFun(skList, predSkDocsToRels, cutoff)
                
                fullEstRel = estRel*(clUtil)+(1-estRel)*skUtil
                #print(candDoc+':'+str(fullEstRel))
                bestDoc = (candDoc,fullEstRel) if bestDoc == None or bestDoc[1]<fullEstRel else bestDoc
        return [bestDoc]
    else:
        raise Exception('Doc Choice type not valid: SM, DM, DL not', algType)

'''Returns a map of the predicted relevances
    conditioned on the set of clicks/skips
    (docsRelsMap) based on full knowledge.
'''
def _predictRelsFK(prClickGivenRel, prClickGivenNonrel, 
                 profileSet,candDocs,currPath):

    #what is the probability that it is each profile,given the clicks?
    (probPrsGivenPath,_) = profileSet.getProbProfilesGivenClicks(
                prClickGivenRel, prClickGivenNonrel, currPath)
    #build dictionary:
    #the expected utility of a particular document is
    #the sum of (prob profile)(utility)
    docsToExpUtils = dict()
    for cd in candDocs:
        expVal = 0
        for (pr,probPr) in probPrsGivenPath:
            expVal +=(probPr*profileSet.getProfToDocVal(pr,cd))
        docsToExpUtils[cd] = expVal
    return docsToExpUtils