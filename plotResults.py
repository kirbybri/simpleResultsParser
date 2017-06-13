import sys
import string
from subprocess import check_call as call
import os
import ntpath
import glob
import struct
import json
import time
import datetime

from ROOT import gROOT, gPad, TCanvas, TF1, TH1F, TH2I, TProfile, TGraph, TFile
gROOT.Reset()
import time

runDates = {}

#canvas and generic histograms
c1 = TCanvas( 'evtDisp', 'All Channels', 1500, 1000 )
h_mean_test = TH1F( 'h_mean_test','',2000,0,20000)
h_rms_test = TH1F( 'h_rms_test','',2000,0,200)
h_badch_test = TH1F( 'h_badch_test','',64,0-0.5,64-0.5)

#configuration variable lookup, global variables
gainNames = ["4.7mV/fC","7.8mV/fC","14mV/fC","25mV/fC"]
shapeNames = ["0.5us","1us","2us","3us"]
baseNames = ["200mV","900mV"]

#hardcoded cut limits
cutLimitValues = [[2585.0, 2598.184246981991, 66.08869276144222], [7235.0, 7235.750346466047, 28.638532587610346], [2585.0, 2595.3462603878115, 65.2214486600767], [7245.0, 7247.602929532858, 28.354417228566803], [2615.0, 2627.3312883435583, 62.721031954660944], [7275.0, 7270.809259992086, 28.84342282883049], [2635.0, 2647.3669107460914, 62.06469902230914], [7295.0, 7293.563514048278, 28.2694757503699], [2595.0, 2613.8125865822285, 64.44034442189678], [7245.0, 7244.043942992874, 28.34467978067012], [2605.0, 2615.8153572135366, 63.86248449783976], [7265.0, 7262.834092258959, 28.204028579788137], [2645.0, 2660.342438638163, 61.621510260250425], [7295.0, 7300.33544429052, 28.864507454878858], [2675.0, 2693.426677221453, 61.57313663070041], [7335.0, 7337.472799208705, 28.83525293871399], [2615.0, 2630.5124653739613, 63.61212398515421], [7255.0, 7258.9244013457355, 28.220805048436745], [2635.0, 2646.8401266323704, 62.67150875761793], [7295.0, 7292.001781120127, 28.17798799252695], [2725.0, 2719.1729323308273, 61.62277994170311], [7365.0, 7358.764589515331, 29.627625857545304], [2765.0, 2781.206964780372, 62.323414989590155], [7425.0, 7425.999010880317, 30.15638433782274], [2635.0, 2656.834190740008, 63.007805767387104], [7285.0, 7284.220265188997, 28.185188969878805], [2675.0, 2698.1525826241837, 62.424590341298966], [7345.0, 7343.089865399842, 28.876656365958024], [2805.0, 2821.4080744112407, 62.49402354258331], [7455.0, 7461.79263949347, 30.804760314870826], [2915.0, 2934.4320205818326, 64.5900312368788], [7575.0, 7579.02414885194, 32.06562776767223], [4.625, 5.003366336633663, 0.6466745125667284], [4.375, 4.6454828814565605, 0.561743811351909], [5.125, 5.2915017807677085, 0.6511897047374066], [4.875, 4.895829210370077, 0.43110786677820156], [5.625, 5.721336633663366, 0.6372134926322804], [5.375, 5.391485148514851, 0.40417134671102883], [5.875, 6.04165010927876, 0.5551109495146919], [5.875, 5.775534441805226, 0.42497113613669674], [6.875, 7.268252869014642, 0.9728237330566221], [6.625, 6.986891571032845, 0.9470394496267681], [7.625, 7.864859517214088, 0.9107688842281999], [7.375, 7.519419156936474, 0.7206796136471042], [8.625, 8.631831683168317, 0.7906964353388474], [8.625, 8.441607284243863, 0.6828745320007656], [9.375, 9.289489311163896, 0.7699651129903503], [9.125, 9.230927171977044, 0.7253932214919832], [11.625, 12.205217606330367, 1.753079628004169], [11.375, 11.963229475766568, 1.7840525918831485], [13.125, 13.268599129402453, 1.4271378642391082], [12.625, 13.020825089038386, 1.303762849654727], [15.375, 14.947170557973882, 1.2749867732873117], [15.125, 15.0050949742778, 1.250976077509188], [16.375, 16.349871388998814, 1.3098122633024685], [16.625, 16.503512069647805, 1.4086170173667785], [19.375, 20.874159081915316, 3.0827906071612206], [19.375, 20.593836565096954, 3.047996603056552], [22.375, 22.994014641867828, 2.4052499009570636], [22.875, 23.162791848041156, 2.5393677860589285], [25.875, 26.47304115552038, 2.303787920498645], [27.375, 26.843391373169766, 2.7137732586091454], [28.375, 28.67065690542145, 2.409856925520438], [27.875, 28.71680846853977, 2.392852306099216], [179.5, 179.4664416203336, 2.6252322652962836], [179.5, 179.7239221140473, 2.8447000988481883], [176.5, 176.84167162993845, 1.8392292326181905], [175.5, 175.90341473099068, 1.803106603059931], [172.5, 173.18314472900536, 1.9324660545822747], [171.5, 171.79586973788722, 1.8221757549258617], [172.5, 172.5897537728356, 1.947352701646549], [170.5, 170.806454816286, 1.8865614869354261], [107.5, 107.91489572989076, 1.664172548790351], [107.5, 108.04310687326182, 1.7709047565677174], [106.5, 106.12641509433962, 1.0760816403107916], [105.5, 106.00029791459781, 1.05581564860589], [103.5, 103.77408142999008, 1.0952427260287096], [103.5, 103.35240365514501, 1.0869376411696325], [103.5, 103.29030976965846, 1.171762614378468], [103.5, 103.2027402700556, 1.1555029596706934], [60.5, 60.3875868917577, 1.1082765439463353], [77.5, 77.30751730959446, 1.7385894405456304], [59.5, 59.21232876712329, 0.6600070964722131], [74.5, 74.61594776414721, 1.6123076424664895], [57.5, 57.76072279586974, 0.6607501346750474], [75.5, 75.66511581864977, 1.6809631709801713], [57.5, 57.510127084988085, 0.6537731142239139], [76.5, 76.08074103427779, 1.696792859844406], [43.5, 43.24915924826904, 0.9799103621580322], [88.5, 88.71507716660071, 4.177293926794367], [41.5, 41.22926974074807, 0.8814154150283655], [91.5, 91.69397661977412, 4.6207699721556175], [41.5, 41.55268369974252, 0.9482537698818089], [94.5, 95.42089611419509, 4.993362714976938], [38.5, 38.13054675118859, 0.8228571184323147], [95.5, 99.06139226991245, 14.260092010782015]]

