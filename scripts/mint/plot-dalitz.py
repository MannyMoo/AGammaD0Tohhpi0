#!/usr/bin/env python

# Load Mint2 libraries.
import Mint2
from AGammaD0Tohhpi0.data import datalib
from ROOT import DalitzEvent
from AGammaD0Tohhpi0.mint import set_default_config
import ROOT

set_default_config()

tree = datalib.get_data('MINT_test-kkpi0')

tree.GetEntry(0)
evt = DalitzEvent()
evt.fromTree(tree)
pattern = evt.eventPattern()

s12min, s12max = pattern.sijMin(1,2), pattern.sijMax(1,2)
s13min, s13max = pattern.sijMin(1,3), pattern.sijMax(1,3)
s23min, s23max = pattern.sijMin(2,3), pattern.sijMax(2,3)

# makes histograms for these variables and fills their values as it loops over the events
# 1D histograms for each variable, and a 2D histogram for m^2(K+pi0) vs m^2(K-pi0)

c1 = ROOT.TCanvas('c1','Histogram',500,500)
h1 = ROOT.TH1F("h1","s12 = m^2(K+K-)",50,s12min,s12max)
h2 = ROOT.TH1F("h2","s13 = m^2(K+pi0)",50,s13min,s13max)
h3 = ROOT.TH1F("h3","s23 = m^2(K-pi0)",50,s23min,s23max)
h4 = ROOT.TH2F("h4"," m^2(K+pi0) vs m^2(K-pi0)/s13 vs s23",50,s13min,s13max,50,s23min,s23max)

e1=[]
e2=[]
e3=[]
N=[]

for i in xrange(tree.GetEntries()):
    tree.GetEntry(i)
    evt = DalitzEvent()
    evt.fromTree(tree)
    
    tag = tree.tag
    s12 = evt.s(1,2) # s12 = m^2(K+K-)
    s13 = evt.s(1,3) # s13 = m^2(K+pi0)
    s23 = evt.s(2,3) # s23 = m^2(K-pi0)

    e1.append(s12)
    e2.append(s13)
    e3.append(s23)

    h1.Fill(s12)
    h2.Fill(s13)
    h3.Fill(s23)
    h4.Fill(s13,s23)

#h1.Fill(e1)
#h2.Fill(e2)
#h3.Fill(e3)
#h4.Fill(e2,e3)


c1.Divide(2,2)
c1.cd(1)
h1.Draw()
c1.cd(2)
h2.Draw()
c1.cd(3)
h3.Draw()
c1.cd(4)
h4.Draw()

#separate histograms for D0 (tag == 1) and D0bar (tag == -1), so 8 histograms in total
