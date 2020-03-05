#!/usr/bin/env python

from AGammaD0Tohhpi0.data import datalib
from AnalysisUtils.fit import multi_gauss, translate_and_scale_pdf
from AGammaD0Tohhpi0.workspace import workspace
import ROOT
from ROOT import RooFit
from math import sqrt
from AnalysisUtils.plot import plot_fit

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
    realpdfs, NbgList, NsigList = {}, [], []
    
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
        Ntot = realmassbins.datasets[realcats[i]].sumEntries()
        Nbg = workspace.roovar("Nbg_"+str(i), xmin = 0., xmax = Ntot)
        Nsig = workspace.roovar("Nsig_"+str(i), xmin = 0., xmax = Ntot)
  
        NbgList.append(Nbg)
        NsigList.append(Nsig)
  
        pdf = workspace.factory("SUM", "total_pdf_"+str(i), *[Nbg.GetName() + "*" + bg_pdf.GetName(), Nsig.GetName() + "*" + mcpdfs[cat].GetName()])
        realpdfs[realcats[i]] = pdf
    
    #Creating simultaneous pdf and fitting to data
    real_simul = realmassbins.make_roosimultaneous(realpdfs)
    real_simul.fitTo(realmassbins.datahist)

    return realpdfs, NbgList, NsigList



if __name__ == "__main__":

    dm = workspace.roovar('deltam')

    cutval, dval, count = -1., 0.05, 0
    sel = "Dstr_FIT_CHI2 < 30 && Dstr_FIT_CHI2 > 0 && H1_PIDK < -5 && H2_PIDK < -5"
    mcpdfs, realpdfs, bg_fracs = {}, {}, []
    x, y1, y2 = [], [], [] # Arrays to feed to TGraph for plotting S/sqrt(S+B) or (S/errS)^2 later    


    # Fit mc data for signal shape
    mcmassbins = datalib.get_deltam_in_mass_bins_dataset('MC_2016_pipipi0', update = True)    
    mcpdfs = fit_mc(dm, mcmassbins)

    # List to store plots at each cut value
    plots = []

    while cutval <= 1.:
    
        # For testing smaller cut range - allows datasets to be named same way which means they don't need completely remade
        if cutval < -0.85:
            cutval = round(cutval + dval, 2)
            count += 1
            continue
        
        print "\n\nProcessing at BDT cut of {} ...\n\n".format(cutval)
    
        # Read in dataset with cut applied     
        dataset_name = 'RealData_2015_Charm_MagUp_pipipi0_Resolved_TriggerFiltered'
        realmassbins = datalib.get_deltam_in_mass_bins_dataset(dataset_name, suffix = "_BDT_cut_{}".format(count), 
                                                                selection = sel + " && BDT >= {}".format(cutval), update = True)
        realcats = sorted(realmassbins.catvals)    
    
        # Fit real data with mc signal shape
        realpdfs, NbgList, NsigList = fit_data(dm, realmassbins, mcmassbins, mcpdfs)    
    
        # Calculate S, tot=S+B --> S/sqrt(S+B)
        Nbg, Nsig, errNsigSq = 0, 0, 0.     
        for i in range(len(NbgList)):
            Nbg += NbgList[i].getValV()
            Nsig += NsigList[i].getValV()    
            errNsigSq += NsigList[i].getError() ** 2
        
        errNsig = errNsigSq ** 0.5

        x.append(cutval)
        y1.append(Nsig / sqrt(Nbg+Nsig))
        y2.append(Nsig*Nsig / errNsig*errNsig) 

        #Plotting fits and pulls
        #drawlist = [-1.0, -0.5, 0.1, 0.5, 1.0]
        drawlist = []
        if cutval in drawlist:
            plots.append([])
            j = 0        
            signame = {realcats[0]: "dm_pdf_core_dm_pdf_0",
                       realcats[1]: "dm_pdf_core",
                       realcats[2]: "dm_pdf_core_dm_pdf_1" } #Since signal pdfs are currently defined by mc categories which we don't loop over 
            for cat, hist in realmassbins.datasets.items():
                components = [  [ RooFit.Name("Total") ],
                                [ RooFit.Components("bg_pdf"), RooFit.Name("BG"), RooFit.LineStyle(2), RooFit.LineColor(ROOT.kGreen+2) ], 
                                [ RooFit.Components(signame[cat]), RooFit.Name("Signal"), RooFit.LineStyle(3), RooFit.LineColor(ROOT.kRed+2) ]
                             ]
                stuff = plot_fit(realpdfs[cat], hist, components=components)
                plots[j].append(stuff)
                canv = stuff['canv']
                canv.SetName(cat)
                canv.SetTitle("cut_eq_" + str(cutval))
                canv.Draw()
            j += 1
    
        cutval = round(cutval + dval, 2) # Rounding avoids values like "0.49999..." since dval has finite precision    
        count += 1


    # Plotting S/sqrt(S+B) OR (S/errS)^2 vs BDT cut value
    def plotGraph(x, y, cname):
        plot = ROOT.TGraph(len(x))
        canv = ROOT.TCanvas(cname, cname)
        for i in range(len(x)):
            plot.SetPoint(i, x[i], y[i])
        
        plot.Draw("A*")
        return plot, canv


    #print x, "\n", [val/max(y1) for val in y1], "\n", [val/max(y2) for val in y2]

    p1, c1 = plotGraph(x, y1, "S/sqrt(S+B) vs BDT cut")
    p2, c2 = plotGraph(x, y2, "(S/errS)^2 vs BDT cut")