#make summary plots, global variables
g_all = []
h_all = []
h_cumul = []
for g in range(0,4,1):
  for s in range(0,4,1):
    for b in range(0,2,1):
      config_ind = 8*int(g) + 2*int(s) + int(b)
      configName = str(gainNames[int(g)]) + " " + str(shapeNames[int(s)]) + " " + str(baseNames[int(b)])

      #make graphs
      g_meanVsChan = TGraph()
      g_meanVsChan.SetTitle("Channel Pedestal Mean")
      g_meanVsChan.GetXaxis().SetTitle("Channel Number")
      g_meanVsChan.GetYaxis().SetTitle("Pedestal Mean (ADC counts)")
      
      g_rmsVsChan = TGraph()
      g_rmsVsChan.SetTitle("Channel Pedestal RMS")
      g_rmsVsChan.GetXaxis().SetTitle("Channel Number")
      g_rmsVsChan.GetYaxis().SetTitle("Pedestal RMS (ADC counts)")

      g_gainVsChan = TGraph()
      g_gainVsChan.SetTitle("Channel Gain")
      g_gainVsChan.GetXaxis().SetTitle("Channel Number")
      g_gainVsChan.GetYaxis().SetTitle("Gain (e- / ADC)")

      g_encVsChan = TGraph()
      g_encVsChan.SetTitle("Channel ENC")
      g_encVsChan.GetXaxis().SetTitle("Channel Number")
      g_encVsChan.GetYaxis().SetTitle("ENC (e-)")

      g_meanVsChan.SetMarkerStyle(21)
      g_rmsVsChan.SetMarkerStyle(21)
      g_gainVsChan.SetMarkerStyle(21)
      g_encVsChan.SetMarkerStyle(21)
      g_all.append( [g_meanVsChan, g_rmsVsChan, g_gainVsChan, g_encVsChan] )

      #make histograms
      name = "h_meanVsChan_intPulser_" + str(g) + "_" + str(s) + "_" + str(b)
      h_meanVsChan = TH1F(name,"",2000,0,20000)
      h_meanVsChan.SetTitle("Pedestal Mean, " + configName )
      h_meanVsChan.GetXaxis().SetTitle("Pedestal Mean (ADC counts)")
      h_meanVsChan.GetYaxis().SetTitle("Number of Channels / 10 ADC counts")
      h_meanVsChan.GetYaxis().SetTitleOffset(2)

      name = "h_rmsVsChan_intPulser_" + str(g) + "_" + str(s) + "_" + str(b)
      h_rmsVsChan = TH1F(name,"",200,0,50)
      h_rmsVsChan.SetTitle("Pedestal RMS, " + configName )
      h_rmsVsChan.GetXaxis().SetTitle("Pedestal RMS (ADC counts)")
      h_rmsVsChan.GetYaxis().SetTitle("Number of Channels / 0.25 ADC counts")
      h_rmsVsChan.GetYaxis().SetTitleOffset(2)

      name = "h_gainVsChan_intPulser_" + str(g) + "_" + str(s) + "_" + str(b)
      h_gainVsChan = TH1F(name,"",200,0,200)
      h_gainVsChan.SetTitle("Gain, " + configName )
      h_gainVsChan.GetXaxis().SetTitle("Channel Gain (e- / ADC count)")
      h_gainVsChan.GetYaxis().SetTitle("Number of Channels")
      h_gainVsChan.GetYaxis().SetTitleOffset(2)

      name = "h_encVsChan_intPulser_" + str(g) + "_" + str(s) + "_" + str(b)
      h_encVsChan = TH1F(name,"",250,0,2500)
      h_encVsChan.SetTitle("ENC, " + configName )
      h_encVsChan.GetXaxis().SetTitle("ENC (e-)")
      h_encVsChan.GetYaxis().SetTitle("Number of Channels / 10 e-")
      h_encVsChan.GetYaxis().SetTitleOffset(2)

      h_meanVsChan.SetLineColor(1 + int(s) )
      h_rmsVsChan.SetLineColor(1 + int(s) )
      h_gainVsChan.SetLineColor(1 + int(s) )
      h_encVsChan.SetLineColor(1 + int(s) )

      h_all.append( [h_meanVsChan, h_rmsVsChan, h_gainVsChan, h_encVsChan] )

