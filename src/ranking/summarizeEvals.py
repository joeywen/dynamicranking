'''
Created on Feb 2, 2011

@author: Christie
'''
import os.path
import utils.flExts
def summarizeEval(evalsDir,summOutFl=None, verbosity = 1):
    sumUtil = dict()
    numExmpls = dict()
    algs = set()
    gms = set()
    ems = set()
    #algtypes = ['SM','DM','DL']
    #metrictypes = ['DCG','NDCG','MAP','PREC']
    #assumes formatting is tid+'_'+alg+'_genmet_'+gmet+'_evalmet_'+emet+'_tst.eval'
    for evflnm in os.listdir(evalsDir):
        if evflnm.endswith(utils.flExts.evalExt):
            with open(os.path.join(evalsDir, evflnm)) as evfl:
                (basenm,_,_)=evflnm.partition('.')
                (tid,alg,gmet,emet)= basenm. split('_')
                algs.add(alg)
                gms.add(gmet)
                ems.add(emet)
                if not((alg,gmet,emet) in sumUtil):
                    sumUtil[(alg,gmet,emet)]=0
                    numExmpls[(alg,gmet,emet)]=0
                for line in evfl:
                    (useln, ln) = utils.utils.stripComments(line)
                    if (useln):
                        (instid,tid,prnm,vv)=ln.strip().split(None)
                        sumUtil[(alg,gmet,emet)]+=float(vv)
                        numExmpls[(alg,gmet,emet)]+=1
            evfl.close()
    
        
    if summOutFl !=None:
        with open(summOutFl, 'w') as wr:
            for (alg,gmet,emet) in sumUtil.keys():
                summy = sumUtil[(alg,gmet,emet)]
                count = numExmpls[(alg,gmet,emet)]
                wr.write(alg+' '+gmet+' '+emet+' '+str(utils.utils.safeDiv(summy/count)))
    for gm in gms:
        for alg in algs:
            ss = alg+', '+gm+': '
            for em in ems:
                if (alg,gm,em) in sumUtil.keys():
                    summy = sumUtil[(alg,gm,em)]
                    count = numExmpls[(alg,gm,em)]
                    vv = summy/count
                else:
                    vv=0
                ss +=em+':'+str(vv)+' '
            print(ss)
                
#def evaluateWithFullKnowledge(verbosity = 1):
#    createPaths.getFullKnowledgePaths(docHistFl,qEventsFl,profilesFl,
#                outputPathFl,topicId,utilityMetric='DCG',algorithmType='DM',
#                cutoff=10, prClickIfDocRel=1, 
#                prClickIfDocNotRel=0, verbosity=2)
#    evaluatePaths(pathFl, profilesFl, topicId,
#                  outputEvalFl, metric='DCG', cutoff=10):
def __getfls(pth, extensions, extensionsOpt=None):
    retset = [None for _ in extensions]
    optRetSet = dict()
    for fl in os.listdir(pth):
        for ext in extensions:
            if fl.endswith(ext):
                ind = extensions.index(ext)
                retset[ind]=os.path.join(pth,fl)
        if (extensionsOpt != None ):
            for ext in extensionsOpt:
                if fl.endswith(ext):
                    optRetSet[ext]=os.path.join(pth,fl)
        if (retset.count(None)==0 and extensionsOpt==None):
            return retset
        elif (retset.count(None)==0 and len(extensionsOpt)==len(optRetSet)):
            return(retset,optRetSet)
    if (retset.count(None)==0):
        if (extensionsOpt==None):
            return retset
        else:
            return (retset,optRetSet)
    raise Exception('One of the filetypes doesnt exist!--' +repr(retset)\
                    + ' file: '+pth)