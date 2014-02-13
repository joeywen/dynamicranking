from root import ranking
import os
import shutil
inDir = 'trec_fk' 
outEvalDir = 'out_eval_dir'
outPathDir= 'out_path_dir'
outSummaryDir = 'out_summary_stats'
runtypes = ['DCG']
evaltypes = ['NDCG','DCG','MAP','PREC']
prClickIfRel = 1
prClickIfNotRel = 0
prep = True

if prep:
    #make a file with combined data.
    if os.path.exists(outPathDir):
        shutil.rmtree(outPathDir)
    os.mkdir(outPathDir)
    if os.path.exists(outEvalDir):
        shutil.rmtree(outEvalDir)
    os.mkdir(outEvalDir)
    ranking.prepareFKDirectoryInput(inDir, 
                prClickIfRel = prClickIfRel, 
                prClickIfNotRel = prClickIfNotRel,
                numQEvents = 10)
    ranking.evaluateFKModel(inDir, outEvalDir, outPathDir, 
                utilityMetrics = runtypes, evalMetrics = evaltypes,
                prClickIfRel = prClickIfRel, 
                prClickIfNotRel = prClickIfNotRel)

if os.path.exists(outSummaryDir):
    shutil.rmtree(outSummaryDir)
os.mkdir(outSummaryDir)
    
sumD = dict()
means = dict()
for rm in runtypes:
    for em in evaltypes:
        for et in ['DM','SM']:
            sumD[(rm,em,et)]=open(os.path.join(outSummaryDir, et+'_'+rm+'_'+em+'_stats'),'w')
            means[(rm,em,et)] = 0
numnum = len(os.listdir(outEvalDir))/(len(runtypes)*len(evaltypes)*2)
for drnm in os.listdir(outEvalDir):
    (tnm,et,_,rm,_,em,endy) = drnm.split('_')
    with open(os.path.join(outEvalDir, drnm)) as ff:
        summy = 0
        count = 0
        for line in ff:
            (instid,tid,prnm,vv)=line.strip().split(None)
            summy = summy+float(vv)
            count+=1
    sumD[(rm,em,et)].write(str(summy/count)+'\n')
    means[(rm,em,et)] +=(summy/count)
    
for wr in sumD.values():
    wr.close()
for rm in runtypes:
    for em in evaltypes:
        ss=('run type: '+rm+', eval type: '+em+',\t')
        for et in ['DM','SM']:
            ss+=et+': '+str(means[(rm,em,et)]/numnum)+'\t'
        print(ss)