def findKey(jsonObject, keyName ):
  if str(keyName) in jsonObject:
    varName = jsonObject[str(keyName)]
  else:
    return None
  return varName

def isTestValid(test_data):
  param_var_names = ['operator_name','session_start_time','test_version','asic0id','asic1id','asic2id','asic3id','base_ind','gain_ind','shape_ind','results']
  for testVar in param_var_names :
    var = findKey(test_data, str(testVar) )
    if var == None:
      return 0
  try:
    asicNum = int( findKey(test_data, str('asic0id') ) )
  except ValueError:
    return 0
  try:
    asicNum = int( findKey(test_data, str('asic1id') ) )
  except ValueError:
    return 0
  try:
    asicNum = int( findKey(test_data, str('asic2id') ) )
  except ValueError:
    return 0
  try:
    asicNum = int( findKey(test_data, str('asic3id') ) )
  except ValueError:
    return 0
  return 1

def processTest(test_data, testNum, asicNum):

  #check if necessary entries in results dict
  isTestValid(test_data)

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
    h_all[config_ind][0].Fill( float(mean) )
    h_all[config_ind][1].Fill( float(rms) )
    h_all[config_ind][2].Fill( float(gain) )
    h_all[config_ind][3].Fill( float(enc) )
    h_mean_test.Fill(float(mean))
    h_rms_test.Fill(float(rms))
    
    #apply cut
    result = applyCuts(mean, chNum, 0,5 , config_ind)
    if result == 0 :
      print "Bad channel " + str(chNum)
      h_badch_test.SetBinContent(int(chNum)+1,1)
    result = applyCuts(rms, chNum, 1, 10, config_ind)
    if result == 0 :
      print "Bad channel " + str(chNum)
      h_badch_test.SetBinContent(int(chNum)+1,1)
    result = applyCuts(gain, chNum, 2, 5, config_ind)
    if result == 0 :
      print "Bad channel " + str(chNum)
      h_badch_test.SetBinContent(int(chNum)+1,1)

