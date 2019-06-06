#!/usr/bin/env python

# Load Mint2 libraries.
import Mint2, ROOT, math
from AGammaD0Tohhpi0.data import datalib
from ROOT import PhaseDifferenceCalc, DalitzEventList, TFile, DalitzEventPattern
from ROOT.MINT import NamedParameterBase
from AGammaD0Tohhpi0.mint import config

# Set the config file.
NamedParameterBase.setDefaultInputFile(config)

# Retrieve the dataset as a DalitzEventList
fdata = TFile.Open('/nfs/lhcb/d2hh01/hhpi0/data/mint/data_3SigmaCPV/pipipi0_1.root')
evtlist = DalitzEventList(fdata.Get('DalitzEventList'))
evtData = fdata.Get('DalitzEventList')

# Get the phase difference calculator.
pattern = DalitzEventPattern(421, 211, -211, 111)
diffcalc = PhaseDifferenceCalc(pattern, config)

nbinsPhase = 17
nbinsTime = 25
tMax = 3

D0_decayTimeHist = ROOT.TH2F("D0 Phase Binned Decay Times", '', nbinsTime, 0, tMax, nbinsPhase, -2.*math.pi, 2.*math.pi)
D0bar_decayTimeHist = ROOT.TH2F("D0bar Phase Binned Decay Times", '', nbinsTime, 0, tMax, nbinsPhase, -2.*math.pi, 2.*math.pi)

# Loop over events.
i = 0
for evt in evtData :
    phasediff = diffcalc.phase_difference(evtlist[i])
    s13 = evtlist[i].s(1, 3)
    s23 = evtlist[i].s(2, 3)
    tag = evt.tag
    decayTime = evt.decaytime

    #Ensure all phases in 0->2pi region
    if phasediff < 0. :
        phasediff += 2*math.pi

    #Add to phase binned decay time histogram based on tag (D0 or D0bar)
    if (tag == 1) : 
        if s13 < s23 :
            D0_decayTimeHist.Fill(decayTime, phasediff)
        else : 
            D0_decayTimeHist.Fill(decayTime, -1*phasediff)
    elif(tag == -1) :
        if s13 > s23 :
            D0bar_decayTimeHist.Fill(decayTime, phasediff)
        else : 
            D0bar_decayTimeHist.Fill(decayTime, -1*phasediff)

    i += 1


c1 = ROOT.TCanvas("c1", "D0 to D0bar ratios by phase")


phaseBin = 12
D0_hist = D0_decayTimeHist.ProjectionX("D0", phaseBin, phaseBin)
D0bar_hist = D0bar_decayTimeHist.ProjectionX("D0bar", phaseBin, phaseBin)
plot = ROOT.TGraphErrors(nbinsTime)

for i in range(nbinsTime) : 

    D0_count = D0_hist.GetBinContent(i)
    D0bar_count = D0bar_hist.GetBinContent(i)

    if (D0bar_count != 0) and (D0_count != 0) :
        x = i*( float(tMax)/nbinsTime )
        y = float(D0_count)/D0bar_count
        err_y =  float(D0_count)/D0bar_count * math.sqrt( (1/float(D0_count)) + (1/float(D0bar_count)) ) 

        plot.SetPoint(i, x, y)
        plot.SetPointError(i, 0, err_y)


plot.Draw("A*")


    


    
    

    

