from AGammaD0Tohhpi0.data import datalib
from ROOT import RooDataSet, RooDataHist, RooRealVar, RooGaussian, RooArgList, RooArgSet, RooAddPdf, RooFormulaVar, RooGenericPdf, RooDstD0BG, RooCategory, RooSimultaneous
from ROOT.RooFit import RooConst, Components, LineStyle, LineColor, MarkerColor, Import, Index, Cut, Slice, ProjWData
from ROOT import kRed, kGreen, kCyan, TCanvas, TPad, TH1
from AnalysisUtils.makeroodataset import make_roodatahist
import sys

if len(sys.argv) == 2 :
    mag = sys.argv[1]

lo_dataset = datalib.get_dataset('Data_2015_pipipi0_Resolved_Mag'+mag+'_LowMass')
mid_dataset_raw = datalib.get_dataset('Data_2015_pipipi0_Resolved_Mag'+mag)
hi_dataset = datalib.get_dataset('Data_2015_pipipi0_Resolved_Mag'+mag+'_HighMass')
dataset_sig = datalib.get_dataset('MC_2016_pipipi0')

#deltam = m_D* - m_D0
deltam = lo_dataset.get(0)["deltam"]
deltam.setMax(155)
dm_min = deltam.getMin()
dm_max = deltam.getMax()


##### Dividing dataset based on D0 mass #####

#Define allowed regionsi
regions = ["lo_mid", "mid", "hi_mid"]
n_regions= len(regions)

#Create index for RooFit to distinguish regions
regionIndex = RooCategory("regionIndex", "regionIndex")
for i in range(n_regions) :
    regionIndex.defineType(regions[i])

lo_mass_cut = 1830
hi_mass_cut = 1900
lo_mid_dataset = mid_dataset_raw.reduce("D0_mass < "+str(lo_mass_cut))
mid_dataset = mid_dataset_raw.reduce("D0_mass >= "+str(lo_mass_cut)+" && D0_mass <= "+str(hi_mass_cut))
hi_mid_dataset = mid_dataset_raw.reduce("D0_mass > "+str(hi_mass_cut))

#Create new dataset separated by region
dataset = RooDataSet("dataset_"+mag, "dataset_"+mag, RooArgSet(deltam), Index(regionIndex), Import("lo_mid", lo_mid_dataset), Import("mid", mid_dataset), Import("hi_mid", hi_mid_dataset))
datahist = dataset.binnedClone()

##############################################


########### Fitting Pure Signal ##############

draw_p_sig = True

#Initial parameters for signal components
init_m = [145.4, 145.1, 148.3]
init_w = [0.37, 1, 5]
w_min = 0
w_max = 10

#Number of separate pdfs which make up the signal
n_sig_pdf = 3

#'p_' prefix indicates parameters/functions for pure signal
p_means, p_widths, p_gauss = [], [], []

#Create signal components - 3 Gaussians for now
for i in range(n_sig_pdf) :
    p_means.append(RooRealVar("p_mean_{}".format(i), "p_mean_{}".format(i), init_m[i], dm_min, dm_max))
    p_widths.append(RooRealVar("p_width_{}".format(i), "p_width_{}".format(i), init_w[i], w_min, w_max))
    p_gauss.append(RooGaussian("p_gauss_{}".format(i), "p_gauss_{}".format(i), deltam, p_means[i], p_widths[i]))

#Add the 3 Gaussians making up the signal 
p_sig1frac = RooRealVar("p_sig1frac", "p_sig1frac", 0.01, 0, 1)
p_sig2frac = RooRealVar("p_sig2frac", "p_sig2frac", 0.01, 0, 1)
p_signal_pdf = RooAddPdf("p_signal_pdf", "p_signal_pdf", RooArgList(*p_gauss), RooArgList(p_sig1frac, p_sig2frac))

#Fit composite signal to data
p_signal_pdf.fitTo(dataset_sig)

#Draw pure signal fit
if draw_p_sig :
    pure_canvas = TCanvas("pure_canv", "Pure Signal Fit")
    p_frame = deltam.frame()
    dataset_sig.plotOn(p_frame)
    p_signal_pdf.plotOn(p_frame)
    p_frame.Draw()

