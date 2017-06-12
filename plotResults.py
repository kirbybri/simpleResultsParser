"""
from builtins import range
from builtins import int
from builtins import str
from builtins import hex
from builtins import object
"""
import sys
import string
from subprocess import check_call as call
import os
import ntpath
import glob
import struct
import json
import time

from ROOT import gROOT, gPad, TCanvas, TF1, TH1F, TH2I, TProfile, TGraph
gROOT.Reset()
import time

c1 = TCanvas( 'evtDisp', 'All Channels', 1400, 1000 )
#g_encVsCh = TGraph( )
#g_gainVsCh = TGraph( )
#h_encAll = TH1F( 'h_encAll', 'ENC Distribution, All Chips : 14mV/fC,1us,200mV',150,0,1500)
h_mean_test = TH1F( 'h_mean_test','',2000,0,20000)
h_rms_test = TH1F( 'h_rms_test','',2000,0,200)
#get config specific plots

g_all = []
for g in range(0,4,1):
  for s in range(0,4,1):
    for b in range(0,2,1):
      config_ind = 8*int(g) + 2*int(s) + int(b)
      g_meanVsChan = TGraph()
      g_rmsVsChan = TGraph()
      g_gainVsChan = TGraph()
      g_encVsChan = TGraph()
      g_meanVsChan.SetMarkerStyle(21)
      g_rmsVsChan.SetMarkerStyle(21)
      g_gainVsChan.SetMarkerStyle(21)
      g_encVsChan.SetMarkerStyle(21)
      g_all.append( [g_meanVsChan, g_rmsVsChan, g_gainVsChan, g_encVsChan] )

def findKey(jsonObject, keyName ):
  if str(keyName) in jsonObject:
    varName = jsonObject[str(keyName)]
  else:
    #print( "checkResults : Coult not find " + str(keyName) + " key, return" )
    return None
  return varName

def processTest(test_data, testNum):

  #check if necessary entries in results dict
  param_var_names = ['operator_name','session_start_time','test_version','asic0id','asic1id','asic2id','asic3id','base_ind','gain_ind','shape_ind','results']
  for testVar in param_var_names :
    var = findKey(test_data, str(testVar) )
    if var == None:
      return None

  gain_ind = int(test_data['gain_ind'])
  shape_ind = int(test_data['shape_ind'])
  base_ind = int(test_data['base_ind'])
  if (gain_ind < 0) or (gain_ind > 3 ):
    return None
  if (shape_ind < 0) or (shape_ind > 3 ):
    return None
  if (base_ind < 0) or (base_ind > 3 ):
    return None
  config_ind = 8*int(gain_ind) + 2*int(shape_ind) + int(base_ind)
  g_all[config_ind][0].Set(0)
  g_all[config_ind][1].Set(0)
  g_all[config_ind][2].Set(0)
  g_all[config_ind][3].Set(0)
  h_mean_test.Reset()
  h_rms_test.Reset()

  results = test_data['results']
  for ch_data in results:
    chNum = findKey( ch_data, 'ch' )
    if chNum == None :
      continue
    enc = ch_data['enc']
    gain = ch_data['gain']
    mean = ch_data['mean']
    rms = ch_data['rms']
    g_all[config_ind][0].SetPoint(  g_all[config_ind][0].GetN(),  int(chNum), float(mean) )
    g_all[config_ind][1].SetPoint(  g_all[config_ind][1].GetN(),  int(chNum), float(rms) )
    g_all[config_ind][2].SetPoint(  g_all[config_ind][2].GetN(),  int(chNum), float(gain) )
    g_all[config_ind][3].SetPoint(  g_all[config_ind][3].GetN(),  int(chNum), float(enc) )
    h_mean_test.Fill(float(mean))
    h_rms_test.Fill(float(rms))

def plotInternalAsicResults():
  for g in range(0,4,1):
    for s in range(0,4,1):
      for b in range(0,2,1):
        config_ind = 8*int(g) + 2*int(s) + int(b)
        g_all[config_ind][1].GetYaxis().SetRangeUser(0,40)
        g_all[config_ind][2].GetYaxis().SetRangeUser(0,200)

  graphNum = int(1)
  bInd = int(0) #0 = 200mV, 1 = 900mV
  c1.Clear()
  c1.Divide(2,2)
  for pad in range(0,4,1):
    padNum = int(pad)
    c1.cd(padNum+1)
    g_all[0+2*padNum+bInd][graphNum].Draw("ALP")
    g_all[8+2*padNum+bInd][graphNum].Draw("LP")
    g_all[16+2*padNum+bInd][graphNum].Draw("LP")
    g_all[24+2*padNum+bInd][graphNum].Draw("LP")
  c1.Update()

  check = raw_input("Press key to continue")

def processRun(run):

  #sort timestamps
  testTimes = {}
  index = 0
  for test in run:
    if len(test) == 0 :
      continue
    timeStamp = test['timestamp']
    testTimes[timeStamp] = index
    index = index + 1

  #hardcode requirement for number of tests here, not ideal
  if index != 45 :
    return None

  #map index in record to order in test sequence
  test_order = {}
  testNum = 0
  for k in sorted(testTimes):
   index = testTimes[k]
   test_order[str(index)] = testNum
   testNum = testNum + 1

  #clear graphs
  for g in range(0,4,1):
    for s in range(0,4,1):
      for b in range(0,2,1):
        config_ind = 8*int(g) + 2*int(s) + int(b)
        g_all[config_ind][0].Set(0)
        g_all[config_ind][1].Set(0)
        g_all[config_ind][2].Set(0)
        g_all[config_ind][3].Set(0)
  h_mean_test.Reset()
  h_rms_test.Reset()

  #actually process tests
  index = 0
  isBadRun = 0
  for test in run:
    if len(test) == 0 :
      continue
    timeStamp = test['timestamp']
    testNum = int(test_order[str(index)])
    index = index + 1

    #analyze internal pulser gain measurement
    testType = test['type']
    if (testType == 'quadFeAsic_gain') and (testNum < 32) :
      processTest( test, testNum )
      h_mean_test.GetXaxis().SetRangeUser(0.5,19999.5)
      meanRms = h_mean_test.GetRMS()
      if meanRms > 2000 : 
        isBadRun = 1

  #identify bad runs
  print isBadRun
 
  #Make internal pulser plots
  plotInternalAsicResults()
  #print( "Number of good tests " + str(count) )

def main():

  #open list of measurements, get all results
  with open('outfile_hothdaq2.json') as json_data:
    data = json.load(json_data)

  for run in data:
    processRun( run )

if __name__ == '__main__':
    main()
