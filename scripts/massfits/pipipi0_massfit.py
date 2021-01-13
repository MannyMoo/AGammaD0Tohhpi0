#!/usr/bin/env python

from AGammaD0Tohhpi0.data import datalib
from AGammaD0Tohhpi0.workspace import workspace
import ROOT
from AGammaD0Tohhpi0.pipipi0_utils import DmFitter3Pi, RESOLVED_TRAIN_DATANAME, RESOLVED_SEL, MERGED_TRAIN_DATANAME, MERGED_SEL
from AnalysisUtils.fit import add_sideband_subtraction_weights

ROOT.gROOT.SetBatch(False)
rootstuff, results, chi2s = [], [], []

lifetime = 0.4101
dm = workspace.roovar('deltam')
dataname = MERGED_TRAIN_DATANAME
basesel = MERGED_SEL

bg_pdf = workspace.factory("RooDstD0BG::bg_pdf(deltam,deltam0[139.57],c[2.],a[-0.5],b[-1.])") 

fitter = DmFitter3Pi(datalib, dataname, None, bg_pdf, workspace, selection = 'inrange_all', suffix = '_no_cuts')
fitter.set_constant(['c', 'deltam0'], flag=False)

#resolved : timebins = [0., 1.17, 1.54, 1.97, 2.59, 100./lifetime]
timebins = [0., 1.44, 2.08, 100./lifetime] 
sigmalist = []
for i in range(1, len(timebins)):

    sel = basesel + ' && BDT > -0.28 && decaytime > {} && decaytime < {}'.format(lifetime*timebins[i-1], lifetime*timebins[i])
    suffix = '_timebin_{}'.format(i-1)
    fitter.update_dataset(dataname, selection = sel, suffix = suffix)

    results.append(fitter.fit_mc_data())
    results.append(fitter.fit_real_data(constants=['sigmacoeff']))

    chi2s.append(fitter.get_chi2()) 
    sigmalist.append(fitter.get_sigmas())

    rootstuff.append(fitter.plot_real_fit(save = False, plotdir = 'update-2021-01-12/', filesuffix = '_timebin_{}'.format(i-1)))

for r in results : r.Print()

