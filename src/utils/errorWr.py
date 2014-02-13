'''
Created on Nov 26, 2010

@author: Christie
'''
import sys
import traceback
def wrErr(isEnd = False,msg = None):
#    traceback.print_exc()
    if isEnd:
        xx = sys.exc_info()
        print('Error: ' +str(xx[1]))
        if msg != None:
            print(msg)
        exit(-1)
    else:
        raise Exception(sys.exc_info())
    
    
   
