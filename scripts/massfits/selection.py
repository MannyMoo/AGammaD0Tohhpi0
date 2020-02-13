#!/usr/bin/env python

from AGammaD0Tohhpi0.data import datalib
from AnalysisUtils.fit import multi_gauss, translate_and_scale_pdf, add_sideband_subtraction_weights
from AnalysisUtils.tmva import TMVADataLoader, TMVAClassifier
from AnalysisUtils.treeutils import copy_tree
from AnalysisUtils.addmva import add_mva_friend
from AGammaD0Tohhpi0.workspace import workspace
from AnalysisUtils.plot import plot_fit
import ROOT
from ROOT import RooFit
import sys	

### Fitting MC data ###

# mcdata = datalib.MC_2016_pipipi0_Dataset()
# mcmassbins = datalib.get_deltam_in_mass_bins_dataset('MC_2016_pipipi0')
# 
# dm = workspace.roovar('deltam')
# 
# cats = sorted(mcmassbins.catvals)
# mcpdfs = {}
# 
# # Make the PDF for the central bin.
# g1 = multi_gauss(workspace, 'dm_pdf_core', dm, [145.4, 145.2, 145.6], [(0.5, 0.5), (0.5, 1.5), 2.], 10.)
# corecat = cats[(len(cats)-1)/2]
# cats.remove(corecat)
# mcpdfs[corecat] = g1
# 
# # For the other bins
# for i, cat in enumerate(cats):
#     name = 'dm_pdf_' + str(i)
#     trans = workspace.roovar(name + '_translation', val = 0., error = 0.1, xmin = -10., xmax = 10.)
#     scale = workspace.roovar(name + '_scale', val = 1.1, error = 0.05, xmin = 0.8, xmax = 5.)
#     pdf = translate_and_scale_pdf(workspace, g1, name, dm, trans, scale,
#                                   workspace.roovar('dm_pdf_core_mean_0'))
#     mcpdfs[cat] = pdf
# 
# mcsimul = mcmassbins.make_roosimultaneous(mcpdfs)
# mcsimul.fitTo(mcmassbins.datahist)
#  
#     
### Now fitting real data ### 
 
if (len(sys.argv) < 2) or (sys.argv[1] not in ['Up', 'Down']):
    print "\nError: Polarisation not specified correctly."
    sys.exit()
else:
    mag = sys.argv[1]

#Reading in data
dataset_name = 'RealData_2015_Charm_Mag'+mag+'_pipipi0_Resolved_TriggerFiltered'
# #dataset_name = 'RealData_2017_Charm_Mag'+mag+'_pipipi0_Merged_TriggerFiltered'
# realdataset = datalib.get_dataset(dataset_name, update = True)
# realmassbins = datalib.get_deltam_in_mass_bins_dataset(dataset_name, update = True)
realtree = datalib.get_data(dataset_name)
  