def applyCuts(var, ch,type_ind,cutLevel,config_ind):
  varVal = float(var)
  chVal = int(ch)
  #pedestal mean cuts
  if type_ind == 0 :
    maxBin = cutLimitValues[0 + config_ind][0]
    rms = cutLimitValues[0 + config_ind][2]
    if varVal > maxBin + cutLevel*rms :
      return 0

  #rms cuts
  if type_ind == 1 :
    maxBin = cutLimitValues[32 + config_ind][0]
    rms = cutLimitValues[32 + config_ind][2]
    if chVal >= 48 :
      rms = rms*1.25
    if varVal > maxBin + cutLevel*rms :
      return 0
    if varVal < maxBin - cutLevel*rms :
      return 0

  #gain cuts
  if type_ind == 2 :
    maxBin = cutLimitValues[64 + config_ind][0]
    rms = cutLimitValues[64 + config_ind][2]
    if config_ind < 24 :
      if varVal < maxBin - cutLevel*rms :
        return 0
  return 1

def plotInternalAsicResults(plotType):
  for g in range(0,4,1):
    for s in range(0,4,1):
      for b in range(0,2,1):
        config_ind = 8*int(g) + 2*int(s) + int(b)
        if b == 0 :
          g_all[config_ind][0].GetYaxis().SetRangeUser(2400,3200)
        if b == 1 :
          g_all[config_ind][0].GetYaxis().SetRangeUser(7000,7800)
        g_all[config_ind][1].GetYaxis().SetRangeUser(0,40)
        g_all[config_ind][2].GetYaxis().SetRangeUser(0,200)

  graphNum = int(plotType)
  if (graphNum < 0) or (graphNum > 2 ):
    return
  bInd = int(1) #0 = 200mV, 1 = 900mV
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

def clearGraphs():
  for g in range(0,4,1):
    for s in range(0,4,1):
      for b in range(0,2,1):
        config_ind = 8*int(g) + 2*int(s) + int(b)
        g_all[config_ind][0].Set(0)
        g_all[config_ind][1].Set(0)
        g_all[config_ind][2].Set(0)
        g_all[config_ind][3].Set(0)

def plotOverallDistributions():
  for g in range(0,4,1):
    for s in range(0,4,1):
      for b in range(0,2,1):
        config_ind = 8*int(g) + 2*int(s) + int(b)
        h_all[config_ind][0].GetXaxis().SetRangeUser(1000,9000)

  graphNum = 2
  bInd = 1
  c1.Clear()
  c1.Divide(4,2)
  for pad in range(0,4,1):
    padNum = int(pad)
    c1.cd(padNum+1)
    h_all[0+8*padNum+bInd][graphNum].SetStats(0)
    h_all[0+8*padNum+bInd][graphNum].Draw()
    h_all[2+8*padNum+bInd][graphNum].Draw("same")
    h_all[4+8*padNum+bInd][graphNum].Draw("same")
    h_all[6+8*padNum+bInd][graphNum].Draw("same")
  bInd = 1
  for pad in range(0,4,1):
    padNum = int(pad)
    c1.cd(4+padNum+1)
    h_all[0+8*padNum+bInd][graphNum].SetStats(0)
    h_all[0+8*padNum+bInd][graphNum].Draw()
    h_all[2+8*padNum+bInd][graphNum].Draw("same")
    h_all[4+8*padNum+bInd][graphNum].Draw("same")
    h_all[6+8*padNum+bInd][graphNum].Draw("same")
  c1.Update()

  check = raw_input("Press key to continue")

def saveOverallDistributions():
  f = TFile("output_analyzeResults.root", "recreate")

  for g in range(0,4,1):
    for s in range(0,4,1):
      for b in range(0,2,1):
        config_ind = 8*int(g) + 2*int(s) + int(b)
        h_all[config_ind][0].Write()
        h_all[config_ind][1].Write()
        h_all[config_ind][2].Write()
        h_all[config_ind][3].Write()

  f.Close()

