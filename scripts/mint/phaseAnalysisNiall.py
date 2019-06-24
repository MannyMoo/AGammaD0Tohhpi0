#!/usr/bin/env python

# Load Mint2 libraries.
import Mint2, ROOT, math
from AGammaD0Tohhpi0.data import datalib
from ROOT import PhaseDifferenceCalc, DalitzEventList, TFile, DalitzEventPattern
from ROOT.MINT import NamedParameterBase
from AGammaD0Tohhpi0.mint import config
from AGammaD0Tohhpi0.mint import pattern_D0Topipipi0, set_default_config
from scipy.optimize import minimize
from AGammaD0Tohhpi0.binflip import *

# Set the config file.
# NamedParameterBase.setDefaultInputFile(config)
set_default_config()

ROOT.TH1.SetDefaultSumw2(True)

# Get the phase difference calculator.
#pattern = DalitzEventPattern(421, 211, -211, 111)
pattern = pattern_D0Topipipi0
diffcalc = PhaseDifferenceCalc(pattern, config)

#flag for whether to draw plots of R(b,j) 
drawRatioPlots = True

verbose = False

#3Sigma_CPV simulation variables
x = 0.0039
y = 0.0065
qoverp = 0.8
phi = -0.7

#Parameters for time/phase histogram setup
nbinsPhase = 8
phaseMin = 2*math.pi*(-0.5) / nbinsPhase
phaseMax = 2*math.pi*(nbinsPhase - 0.5) / nbinsPhase
nbinsTime = 25
tMax = 3

#File to store fit parameters and their errors
outFile = open("fitParameters_100.txt", "w")

