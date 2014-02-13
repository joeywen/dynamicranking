'''
Created on Dec 23, 2010
@author: Christie
'''
import process_qrels
import ranking.createQEvents
import ranking.createPaths
import ranking.evaluatePaths
import ranking.summarizeEvals

inputDir = 'web_input'
qesDir = 'web_qes'
pathsDir = 'web_paths'
evalsDir = 'web_evals'
#creates input directory
process_qrels.processTrecFl()
#creates query events
ranking.createQEvents.createQEvents(inputDir, qesDir, numQEvents = 20)
#creates paths by running ranking algorithm.
ranking.createPaths.createPaths(inputDir, qesDir, pathsDir, verbosity = 2)
#evaluates each path file created.
ranking.evaluatePaths.evaluatePaths(inputDir, pathsDir, evalsDir)
#summarizes evaluation by taking average over topics.
ranking.summarizeEvals.summarizeEval(evalsDir)