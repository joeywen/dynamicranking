'''
Created on Jan 29, 2011

@author: Christie

performs calculation of the estimated utility, either of 
a document, a set of documents, or a path.
Utilized in generating the paths to determine what document to use next
Utilized in evaluatePaths to determine the utlity fo a given path.
'''
import math
'''Returns the evaluation function for the given metric.
    The returned function takes 3 inputs:
    documentsInPath: list of current docs in path.
    docsToRels: map of doc-->rel value.
        Note that this value can be estimated.  For instance:
        --in evaluation, this is relevance for this profile.
        --in deterministic full-knowledge, this is:
            -relevance of all docs seen
            -E(util| past path) of all docs unseen
        --in nondeterministic fk, this is:
            -E(util|click) of all docs seen
            -E(util|past click behavior)
    ctf: cutoff value after which point, stop evaluating.
 '''
def getMetricFunction(metric):
    if metric =='NDCG':
        return lambda dip,dtr,ctf:_calcNDCG(dip,dtr,ctf)
    elif metric == 'DCG':
        return lambda dip,dtr,ctf: _calcDCG(dip,dtr,ctf)
    elif metric == 'PREC':
        return lambda dip,dtr,k:_calcPrec_k(dip,dtr,k)
    elif metric=='MAP':
        return lambda dip,dtr,ctf:_calcMAP(dip,dtr,ctf)
    else:
        raise Exception('metric not implemented.')
    return

'''Returns the estimated utility of each element in potentialDocList,
in the same order as potentialDocList.
    @param metric: DCG, NDCG, etc
    @param isAbsolute: should the absolute marginal 
        utility be returned or is the relative marginal utility ok?
    @param docsInOldPath: the docs that are already in the path
    @param potentialDocList: set of new candidate documents.
        -a list of documents (eg, myopic evaluation)
        -a list of lists of documents (used for lookahead)
        If the latter, then the difference in utility is still returned.
    @param docsToRels: 
        --in evaluation, this is relevance for this profile.
        --in deterministic full-knowledge, this is:
            -relevance of all docs seen
            -E(util| past path) of all docs unseen
        --in nondeterministic fk, this is:
            -E(util|click) of all docs seen
            -E(util|past click behavior)
    @param cutoff: point at which adding a doc no longer helps.
'''
def getDocsetUtil(metric, isAbsolute,docsInOldPath,
                  potentialDocList,docsToRels, cutoff):

    q1 = getMetricFunction(metric)
    utilLst = []
    oldV = 0 if not(isAbsolute) else q1(docsInOldPath, docsToRels, cutoff)
    for newDoc in potentialDocList:
        newDocs = [newDoc] if type(newDoc)==str else newDoc
        #put doc under consideration onto the list
        docsInOldPath.extend(newDocs)
        newV = q1(docsInOldPath,docsToRels,cutoff)
        #pop doc under consideration off of the list.
        docsInOldPath.pop()
        utilLst.append((newDoc,(newV-oldV)))
    return utilLst
'''
@param metric: the type of evaluation (e.g., DCG)
@param isAbsolute: do the values for the document set need to be
the actual probability values, or can they just be proportional to them? 
returns a function for document set utility.
New function accepts input: documents previously in path,
new document set, map of documents to their relevances, and cutoff.
'''
#def getDocsetUtilFunction(metric, isAbsolute=False):
#    '''Returns a function to calculate docsetUtil, where the
#    metric and absoluteness no longer must be filled in.
#    '''
#    return lambda docsInOldPath, newDocSet, docsToRels, cutoff:\
#        _getDocsetUtil(metric, isAbsolute, docsInOldPath, 
#                      newDocSet, docsToRels,cutoff)

'''
calculates NDCG; requires relevances to be binary.
'''
def _calcNDCG(docsInPath, docsToRels, cutoff):
    if type(docsToRels)!= dict:
        raise ValueError('huh?')
    bstLst = list(docsToRels.items()) 
    #if type(docsToRels)=='dict' else list(docsToRels)
    bstLst.sort(key = lambda bst:bst[1],reverse=True)
    bstDocs= [bst[0] for bst in bstLst]
    bestDcg = _calcDCG(bstDocs[0:cutoff],docsToRels, cutoff)
    realDcg = _calcDCG(docsInPath, docsToRels, cutoff)
    ndcg = realDcg / bestDcg if bestDcg>0 else 0
    return ndcg
'''
calculates DCG; requires relevances to be binary.  
'''
def _calcDCG(docsInPath, docsToRels,cutoff):
    pos = 0
    utilSum = 0
    for doc in docsInPath:
        if doc in docsToRels and pos<cutoff:
            util = (docsToRels[doc])/math.log(2+pos,2)
            #util = (math.pow(2,docsToRels[doc])-1)/math.log(2+pos,2)
            utilSum = utilSum+util
        pos = pos+1
    return utilSum
'''
Calculates precision at k.
'''
def _calcPrec_k(docsInPath, docsToRels, k):
    pos = 0 
    utilSum = 0
    for doc in docsInPath:
        if doc in docsToRels and pos<k:
            utilSum= utilSum+docsToRels[doc]
        pos=pos+1
    return utilSum/k
''' 
Calculates mean average precision; relevances must be binary.
'''
def _calcMAP(docsInPath, docsToRels,cutoff):
    numSeen = 0
    numRels = 0
    apsum = 0
    for doc in docsInPath:
        numSeen = numSeen+1
        if doc in docsToRels and numSeen<=cutoff:
            numRels = numRels+docsToRels[doc]
            prec = numRels/numSeen
            apsum = apsum+prec
    totalNumRels = len(docsToRels)
    map = apsum/totalNumRels if totalNumRels>0 else 0
    return map