for fileNo in range(1,101) :

    print "\n Processing file number {}... \n".format(fileNo)

    ######## Setting up variables and reading in events ###########

    #Each file here contains 500,000 events 
    fdata = TFile.Open('/nfs/lhcb/d2hh01/hhpi0/data/mint/data_3SigmaCPV/pipipi0_{}.root'.format(fileNo)) 
    #Retrieve the dataset as a DalitzEventList and nTuple
    evtlist = DalitzEventList(fdata.Get('DalitzEventList'))
    evtData = fdata.Get('DalitzEventList')

    tAv = []
    tSqAv = [] 

    for i in range( nbinsTime ) : 
        tAv.append(0)
        tSqAv.append(0)

    upperHists = []
    lowerHists = []
    #Here 0 index is D0 histogram, 1 is D0bar
    for i in range(2) :
        upperHists.append( ROOT.TH2F("upper hist i{} f{}".format(i, fileNo), "", nbinsTime, 0, tMax, nbinsPhase, phaseMin, phaseMax ) )
        lowerHists.append( ROOT.TH2F("lower hist i{} f{}".format(i, fileNo), "", nbinsTime, 0, tMax, nbinsPhase, phaseMin, phaseMax ) )




    ######## Data gets processed here  ###########

   #Calling function to perform phase binning and store all (binned) decay times
    tList, tSqList = binByPhase(evtData, evtlist, diffcalc, lowerHists, upperHists, tMax)

    #Calculating parameters required for fit to data
    for i in range( nbinsTime ) : 
        tAv[i] = sum(tList[i]) / len(tList[i])
        tSqAv[i] = sum(tSqList[i]) / len(tSqList[i])

    X, F, Fbar, r = computeIntegrals(pattern, diffcalc, nbinsPhase)


    #Get fit from known parameters used in simulation
    zcp, deltaz = getZvals(x,y,qoverp,phi)
    RPlots = getFit(zcp, deltaz, tAv, tSqAv, r, X)

    #Get fitted parameter values from minimising chi squared
    #result = minimize(getChiSquared, [x, y, qoverp, phi], (tAv, tSqAv, r, X, nbinsTime, nbinsPhase, lowerHists, upperHists))
    result = minimize(getChiSquared, [zcp.real, zcp.imag, deltaz.real, deltaz.imag], (tAv, tSqAv, r, X, lowerHists, upperHists))

    #Extract fitted values and errors
    # xFit, yFit, qoverpFit, phiFit = result.x
    # err_xFit = result.hess_inv[0][0]**0.5
    # err_yFit = result.hess_inv[1][1]**0.5 
    # err_qoverpFit = result.hess_inv[2][2]**0.5
    # err_phiFit = result.hess_inv[3][3]**0.5
    zcpFit = complex(result.x[0], result.x[1])
    deltazFit = complex(result.x[2], result.x[3])
    err_ReZcpFit = result.hess_inv[0][0]**0.5
    err_ImZcpFit = result.hess_inv[1][1]**0.5 
    err_ReDzFit = result.hess_inv[2][2]**0.5
    err_ImDzFit = result.hess_inv[3][3]**0.5

    #Calculate fit function values from fitted parameters
    #zcpFit, deltazFit = getZvals( xFit, yFit, qoverpFit, phiFit )
    RFits = getFit(zcpFit, deltazFit, tAv, tSqAv, r, X)

    #Store fitted values in text file
    # outFile.write("{} {} ".format(xFit, err_xFit))
    # outFile.write("{} {} ".format(yFit, err_yFit))
    # outFile.write("{} {} ".format(qoverpFit, err_qoverpFit))
    # outFile.write("{} {}\n".format(phiFit, err_phiFit))
    outFile.write("{} {} ".format(zcpFit.real, err_ReZcpFit))
    outFile.write("{} {} ".format(zcpFit.imag, err_ImZcpFit))
    outFile.write("{} {} ".format(deltazFit.real, err_ReDzFit))
    outFile.write("{} {}\n".format(deltazFit.imag, err_ImDzFit))




    ######## Output on screen happens here ############

    #Print out some parameters if verbose flag set to true
    if (verbose) :
        print "-"*135, "\n"
        print "\t b", "\t"*4, "Xb", " \t "*4, " Fb", "\t"*3, " Fb bar", " \t "*2, "rb\n"
        print"-"*135, "\n"
        for i in range(nbinsPhase) :
            print "\t {}\t\t {}\t\t{}\t\t{}\t\t{}\n".format( i+1, X[0][i], F[0][i], Fbar[0][i], r[i] )
            print "\t{}\t\t {}\t\t{}\t\t{}\n\n".format(-1*(i+1), X[1][i], F[1][i], Fbar[1][i] )

        print "Optimisation results:\t x: {}\t y: {}\t qoverp: {}\t phi: {}".format(xFit, yFit, qoverpFit, phiFit)
        print "Optimisation Errors: \t errx: {}\t erry: {}\t errqoverp: {}\t errphi: {}".format(err_xFit, err_yFit, err_qoverpFit, err_phiFit)
        print "Simulation parameters:\t x: {}\t\t y: {}\t\t qoverp: {}\t\t phi: {}".format(x, y, qoverp, phi) 


    # Draw ratio plots - only really useful when testing on a single file
    if (drawRatioPlots) :
        ratioPlots = createRatioPlots(upperHists, lowerHists, tMax, fileNo)

        canvas = []
        canvas.append( ROOT.TCanvas("c1 f{}".format(fileNo), "D0 ratios by bin") )
        canvas[0].Divide(2,4)
        canvas.append( ROOT.TCanvas("c2 f{}".format(fileNo), "D0bar ratios by bin") )
        canvas[1].Divide(2,4)
    
        for i in range(2) :
            for b in range(1, nbinsPhase + 1) :
                #Drawing ratio plot
                canvas[i].cd(b)
                setPlotParameters(ratioPlots[i][b-1], i, b)
                ratioPlots[i][b-1].Draw()

                #Drawing fit with simulation parameters
                RPlots[i][b-1].SetMarkerStyle(5)
                RPlots[i][b-1].Draw('Same P')

                #Drawing fit with fitted parameters
                RFits[i][b-1].SetMarkerStyle(4)
                RFits[i][b-1].SetMarkerColor(2)
                RFits[i][b-1].Draw('Same P')

    print "File number {} processed.".format(fileNo) 


outFile.close()
