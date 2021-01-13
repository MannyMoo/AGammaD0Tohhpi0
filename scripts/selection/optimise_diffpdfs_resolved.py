#!/usr/bin/env python

from AGammaD0Tohhpi0.data import datalib
from AGammaD0Tohhpi0.workspace import workspace
from AGammaD0Tohhpi0.pipipi0_utils import DmFitter3Pi, RESOLVED_TRAIN_DATANAME, RESOLVED_SEL
import pickle as pkl
import ROOT
from math import sqrt

ROOT.gROOT.SetBatch(True)

dm = workspace.roovar('deltam')
dataset = RESOLVED_TRAIN_DATANAME
rootstuff = []
method = 'BDT'


mincut, maxcut, ncuts, effns, statsigs, cuts = -0.25, 0.35, 13, [], [], []
nsigs, nbgs, results = [], [], []
for i in range(ncuts):
    cut = mincut + i*(maxcut - mincut)/(ncuts - 1.)
    selection = RESOLVED_SEL + ' && '+method+' > {}'.format(cut)

    bg_pdf = workspace.factory("RooDstD0BG::bg_pdf(deltam,deltam0[139.57],c[2.],a[-0.5],b[-1.])") 
    fitter = DmFitter3Pi(datalib, dataset, None, bg_pdf, workspace, selection = selection , suffix = '_'+method.lower()+'_cut_{}'.format(i))
    fitter.set_constant(['b', 'c', 'deltam0'], flag=False)
    
    results.append(fitter.fit_mc_data())
    results.append(fitter.fit_real_data(constants=['sigmacoeff']))
    
    if i == 0: fitter.set_constant(['b', 'c', 'deltam0', 'gamma', 'mean', 'sigma', 'sigma_dm_pdf_0', 'sigma_dm_pdf_1', 'sigmacoeff'])

    rootstuff.append(fitter.plot_real_fit(save = True, plotdir = 'opt_massfits/resolved/', filesuffix ='_{}'.format(i)))

    nsig = sum([workspace.roovar('Nsig_{}'.format(j)).getVal() for j in range(3)])
    nerr = sqrt( sum( [workspace.roovar('Nsig_{}'.format(j)).getError()**2 for j in range(3)] ) ) 
    effns.append((nsig/nerr)**2)
  
    statsigs.append(fitter.get_signal_significance())
    cuts.append(cut) 

    nsigs.append(nsig)
    nbgs.append(sum([workspace.roovar('Nbg_{}'.format(j)).getVal() for j in range(3)]))


stuff = {'x' : cuts, 'effns' :effns, 'statsigs' : statsigs}
with open(method+'_resolved_opts.pkl', 'wb') as f:
    pkl.dump(stuff, f)
