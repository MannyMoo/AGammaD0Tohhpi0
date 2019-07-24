#!/usr/bin/env python

from AGammaD0Tohhpi0.data import datalib
from AGammaD0Tohhpi0.selection import MC_sel_pipi_R, MC_sel_pipi_M, kin_allowed_sel, AND
from AGammaD0Tohhpi0.mint import pattern_D0Topipipi0, set_default_config
import ROOT

set_default_config()
ROOT.TH1.SetDefaultSumw2(True)

#Getting limits for Dalitz plot
pattern = pattern_D0Topipipi0
s13min = pattern.sijMin(1, 3)
s13max = pattern.sijMax(1, 3)
s23min = pattern.sijMin(2, 3)
s23max = pattern.sijMax(2, 3)

#Read in reconstructed and generated data, set string 'recosel' to select truth matched, kinematically allowed candidates
recotree = datalib.MC_2016_S28_Resloved_pipipi0_Dalitz_MagBoth()
recosel = AND(MC_sel_pipi_R, kin_allowed_sel)
recotree_M = datalib.MC_2016_S28_Merged_pipipi0_Dalitz_MagBoth()
recosel_M = AND(MC_sel_pipi_M, kin_allowed_sel)
gentree = datalib.MC_2016_Generator_pipipi0_Dalitz_MagBoth()




# ### Resolution ###

# c1 = ROOT.TCanvas("resolution", "resolution")
# nbinsRes = 100
# rmax = 3 * 10**5
# rmin = -1*rmax

# #Filling and fetching histogram h_res with residuals of S13
# recotree.Draw("S13 - true_S13_rec >> h_res({},{},{})".format(nbinsRes, rmin, rmax), recosel, "goff")
# h_res = ROOT.gDirectory.Get("h_res")

# #Fitting histogram with Gaussian to extract width (resolution on S13)
# f_res = ROOT.TF1("f_res", "[0]*TMath::Gaus(x, [1], [2])")
# f_res.SetParameters(h_res.GetMaximum(), h_res.GetMean(), h_res.GetStdDev())
# h_res.Fit(f_res)

# h_res.Draw()




### Efficiency ###

c2 = ROOT.TCanvas("efficiency", "efficiency")
ROOT.gStyle.SetOptStat(0)
nbins = 8

#Fill numerator histogram with true values (which are matched to reconstructed candidates) Dalitz plot and fetch 
recotree.Draw("true_S13_rec : true_S23_rec >> numerator({0},{1},{2},{0},{3},{4})".format(nbins, s13min, s13max, s23min, s23max), recosel, "goff")
numerator = ROOT.gDirectory.Get("numerator")
recotree_M.Draw("S13 : S23 >> temp({0},{1},{2},{0},{3},{4})".format(nbins, s13min, s13max, s23min, s23max), recosel_M, "goff")
temp = ROOT.gDirectory.Get("temp")
numerator.Add(numerator.Clone(), temp.Clone())

#Fill denominator histogram with Dalitz plot containing all events
gentree.Draw("true_S13 : true_S23 >> denominator({0},{1},{2},{0},{3},{4})".format(nbins, s13min, s13max, s23min, s23max), "","goff")
denominator = ROOT.gDirectory.Get("denominator")

#Dividing to get efficiency, and scaling so all points in range (0, 1)
h_efficiency = numerator.Clone()
h_efficiency.Divide(denominator.Clone())
h_efficiency.Scale(1/h_efficiency.GetMaximum())

#Fit with 2D (symmetric) polynomial to get efficiency function
f_eff = ROOT.TF2("f_eff", "[0] + [1]*(x+y) + [2]*(x^2 + y^2) + [3]*(x^3 + y^3)", s13min, s13max, s23min, s23max)
h_efficiency.Fit(f_eff)
h_efficiency.Draw("surf2")


