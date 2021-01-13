#!/usr/bin/env/python

import ROOT
from AGammaD0Tohhpi0.data import datalib
from AnalysisUtils.treeutils import tree_loop, TreeFormula
from AGammaD0Tohhpi0.pipipi0_utils import RESOLVED_SEL, RESOLVED_TRAIN_DATANAME
from array import array

ROOT.gStyle.SetOptStat(0)

lifetime = 0.4101

#weightvar = "SidebandWeightsTree.sideband_weight"
weightvar = "BDTFilteredWeightsTree.weight"
selection = RESOLVED_SEL

tree = datalib.get_data(RESOLVED_TRAIN_DATANAME)
weight = TreeFormula(weightvar, weightvar, tree)
time = TreeFormula("decaytime", "decaytime", tree)

timehist = ROOT.TH1F('timehist', 'Decay time histogram', 100, 0., 6.)
timehistbg = ROOT.TH1F('timehistbg', 'Decay time histogram (bkg.)', 100, 0., 6.)
for i in tree_loop(tree, selection):
    timehist.Fill(time()/lifetime, weight())
    #if weight() < 0.:
    #    timehistbg.Fill(time()/lifetime)

for i in tree_loop(tree, 'deltam > 152.'):
    timehistbg.Fill(time()/lifetime)

timehist.SetLineColor(ROOT.kBlue)
timehist.SetFillColor(ROOT.kAzure-4)
timehist.SetFillStyle(1001)
timehist.SetLineWidth(2)

timehist.GetXaxis().SetTitle('t/#tau')
timehist.GetYaxis().SetTitle('Normalised Events / {} [t/#tau]'.format(timehist.GetBinWidth(0)))

timehistbg.SetLineColor(ROOT.kRed) 
timehistbg.SetFillColor(ROOT.kRed)
timehistbg.SetFillStyle(3354)
timehistbg.SetLineWidth(2)

print timehist.GetSumOfWeights()
timehist.Scale(1./timehist.GetMaximum())
timehistbg.Scale(1./timehistbg.GetMaximum())

canv = ROOT.TCanvas('canv', '')
timehist.Draw('hist')
timehistbg.Draw('same hist')