def deriveCuts():
  cutLimits = []

  cutLevel = 5
  for plot in range (0,1,1):
    for g in range(0,4,1):
      for s in range(0,4,1):
        for b in range(0,2,1):
          plotType = int(plot)
          config_ind = 8*int(g) + 2*int(s) + int(b)

          maxBin = h_all[config_ind][plotType].GetBinCenter( h_all[config_ind][plotType].GetMaximumBin() )
          rms = h_all[config_ind][plotType].GetRMS()

          lowBin = float(maxBin) - float(cutLevel)*float(rms)
          if lowBin < h_all[config_ind][plotType].GetBinCenter( 1 ) :
            lowBin = h_all[config_ind][plotType].GetBinCenter( 1 )
          highBin = float(maxBin) + float(cutLevel)*float(rms)
          if highBin > h_all[config_ind][plotType].GetBinCenter( h_all[config_ind][plotType].GetNbinsX() ) :
            highBin = h_all[config_ind][plotType].GetBinCenter( h_all[config_ind][plotType].GetNbinsX() )
          h_all[config_ind][plotType].GetXaxis().SetRangeUser( lowBin , highBin )

          maxBin = h_all[config_ind][plotType].GetBinCenter( h_all[config_ind][plotType].GetMaximumBin() )
          mean =  h_all[config_ind][plotType].GetMean()
          rms = h_all[config_ind][plotType].GetRMS()

          #print str(plotType) + "\t" + str(g) + "\t" + str(s) + "\t" + str(b) + "\t" + str(maxBin) + "\t" + str(mean) + "\t" + str(rms)
          print str(g) + "\t" + str(s) + "\t" + str(b) + "\t" + str(maxBin) + "\t" + str(round(mean,2)) + "\t" + str(round(rms,2))

          cutLimits.append([maxBin,mean,rms])

          c1.Clear()
          h_all[config_ind][plotType].Draw()
          c1.Update()
          #check = raw_input("Press key to continue")

  print cutLimits

def processRun(run):

  #sort timestamps, get run ID, check that run is ok
  isValid = 1
  isFirst = 1
  isMismatch = 0
  index = 0
  numEmpty = 0
  testTimes = {}
  runId = ""
  asicNum = []
  for test in run:
    if len(test) == 0 :
      numEmpty = numEmpty + 1
      continue
    session_start_time = test['session_start_time']
    timeStamp = test['timestamp']
    testTimes[timeStamp] = index
    index = index + 1
    if isFirst == 1:
      runId = str(session_start_time)
      isFirst = 0
    elif str(session_start_time) != runId :
      isMismatch = 1
    if isTestValid(test) == 0:
      isValid = 0
    elif len(asicNum) == 0:
      asicNum.append( int( test['asic0id'] ) )
      asicNum.append( int( test['asic1id'] ) )
      asicNum.append( int( test['asic2id'] ) )
      asicNum.append( int( test['asic3id'] ) )

  runDate = int(runId[0:8])
  if (isValid == 0 ) or (isMismatch == 1 ):
    return None

  #hardcode requirement for number of tests here, not ideal
  if index != 45 :
    return None

  #skip test runs
  if asicNum == [0,0,0,0] :
    return None

  #identify if "bad run"
  badRunList = ["20170604T212913","20170605T084459","20170604T145806","20170604T163105","20170604T200140","20170604T213043","20170604T152952","20170609T184038"]
  for badRun in badRunList:
    if str(runId) == str(badRun) :
      return None

  #map index in record to order in test sequence (lame)
  test_order = {}
  testNum = 0
  for k in sorted(testTimes):
   index = testTimes[k]
   test_order[str(index)] = testNum
   testNum = testNum + 1

  #clear graphs
  clearGraphs()
  h_mean_test.Reset()
  h_rms_test.Reset()
  h_badch_test.Reset()

  print str(runId)

  #actually process tests in "good" run
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
      processTest( test, testNum , asicNum )
      h_mean_test.GetXaxis().SetRangeUser(0.5,19999.5)
      meanRms = h_mean_test.GetRMS()
      if meanRms > 2000 : 
        isBadRun = 1

  #c1.Clear()
  #h_badch_test.Draw()
  #c1.Update()
  #check = raw_input("Press key to continue")

  #Make internal pulser plots
  #if (asicNum[0] == 71) or (asicNum[1] == 71) or (asicNum[2] == 71) or (asicNum[3] == 71) :
  #  print asicNum
  #  plotInternalAsicResults(0)

def main():

  #open list of measurements, get all results
  with open('outfile.json') as json_data:
    data = json.load(json_data)

  """
  runCount = 0
  for run in data:
    result = processRun( run )
    if result == None:
      continue
    runCount = runCount + 1
  """
  
  with open('outfile_hothdaq1.json') as json_data:
    data = json.load(json_data)
  print "Data length : " + str(len(data))

  runCount = 0
  for run in data:
    result = processRun( run )
    if result == None:
      continue
    runCount = runCount + 1

  with open('outfile_hothdaq2.json') as json_data:
    data = json.load(json_data)
  print "Data length : " + str(len(data))

  for run in data:
    result = processRun( run )
    if result == None:
      continue
    runCount = runCount + 1
  print "Good run count : " + str(runCount)
  

  plotOverallDistributions()
  saveOverallDistributions()
  #deriveCuts()
  
if __name__ == '__main__':
    main()
