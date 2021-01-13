#!/usr/bin/env python

from AGammaD0Tohhpi0.data import datalib
from AGammaD0Tohhpi0.workspace import workspace
import ROOT
from AGammaD0Tohhpi0.pipipi0_utils import DmFitter3Pi, MERGED_TRAIN_DATANAME, MERGED_SEL
from AnalysisUtils.fit import add_sideband_subtraction_weights

ROOT.gROOT.SetBatch(False)
rootstuff = []
results, chi2s = [], []

dm = workspace.roovar('deltam')
dataset = MERGED_TRAIN_DATANAME

# make the signal PDF for the central bin.
core = workspace.factory('Gaussian::core(deltam, mean[145.4], sigma[0.3])')
johnson = workspace.factory('Johnson::johnson(deltam, mean, lambda[0.7], gamma[-0.5, 0.5], delta[1.])')
sig_pdf = workspace.factory('RSUM::sig_pdf(frac_core[0.,1.]*core, johnson)')

bg_pdf = workspace.factory("RooDstD0BG::bg_pdf(deltam,deltam0[139.57],c[2.],a[-0.5],b[-3.])") 

fitter = DmFitter3Pi(datalib, dataset, sig_pdf, bg_pdf, workspace, selection = MERGED_SEL, update = True)
fitter.set_constant(['mean', 'sigma', 'lambda', 'a', 'b',  'c', 'deltam0'], flag=False)
fitter.fit_mc_data()
results.append(fitter.fit_real_data())

for r in results: r.Print()
