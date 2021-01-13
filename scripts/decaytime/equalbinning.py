#!/usr/bin/env/python

import ROOT
from AGammaD0Tohhpi0.data import datalib
from AnalysisUtils.treeutils import tree_loop, TreeFormula
from AGammaD0Tohhpi0.pipipi0_utils import RESOLVED_SEL, RESOLVED_TRAIN_DATANAME
from AGammaD0Tohhpi0.pipipi0_utils import MERGED_SEL, MERGED_TRAIN_DATANAME
import pandas as pd
from array import array

def equal_bins(df, var = 'decaytime', nbins = 10, weightvar = 'weight', dt = 1e-4):
    nperbin = df[weightvar].sum()/float(nbins)
    bins, t = [], 0
    for i in range(nbins+1):
        wsum = 0
        while(wsum < nperbin*i):
            t += dt
            wsum = df.query(var+' < {}'.format(t))[weightvar].sum()
        bins.append(t)
    return bins

def equal_bins_efficient(df, tmin = 0., tmax = 10., var = 'decaytime', nbins = 10, weightvar = 'weight', prec = 0.01):
    bins = [tmin] + [tmax for i in range(nbins)]
    wtot = df[weightvar].sum()
    for i in range(1,nbins):
        lower, upper = tmin, tmax
        wsum = df.query('{} < '.format(bins[i-1]) + var + ' < {}'.format(bins[i]))[weightvar].sum()
        while( abs( (wsum*nbins)/wtot - 1) > prec):
            if wsum > wtot/nbins:
                upper = bins[i]
                bins[i] += (lower - bins[i])/2.
            else:
                lower = bins[i]
                bins[i] += (upper - bins[i])/2.
    return bins


ROOT.gStyle.SetOptStat(0)

lifetime = 0.4101

#weightvar = "SidebandWeightsTree.sideband_weight"
weightvar = "BDTFilteredWeightsTree.weight"
#selection = RESOLVED_SEL + ' && BDT > 0.1'
selection = MERGED_SEL + ' && BDT > -0.28'

tree = datalib.get_data(MERGED_TRAIN_DATANAME)
weight = TreeFormula(weightvar, weightvar, tree)
time = TreeFormula("decaytime", "decaytime", tree)

data = []
for i in tree_loop(tree, selection):
    if weight() != 0. and time() > 0.: 
        data.append( (time(), weight()) )    

nbins = 3
df = pd.DataFrame(columns = ['decaytime', 'weight'], data = data)
timebins = map(lambda x: x/lifetime, equal_bins(df, nbins = nbins))

timehist = ROOT.TH1F('timehist', 'Decay time hist', len(timebins)-1, array('d', timebins))
for i in tree_loop(tree, selection):
    timehist.Fill(time()/lifetime, weight())

timehist.Draw()

#altbins = equal_bins_efficient(df, nbins = nbins)
