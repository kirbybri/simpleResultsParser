import sys
import string
from subprocess import check_call as call
import os
import ntpath
import glob
import struct
import json
import time
import pickle

def findKey(jsonObject, keyName ):
  if str(keyName) in jsonObject:
    varName = jsonObject[str(keyName)]
  else:
    print( "checkResults : Coult not find " + str(keyName) + " key, return" )
    return None
  return varName

def getTestResultsJsonFile(paramsFile, resultsFile):
  #check file path exists
  if (os.path.isfile( str(paramsFile) ) == False) or (os.path.isfile( str(resultsFile) ) == False):
    return None

  testResult = {}

  #get json data from params file
  with open(paramsFile) as json_file:
    try:
      param_data = json.load(json_file)
    except ValueError:
      print("checkResults : Invalid paramaters JSON file")
      return None

  #check if necessary entries in results dict
  param_var_names = ['operator_name','session_start_time','test_version','asic0id','asic1id','asic2id','asic3id','base_ind','gain_ind','shape_ind']
  for testVar in param_var_names :
    var = findKey(param_data, str(testVar) )
    if var == None:
      return None
    testResult[str(testVar)] = var

  #get json data from results file
  with open(resultsFile) as json_file:
    try:
      json_data = json.load(json_file)
    except ValueError:
      print("checkResults : Invalid results JSON file")
      return None

  #convert to dict for test_version=1, unfortunate
  jsonObject = json.loads(json_data)

  #check if necessary entries in results dict
  results_var_names = ['type','timestamp','status_do_analysis','results']
  for testVar in results_var_names :
    var = findKey(jsonObject, str(testVar) )
    if var == None:
      return None
    testResult[str(testVar)] = var

  #return dictionary summarizing one test
  return testResult

def processRunDir( rundir ):
  #check that rundir exists
  if os.path.isdir( str(rundir) ) == False:
    return None

  #find all result json files, keep track of corresponding param pairs
  jsonFiles = []
  for root, dirs, files in os.walk( str(rundir) ):
    for file in files:
      if file.endswith('results.json'):
        #get params + results file full path name
        paramsFile = str(root) + "/params.json"
        if os.path.isfile( str(paramsFile) ) == False:
          continue
        resultsFile = str(root) + "/" + str(file)
        if os.path.isfile( str(resultsFile) ) == False:
          continue
        #add to list of all tests for these ASICs
        jsonFiles.append( (paramsFile, resultsFile) )

  #detect empty directories
  if len(jsonFiles ) == 0 :
    print("getAllResults : No results found in " + str(rundir) )
    return None
  	
  #loop over configs from same "test run", get results in container
  runResults = []
  for test in jsonFiles:
    if len(test) != 2 :
      continue
    paramsFile = test[0]
    resultsFile = test[1]
    #print( str(paramsFile) + "\t" + str(resultsFile) )
    tempResult = getTestResultsJsonFile(paramsFile,resultsFile)
    if tempResult == None:
      continue
    #print(tempResult)
    runResults.append(tempResult)

  #return a list of dictionaries, each dictionary summarizes one test
  print( "getAllResults : Found " + str(len(runResults)) + " in " + str(rundir) )
  return runResults

def get_immediate_subdirectories(a_dir):
  if os.path.isdir( str(a_dir) ) == False :
    return None
  return [name for name in os.listdir(a_dir) if os.path.isdir(os.path.join(a_dir, name))]

def main():

  #test data directory - HARDCODED
  #testDir = "/dsk/1/data/oper/feasic/quadFeAsic/"

  if len(sys.argv) != 2 :
    print( "Usage: python getAllResults <results directory>")
    return
  testDir = sys.argv[1]
  print( str("Results directory : ") + str(testDir) )

  #get subdirectories
  subdirs = get_immediate_subdirectories(str(testDir))
  if subdirs == None :
    return  

  #open list of measurements, get all results
  allRuns = []
  for subdir in subdirs:
    rundir = str(testDir) + str(subdir)
    runResults = processRunDir( rundir )
    if runResults == None:
      continue
    allRuns.append(runResults)

  if len(allRuns) == 0 :
    print("getAllResults : No results found" )
    return
  print( "getAllResults : Found " + str(len(allRuns)) + " test directories")

  with open('outfile.json', 'w') as fout:
    json.dump(allRuns, fout)

if __name__ == '__main__':
    main()
