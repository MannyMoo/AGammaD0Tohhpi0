#!/usr/bin/env python

from AGammaD0Tohhpi0.data import datalib
from AGammaD0Tohhpi0.workspace import workspace
from AGammaD0Tohhpi0.pipipi0_utils import DmFitter3Pi, MERGED_TRAIN_DATANAME, MERGED_SEL
import pickle as pkl
import ROOT
from math import sqrt

ROOT.gROOT.SetBatch(True)

results, chi2s = [], []
dm = workspace.roovar('deltam')
dataset = MERGED_TRAIN_DATANAME
rootstuff = []
method = 'BDT'

bg_pdf = workspace.factory("RooDstD0BG::bg_pdf(deltam,deltam0[139.57],c[2.],a[-0.5],b[-1.])") 
fitter = DmFitter3Pi(datalib, dataset, None, bg_pdf, workspace, selection = MERGED_SEL)
fitter.set_constant(['b', 'c', 'deltam0'], flag=False)

results.append(fitter.fit_mc_data())    

mincut, maxcut, ncuts, effns, statsigs, cuts = -0.5, 0.25, 15, [], [], []
for i in range(ncuts):
    cut = mincut + i*(maxcut - mincut)/(ncuts - 1.)
    selection = MERGED_SEL + ' && '+method+' > {}'.format(cut)

    fitter.update_dataset(dataset, selection = selection, suffix = '_'+method.lower()+'_cut_{}'.format(i))

    #fitter.fit_mc_data()
    results.append(fitter.fit_real_data()) 
    if i == 0: fitter.set_constant(['b', 'c', 'deltam0', 'gamma', 'mean', 'sigma', 'sigma_dm_pdf_0', 'sigma_dm_pdf_1', 'sigmacoeff'])
    chi2s.append(fitter.get_chi2())

    rootstuff.append(fitter.plot_real_fit(save = True, plotdir = 'opt_massfits/merged/', filesuffix ='_{}'.format(i)))

    nsig = sum([workspace.roovar('Nsig_{}'.format(j)).getVal() for j in range(3)])
    nerr = sqrt( sum( [workspace.roovar('Nsig_{}'.format(j)).getError()**2 for j in range(3)] ) ) 
    effns.append((nsig/nerr)**2)
  
    statsigs.append(fitter.get_signal_significance())
    cuts.append(cut) 

stuff = {'x' : cuts, 'effns' :effns, 'statsigs' : statsigs}
with open(method+'_merged_opts.pkl', 'wb') as f:
    pkl.dump(stuff, f)