#Extract fitted parameters
p_fracFits = [p_sig1frac.getValV(), p_sig2frac.getValV()]
p_meanFits, p_widthFits = [], []
for i in range(n_sig_pdf) :
    p_meanFits.append(p_means[i].getValV())
    p_widthFits.append(p_widths[i].getValV())

##############################################



######### Defining background pdf ############

#RooDstD0BG is background pdf implemented in RooFit specifically to model D*-D0 mass distribution bg
bgvar1 = RooRealVar("bgvar1", "bgvar1", 48.3, 0, 100)
bgvar2 = RooRealVar("bgvar2", "bgvar2", -17.4, -50, 10)
bgvar3 = RooRealVar("bgvar3", "bgvar3",0.18, 0.01, 5)
deltam0 = RooRealVar("dm0", "dm0", 139, 130, 150)
bg_pdf = RooDstD0BG("bg_pdf", "bg_pdf", deltam, deltam0, bgvar1, bgvar2, bgvar3)

##############################################



############# Fitting Real Data ##############

total_pdf = RooSimultaneous("total_pdf", "total_pdf", regionIndex)

#Lists for storing all component pdfs, RooFit variables etc.
region_sig_pdfs, region_total_pdfs, bg_fracs, scales, shifts = [], [], [], [], []
shiftedMeans, scaledWidths, sig, fracs = [], [], [], []
for i in range(n_regions) :
    shiftedMeans.append([])
    scaledWidths.append([])
    sig.append([])

#Setting up variable for underlying means/widths which will be shifted/scaled in each region
widths, means = [], []
for i in range(n_sig_pdf) :
    #Take previous fit values as initial values, and fix constant for now
    means.append(RooRealVar("mean_{}".format(i), "mean_{}".format(i), p_meanFits[i], dm_min, dm_max))
    means[i].setConstant(True)
    widths.append(RooRealVar("width_{}".format(i), "width_{}".format(i), p_widthFits[i], w_min, w_max))
    widths[i].setConstant(True)
    if i < n_sig_pdf - 1 :
        fracs.append(RooRealVar("frac_{}".format(i), "frac_{}".format(i), p_fracFits[i], 0, 1))
        fracs[i].setConstant(True)   


for i in range(n_regions) :
  
    region = regions[i]

    #Setting up parameters to allow only single shift (means) and scale (sigmas)
    #shiftedMeans, scaledWidths, sig, fracs  = [], [], [], []
    shifts.append(RooRealVar("shift_"+region, "shift_"+region, 0.005, -1, 1))
    shifts[i].setError(0.01)
    scales.append(RooRealVar("scale_"+region, "scale_"+region, 1.26, 0.001, 5))
    scales[i].setError(0.01)
    for j in range(n_sig_pdf) :
        shiftedMeans[i].append(RooFormulaVar("shifted_mean_{}_".format(j)+region, "mean_{}+shift_".format(j)+region, RooArgList(means[j], shifts[i])))
        scaledWidths[i].append(RooFormulaVar("scaled_width_{}_".format(j)+region, "width_{}*scale_".format(j)+region, RooArgList(widths[j], scales[i])))
        sig[i].append(RooGaussian("sig_{}_".format(j)+region, "sig_{}_".format(j)+region, deltam, shiftedMeans[i][j], scaledWidths[i][j]))

    #Adding components to form total signal pdf
    region_sig_pdfs.append(RooAddPdf("signal_pdf_"+region, "signal_pdf_"+region, RooArgList(*sig[i]), RooArgList(*fracs)))
    bg_fracs.append(RooRealVar("bg_frac_"+region, "bg_frac_"+region, 0.107, 0, 1))
    region_total_pdfs.append(RooAddPdf("total_pdf_"+region, "total_pdf_"+region, RooArgList(region_sig_pdfs[i], bg_pdf), RooArgList(bg_fracs[i])))

    #Adding to simultaneous pdf
    total_pdf.addPdf(region_total_pdfs[i], region)


