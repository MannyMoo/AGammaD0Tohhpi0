#!/usr/bin/env python

from AGammaD0Tohhpi0.data import datalib
from AnalysisUtils.fit import multi_gauss, translate_and_scale_pdf
from AGammaD0Tohhpi0.workspace import workspace
import ROOT
from ROOT import RooFit
from math import sqrt


def fit_mc(dm, mcmassbins):
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
    
    return mcpdfs
 

def fit_data(dm, realmassbins, mcmassbins, mcpdfs):  
    realpdfs, bg_fracs = {}, []
    
    #RooDstD0BG is background pdf implemented in RooFit specifically to model D*-D0 mass distribution bg
    bgvar1 = workspace.roovar("bgvar1", val= 48.3, xmin=0., xmax=100.)
    bgvar2 = workspace.roovar("bgvar2", val=-17.4, xmin=-50., xmax=10.)
    bgvar3 = workspace.roovar("bgvar3", val=0.18, xmin=0.01, xmax=5.)
    #deltam0 = workspace.roovar("dm0", val=139.57) #Charged pion mass from pdg review 2019
    deltam0 = workspace.roovar("dm0", val=139.57, xmin=130., xmax=150.)
    bg_pdf = workspace.factory("RooDstD0BG", "bg_pdf", dm, deltam0, bgvar1, bgvar2, bgvar3)
    
    #Getting category vals for d0 mass bins
    mccats = sorted(mcmassbins.catvals)
    realcats = sorted(realmassbins.catvals)
    
    #Construct total pdf in each region by adding bg and signal pdf (fitted in each region from mc data) 
    for i, cat in enumerate(mccats):
        frac = workspace.roovar("frac_"+str(i), val=1., error=0.01, xmin=0., xmax=1.)
        bg_fracs.append(frac)
        pdf = workspace.factory("RSUM", "total_pdf_"+str(i), *[frac.GetName() + "*" + bg_pdf.GetName(), mcpdfs[cat]])
        realpdfs[realcats[i]] = pdf
    
    #Creating simultaneous pdf and fitting to data
    real_simul = realmassbins.make_roosimultaneous(realpdfs)
    real_simul.fitTo(realmassbins.datahist)

    return realpdfs, bg_fracs



if __name__ == "__main__":

    dm = workspace.roovar('deltam')

    cutval, dval = -1., 0.05
    sel = "Dstr_FIT_CHI2 < 30 && Dstr_FIT_CHI2 > 0 && H1_PIDK < -5 && H2_PIDK < -5"
    mcpdfs, realpdfs, bg_fracs = {}, {}, []
    x, y = [], [] # Arrays to feed to TGraph for plotting S/sqrt(S+B) later    

    while cutval <= 1.:
    
        print "\n\nProcessing at BDT cut of {} ...\n\n".format(cutval)
    
        # Read in datasets with cut applied     
        mcmassbins = datalib.get_deltam_in_mass_bins_dataset('MC_2016_pipipi0', suffix = "_BDT_ge_{}".format(cutval), 
                                                              selection = "BDT >= {}".format(cutval), update = True)    
        dataset_name = 'RealData_2015_Charm_MagUp_pipipi0_Resolved_TriggerFiltered'
        realmassbins = datalib.get_deltam_in_mass_bins_dataset(dataset_name, suffix = "_BDT_ge_{}".format(cutval), 
                                                                selection = sel + " && BDT >= {}".format(cutval), update = True)
        realcats = sorted(realmassbins.catvals)    

        # Fit mc data for signal shape
        mcpdfs = fit_mc(dm, mcmassbins)
    
        # Fit real data with mc signal shape
        realpdfs, bg_fracs = fit_data(dm, realmassbins, mcmassbins, mcpdfs)    
    
        # Calculate S, tot=S+B --> S/sqrt(S+B)
        Ntot, Nsig = 0, 0
        for i in range(3): # Looping over mass bins
            bg_f = bg_fracs[i].getValV()
            n = realmassbins.datasets[realcats[i]].sumEntries() # Total number of events in given mass bin
            Ntot += n
            Nsig += (1-bg_f) * n # bg_f is fraction of bg pdf within total pdf, i.e. fraction of bg events
       
        x.append(cutval)
        y.append(Nsig / sqrt(Ntot))
 
        cutval += dval
        break # So we just run through once for testing


    # Plotting S/sqrt(S+B) vs BDT cut value
    plot = ROOT.TGraph(len(x))
    for i in range(len(x)):
        plot.SetPoint(i, x[i], y[i])

    plot.Draw("A*")