# realpdfs, bg_fracs = {}, []
# 
# #RooDstD0BG is background pdf implemented in RooFit specifically to model D*-D0 mass distribution bg
# bgvar1 = workspace.roovar("bgvar1", val= 48.3, xmin=0., xmax=100.)
# bgvar2 = workspace.roovar("bgvar2", val=-17.4, xmin=-50., xmax=10.)
# bgvar3 = workspace.roovar("bgvar3", val=0.18, xmin=0.01, xmax=5.)
# #deltam0 = workspace.roovar("dm0", val=139.57) #Charged pion mass from pdg review 2019
# deltam0 = workspace.roovar("dm0", val=139.57, xmin=130., xmax=150.)
# bg_pdf = workspace.factory("RooDstD0BG", "bg_pdf", dm, deltam0, bgvar1, bgvar2, bgvar3)
# 
# #Getting category vals for d0 mass bins
# mccats = sorted(mcmassbins.catvals)
# realcats = sorted(realmassbins.catvals)
# 
# #Construct total pdf in each region by adding bg and signal pdf (fitted in each region from mc data) 
# for i, cat in enumerate(mccats):
#     frac = workspace.roovar("frac_"+str(i), val=1., error=0.01, xmin=0., xmax=1.)
#     bg_fracs.append(frac)
#     pdf = workspace.factory("RSUM", "total_pdf_"+str(i), *[frac.GetName() + "*" + bg_pdf.GetName(), mcpdfs[cat]])
#     realpdfs[realcats[i]] = pdf
# 
# #Creating simultaneous pdf and fitting to data
# real_simul = realmassbins.make_roosimultaneous(realpdfs)
# real_simul.fitTo(realmassbins.datahist)
# 
# 
# #Plotting fits and pulls
# plots = []
# signame = {realcats[0]: "dm_pdf_core_dm_pdf_0",
#            realcats[1]: "dm_pdf_core",
#            realcats[2]: "dm_pdf_core_dm_pdf_1" } #Since signal pdfs are currently defined by mc categories which we don't loop over 
# 
# sums = {}
# for cat, hist in realmassbins.datasets.items():
#     components = [  [ RooFit.Name("Total") ],
#                     [ RooFit.Components("bg_pdf"), RooFit.Name("BG"), RooFit.LineStyle(2), RooFit.LineColor(ROOT.kGreen+2) ], 
#                     [ RooFit.Components(signame[cat]), RooFit.Name("Signal"), RooFit.LineStyle(3), RooFit.LineColor(ROOT.kRed+2) ]
#                  ]
#     stuff = plot_fit(realpdfs[cat], hist, components=components)
#     plots.append(stuff)
#     canv = stuff['canv']
#     canv.SetName(cat)
#     canv.SetTitle(cat)
#     canv.Draw()
#     sums[signame[cat]] = hist.sumEntries()
# 
# 
# ### Cleaning up data ###
# #add_sideband_subtraction_weights(datalib, dataset_name, "weightTree", "weight", bg_pdf, dm, 143., 148., 150., dm.getMax(), extrabkgints = [(140, 143)])
# add_sideband_subtraction_weights(datalib, dataset_name, "weightTree", "weight", bg_pdf, dm, 143., 148., 150., 155.)#, extrabkgints = [(150., 155.)])  

cutstring = "inrange_all && selection_pass"

#Reduced varlist from top variables from Manchester+momenta, and acos(D_DIRA_OWNPV)
#varlist = ["piSoft_P", "piSoft_PT", "D_P", "D_PT", "D_CosTheta", "log(Dstr_FDCHI2_OWNPV)", "log(D_IPCHI2_OWNPV)", "pi0_CosTheta", 
#           "pi0_PT",  "Dstr_PT", "acos(D_DIRA_OWNPV)"]

#Full Manchester varlist + extra momenta  
#varlist = ["piSoft_PT", "Dstr_PT", "D_CosTheta", "log(Dstr_FDCHI2_OWNPV)", "log(D_IPCHI2_OWNPV)", 
#          "pi0_PT", "pi0_CosTheta", "acos(D_DIRA_OWNPV)", "pi0_P", "log(piSoft_IPCHI2_OWNPV)", "piSoft_P", "Dstr_P",
#          "D_P", "D_PT", "H1_PT", "H1_P", "H2_PT", "H2_P", "H1_PT + H2_PT"]

#Testing list of variables
varlist = ["log(Dstr_FDCHI2_OWNPV)", "pi0_PT", "D_CosTheta", "pi0_CosTheta"] 

  
dataloader = TMVADataLoader(realtree, realtree, varlist , signalweight = "weight", backgroundweight = "weight<0.", 
                            signalcut = cutstring, backgroundcut = cutstring)

method = "BDT"
classifier = TMVAClassifier(dataloader, [method], factoryoptions = TMVAClassifier.default_factory_options(Transformations = 'I'))
outputfile = ROOT.TFile.Open('train_out.root', 'RECREATE')
classifier.train_factory(outputfile)

#Adding BDT result to tree
add_mva_friend(datalib, dataset_name, "dataset/weights/TMVAClassification_"+method+".weights.xml", method, method+"_output", 
               perfile = False, overwrite = True)



###   Drawing signal peak after classifier cut   ###

from draw import draw_bdt_cut, set_plot_opts
from ROOT.TMVA import TMVAGui

#Refreshing to get classifier output branch
realtree = datalib.get_data(dataset_name)

#Stops statistics from being given on plot
ROOT.gStyle.SetOptStat(0)

#Drawing deltam distribution with some cut on classifier output
canv = ROOT.TCanvas("canv","canv")
canv.cd()
draw_bdt_cut(0.09, realtree, canv = canv, method = method)

tmf = "train_out.root"
TMVAGui(tmf)