#Simultaneously fit all mass regions - bg free and signal with shift/scale only
total_pdf.fitTo(datahist)

#Now, fix bg and fit signal only
bgvar1.setConstant(True)
bgvar2.setConstant(True)
bgvar3.setConstant(True)
deltam0.setConstant(True)
for i in range(n_sig_pdf) :
    means[i].setConstant(False)
    widths[i].setConstant(False)
    if i < n_sig_pdf - 1 :
        fracs[i].setConstant(False)

#Fixing scale and shift in middle D0 mass region to 1 and 0
#shifts[1].setVal(0.) 
shifts[1].setConstant(True)
#scales[1].setVal(1.)
scales[1].setConstant(True)

#Fitting signal only now
total_pdf.fitTo(datahist)


#Plotting fits
canvs = []
fitPads = []
pullPads = []
pulls = []
for i in range(n_regions) :
    region = regions[i]
    canvs.append(TCanvas(region+"_canv", region+" D0 Mass Region Fit"))    

    frame = deltam.frame()
    datahist.plotOn(frame, Cut("regionIndex==regionIndex::"+region))
    regionIndexSet = RooArgSet(regionIndex)
    total_pdf.plotOn(frame, Slice(regionIndex, region), ProjWData(regionIndexSet, datahist))
    pulls.append(frame.pullHist())
    total_pdf.plotOn(frame, Slice(regionIndex, region), ProjWData(regionIndexSet, datahist), Components("bg_pdf"), LineColor(kGreen+2), LineStyle(2))
    total_pdf.plotOn(frame, Slice(regionIndex, region), ProjWData(regionIndexSet, datahist), Components("signal_pdf_"+region), LineColor(kRed+2), LineStyle(3))
    
    #Creating pad to plot fit to data
    fitPads.append(TPad("fitPad_{}".format(i), "fitPad_{}".format(i), 0., 0.3, 1., 1.)) 
    fitPads[i].SetMargin(0.08, 0.05, 0.05, 0.1)
    fitPads[i].Draw()
    fitPads[i].cd()
    frame.Draw()

    #Creating pad to plot pull ( (actual - fit) / uncertainty )
    canvs[i].cd() 
    pullPads.append(TPad("pullPad_{}".format(i), "pullPad_{}".format(i), 0., 0., 1., 0.3))
    pullPads[i].SetMargin(0.08, 0.05, 0.1, 0.05)
    pullPads[i].Draw()

    pull_frame = deltam.frame()
    pull_frame.addPlotable(pulls[i], "P")
    pullPads[i].cd()
    pull_frame.Draw()

    #Formatting pull plot
    #from /opt/local/share/root5/doc/root/tutorials/roofit/rf109_chi2residpull.C
    pull = filter(lambda prim : isinstance(prim, TH1), pullPads[i].GetListOfPrimitives())[0]
    pull.GetYaxis().SetRangeUser(-5., 5.)
    pull.SetTitle('')
    pull.GetXaxis().SetTitle('')
    pull.GetXaxis().SetLabelSize(0.)
    pull.GetXaxis().SetTickLength(0.1)
    pull.GetYaxis().SetLabelSize(0.08)
    pull.GetYaxis().SetNdivisions(5)
    #pull.GetYaxis().SetTickLength(0.1)
    pull.GetYaxis().SetTitle('Pull')
    pull.GetYaxis().SetTitleSize(0.15)
    pull.GetYaxis().SetTitleOffset(0.2)
    pull.GetYaxis().CenterTitle()

    #Formatting fit plot
    fit = filter(lambda prim : isinstance(prim, TH1), fitPads[i].GetListOfPrimitives())[0]
    fit.GetYaxis().SetTitleSize(0.05)
    fit.GetYaxis().CenterTitle()
    fit.GetYaxis().SetTitleOffset(0.7)
    fit.SetTitle("#Delta m fit in "+regions[i]+" region, mag = "+mag)
    fit.GetXaxis().SetRangeUser(140.,155.)
    fit.GetXaxis().SetTitleOffset(0.85)
    fit.GetXaxis().SetTitleSize(0.04)

##############################################



