#!/usr/bin/env python

from AGammaD0Tohhpi0.data import datalib
import ROOT
from ROOT import RooFit
import sys

def set_plot_opts(hist, title = None, col = ROOT.kBlack, width = 1, style = 1):
    
    if title == None:
        title = hist.GetName()    

    hist.SetTitle(title)
    hist.SetLineColor(col)
    hist.SetLineWidth(int(width))
    hist.SetLineStyle(style)

def draw_bdt_cut(cut, tree, canv, method = "BDT"):

    #Plot signal, background and total using given BDT classifier output cut 
    canv.cd()
    sel = "selection_pass && inrange_all && D_IPCHI2_OWNPV < 9"
    tree.Draw("deltam >> h_sig(100, 140, 155)", sel + "&&" + method + "_output > "+str(cut))
    tree.Draw("deltam >> h_bg(100, 140, 155)", sel + "&&" + method + "_output < "+str(cut), "same")
    tree.Draw("deltam >> h_tot(100, 140, 155)", sel, "same")
    
    #Setting signal options
    h_sig = ROOT.gDirectory.Get("h_sig")
    h_sig.GetYaxis().SetRangeUser(0, 10000)
    set_plot_opts(h_sig, title = "Signal", width = 2)

    #Setting background options
    h_bg = ROOT.gDirectory.Get("h_bg")
    set_plot_opts(h_bg, title = "Background", col = ROOT.kGreen+2)
    
    #Setting total options
    h_tot = ROOT.gDirectory.Get("h_tot")
    set_plot_opts(h_tot, title = "Total", col = ROOT.kRed+1, style = 2)

    #Formatting overall plot
    canv.BuildLegend(0.55,0.6,0.9,0.9)
    canv.SetTitle(method+" output cut = "+str(cut))    


if __name__ == "__main__":

    c1 = ROOT.TCanvas("c1", "c1")
    c1.cd()    
    method = "BDT"

    if (len(sys.argv) < 2) or (sys.argv[1] not in ['Up', 'Down']):
        print "\nWarning: Polarisation not specified correctly. Defaulting to 'Up'."
        mag = "Up"
    else:
        mag = sys.argv[1]
    
    #Reading in data
    dataset_name = 'RealData_2015_Charm_Mag'+mag+'_pipipi0_Resolved_TriggerFiltered'
    #dataset_name = 'RealData_2017_Charm_Mag'+mag+'_pipipi0_Merged_TriggerFiltered'
    realtree = datalib.get_data(dataset_name)
        
    #Stops histogram data from printing on plot
    ROOT.gStyle.SetOptStat(0)

    draw_bdt_cut(0.1, realtree, c1, method = method)
    
    c2 = ROOT.TCanvas("c2", "c2")
    c2.cd()
    realtree.Draw(method+"_output", "selection_pass && inrange_all")
    
    def draw(cut, method = method):
        draw_bdt_cut(cut, realtree, c1, method = method)

