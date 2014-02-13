'''
Created on Aug 17, 2010

@author: Christie
'''
import re
import os.path
import atexit

'''
We ran into a problem that on some Linux machines,
temporary files don't appear to delete; we manually delete
them on exit.  If exit is abnormal, then the files will
remain (and can be examined for any problems.
'''
def deleteOnExit(flname):
    atexit.register(_deletelet,flname)
'''
Helper for deleteOnExit.
'''
def _deletelet(flname):
    if os.path.exists(flname):
        os.remove(flname)
'''
Removes comments from input file.
'''
def stripComments(line):
    #print(line)
    ll = re.sub('[#].*','',line).strip()
    #print(ll)
    return (len(ll)>0,ll)
'''
Just positive value tester.
'''
def isPos(x):
    return 1 if x>0 else 0
'''
"safe" division:
First checks if denominator is zero; if it is, returns 0.
'''
def safeDiv (v1, v2):
    if v2 == 0:
        return 0
    else:
        return v1/v2
'''
Gets the set of all files with a particular extension.
'''
def getFlLst(flName, extension):
    flLst = []
    dirLst = [flName] if type(flName) is str else flName
    for dr in dirLst:
        for root,dirs, files in os.walk(dr):
            for filenm in files:
                if filenm.endswith(extension):
                    flLst.append(os.path.join(root,filenm))
    return flLst
