#!/usr/bin/env python

from AGammaD0Tohhpi0.data import datalib
from AGammaD0Tohhpi0.workspace import workspace
import ROOT
from AGammaD0Tohhpi0.pipipi0_utils import DmFitter3Pi, RESOLVED_TRAIN_DATANAME, RESOLVED_SEL
from AnalysisUtils.fit import add_sideband_subtraction_weights

ROOT.gROOT.SetBatch(False)
rootstuff, results = [], []

dm = workspace.roovar('deltam')
dataset = RESOLVED_TRAIN_DATANAME

# make the signal PDF for the central bin.
gauss_core = workspace.factory('Gaussian::core(deltam, mean[145.4], sigma[0.3])')
johnson = workspace.factory('Johnson::johnson(deltam, mean, lambda[0.7], gamma[-0.5, 0.5], delta[1.])')
sig_pdf = workspace.factory('RSUM::sig_pdf(frac_core[0.,1.]*core, johnson)')

bg_pdf = workspace.factory("RooDstD0BG::bg_pdf(deltam,deltam0[139.57],c[2.],a[-0.5],b[0.])")  

fitter = DmFitter3Pi(datalib, dataset, sig_pdf, bg_pdf, workspace, selection = RESOLVED_SEL, suffix = '_pre_mva_cut')
fitter.set_constant(['mean', 'sigma', 'lambda', 'b', 'c', 'deltam0'], flag=False)
#fitter.fit_mc_data()
#results.append(fitter.fit_real_data())

#add_sideband_subtraction_weights(datalib, dataset, "SidebandWeightsTree", "sideband_weight", fitter.bg_pdf, dm, 
#                                 144.5, 146.5, 152., 155., datasetsel = RESOLVED_SEL) 

chi2s = []
for dataname in datalib.get_matching_datasets("RealData.*pipipi0_Resolved_TriggerFiltered$"):
    if dataname != RESOLVED_TRAIN_DATANAME: continue
    sel = RESOLVED_SEL
    suffix = '_pre_mva_cut' 
    fitter.update_dataset(dataname, selection = sel, suffix = suffix)

    results.append(fitter.fit_mc_data())
    results.append(fitter.fit_real_data(constants = [])) 
    chi2s.append(fitter.get_chi2())
    rootstuff += [fitter.plot_real_fit(plotdir = '../temp/', save = False, filesuffix = '')]

for r in results : r.Print()
