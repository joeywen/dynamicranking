'''
Created on Dec 23, 2010
@author: Christie
'''

import ranking.createQEvents
import ranking.createPaths
import ranking.evaluatePaths
import ranking.summarizeEvals

inputDir = 'interactive_input'
qesDir = 'interactive_qes'
pathsDir = 'interactive_paths'
evalsDir = 'interactive_evals'
#probability clicking if relevant
prClickIfRel = 1
#probability of the user clicking if the document is not relevant.
prClickIfNotRel = 0

import process_qrels
#creates the input files
process_qrels.processTrecFl()
#creates query events
ranking.createQEvents.createQEvents(inputDir, qesDir, numQEvents = 20, 
                                    prClickIfRel= prClickIfRel,
                                   prClickIfNotRel = prClickIfNotRel)
#calculates paths using the ranking algorithm
ranking.createPaths.createPaths(inputDir, qesDir, pathsDir, 
                                prClickIfRel= prClickIfRel,
                                algorithmType = ['DM','SM'],
                                utilityMetric = ['DCG'],
                                prClickIfNotRel = prClickIfNotRel,
                                verbosity = 2)
#evaluates paths
ranking.evaluatePaths.evaluatePaths(inputDir, pathsDir, evalsDir)
#summarizes evaluation results over all topics
ranking.summarizeEvals.summarizeEval(evalsDir)