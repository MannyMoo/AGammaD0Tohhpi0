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
#info = datalib.get_data_info('MINT_data_3SigmaCPV')
info = datalib.get_data_info('MINT_time-indepedent')
fdata = TFile.Open(info['files'][0])
evtlist = DalitzEventList(fdata.Get('DalitzEventList'))

# Get the phase difference calculator.
pattern = DalitzEventPattern(421, 211, -211, 111)
diffcalc = PhaseDifferenceCalc(pattern, config)

# Plot of the phase differences.
hphasediffs = ROOT.TH1F('phasediffs', '', 100, 0., 2.*math.pi)

# D0 mass minus pi+ mass
mmax = (1864.8 - 139)**2

hdalitz = ROOT.TH2F('dalitz', '', 100, 0, mmax, 100, 0, mmax)

# Plot of the phase differences as a function of Dalitz position.
hphasedalitz = ROOT.TH3F('phasedalitz', '', 100, 0., mmax, 100, 0., mmax, 100, 0., 2.*math.pi)


# Loop over events.
for evt in evtlist :
    phasediff = diffcalc.phase_difference(evt)
    s13 = evt.s(1, 3)
    s23 = evt.s(2, 3)
    # The binning is inverted in the lower half of the Dalitz plot, so invert the phase difference.
    if s23 < s13 :
        phasediff *= -1
    # Use the convention that phases run from 0 to 2pi rather than -pi to +pi.
    if phasediff < 0. :
        phasediff += 2*math.pi
    hphasediffs.Fill(phasediff)
    hdalitz.Fill(s13, s23)
    hphasedalitz.Fill(s13, s23, phasediff)

c1 = ROOT.TCanvas()
hphasediffs.Draw()

c2 = ROOT.TCanvas('c2', '', 600, 600)
# Make the 2D projection of mean phase difference in each Dalitz bin.
pphasedalitz = hphasedalitz.Project3DProfile()
pphasedalitz.Draw('colz')

c3 = ROOT.TCanvas('c3', '', 600, 600)
hdalitz.Draw()
