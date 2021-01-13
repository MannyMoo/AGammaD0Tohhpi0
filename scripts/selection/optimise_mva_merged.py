#!/usr/bin/env python

from AGammaD0Tohhpi0.data import datalib
from AGammaD0Tohhpi0.workspace import workspace
from AGammaD0Tohhpi0.pipipi0_utils import DmFitter3Pi, MERGED_SEL, MERGED_TRAIN_DATANAME
import pickle as pkl
import ROOT

ROOT.gROOT.SetBatch(True)

dm = workspace.roovar('deltam')
dataset = MERGED_TRAIN_DATANAME
rootstuff, results = [], []
method = 'BDT'

# make the signal PDF for the central bin.
core = workspace.factory('Gaussian::core(deltam, mean[145.4], sigma[0.3])')
johnson = workspace.factory('Johnson::johnson(deltam, mean, lambda[0.7], gamma[-0.5, 0.5], delta[1.])')
sig_pdf = workspace.factory('RSUM::sig_pdf(frac_core[0.,1.]*core, johnson)')

bg_pdf = workspace.factory("RooDstD0BG::bg_pdf(deltam,deltam0[139.57],c[2.],a[-0.5],b[0.])") 

fitter = DmFitter3Pi(datalib, dataset, sig_pdf, bg_pdf, workspace)
fitter.set_constant(['mean', 'sigma', 'lambda', 'b', 'c', 'deltam0'], flag=False)

mincut, maxcut, ncuts, effns, statsigs, cuts = -0.3, 0.3, 21, [], [], []
for i in range(ncuts):
    cut = mincut + i*(maxcut - mincut)/(ncuts - 1.)
    selection = MERGED_SEL + ' && '+method+' > {}'.format(cut)
    fitter.update_dataset(dataset, selection = selection , suffix = '_'+method.lower()+'_cut_{}'.format(i))
    fitter.fit_mc_data()
    results.append(fitter.fit_real_data())
    
    rootstuff.append(fitter.plot_real_fit(save = True, plotdir = 'opt_massfits/merged/', filesuffix ='_{}'.format(i)))

    nsig = sum([workspace.roovar('Nsig_{}'.format(j)).getVal() for j in range(2)])
    nsigerrSq = sum([workspace.roovar('Nsig_{}'.format(j)).getError()**2 for j in range(2)])
    nsigerr = nsigerrSq**0.5
    effns.append((nsig/nsigerr)**2)

    statsigs.append(fitter.get_signal_significance())
    cuts.append(cut) 


stuff = {'x' : cuts, 'effns' :effns, 'statsigs' : statsigs}
with open(method+'_merged_opts.pkl', 'wb') as f:
    pkl.dump(stuff, f)
