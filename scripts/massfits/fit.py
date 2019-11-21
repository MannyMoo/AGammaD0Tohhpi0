#!/usr/bin/env python

from AGammaD0Tohhpi0.data import datalib
from AnalysisUtils.fit import multi_gauss, translate_and_scale_pdf
from AGammaD0Tohhpi0.workspace import workspace
from AnalysisUtils.plot import plot_fit
import ROOT
from ROOT import RooFit

mcdata = datalib.MC_2016_pipipi0_Dataset()
mcmassbins = datalib.get_deltam_in_mass_bins_dataset('MC_2016_pipipi0')

dm = workspace.roovar('deltam')

cats = sorted(mcmassbins.catvals)
mcpdfs = {}

# Make the PDF for the central bin.
g1 = multi_gauss(workspace, 'dm_pdf_core', dm, [145.4, 145.2, 145.6], [(0.5, 0.5), (0.5, 1.5), 2.], 10.)
corecat = cats[(len(cats)-1)/2]
cats.remove(corecat)
mcpdfs[corecat] = g1

# For the other bins
for i, cat in enumerate(cats):
    name = 'dm_pdf_' + str(i)
    trans = workspace.roovar(name + '_translation', val = 0., error = 0.1, xmin = -10., xmax = 10.)
    scale = workspace.roovar(name + '_scale', val = 1.1, error = 0.05, xmin = 0.8, xmax = 5.)
    pdf = translate_and_scale_pdf(workspace, g1, name, dm, trans, scale,
                                  workspace.roovar('dm_pdf_core_mean_0'))
    mcpdfs[cat] = pdf

mcsimul = mcmassbins.make_roosimultaneous(mcpdfs)
mcsimul.fitTo(mcmassbins.datahist)

plots = []
for cat, hist in mcmassbins.datasets.items():
    stuff = plot_fit(mcpdfs[cat], hist)
    plots.append(stuff)
    canv = stuff['canv']
    canv.SetName(cat)
    canv.SetTitle(cat)
    canv.Draw()
    
