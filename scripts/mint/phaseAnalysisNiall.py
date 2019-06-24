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
set_default_config()

ROOT.TH1.SetDefaultSumw2(True)

# Get the phase difference calculator.
pattern = pattern_D0Topipipi0
diffcalc = PhaseDifferenceCalc(pattern, config)

#Output to screen flags
drawRatioPlots = True

#Verbosity level: 0 for nothing, 1 for just fit result, 2 for integrals and fit results
verbose = 1

#Simulation variables
x = 0.0039
y = 0.0065
qoverp = 0.8
phi = -0.7


#Parameters for time/phase histogram setup
nbinsPhase = 8
phaseMin = 2*math.pi*(-0.5) / nbinsPhase
phaseMax = 2*math.pi*(nbinsPhase - 0.5) / nbinsPhase
nbinsTime = 50
tMax = 7.5

#Files to store fit parameters and their errors
outFiles = [open("fitParameters_chi2.txt", "w"), open("fitParameters_chi2Test.txt", "w")]



for fileNo in range(1,2) :

    print "Processing file number {}... \n".format(fileNo)

    #Setting up variables and reading in events 

    fdata = TFile.Open('/nfs/lhcb/d2hh01/hhpi0/data/mint/data_3SigmaCPV_prec1e-3/pipipi0_{}.root'.format(fileNo)) 

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





    #Processing data 

    #Calling function to perform phase binning and store all (binned) decay times
    tList, tSqList = binByPhase(evtData, evtlist, diffcalc, lowerHists, upperHists, tMax)

    #Calculating parameters required for fit to data
    for i in range( nbinsTime ) : 
        tAv[i] = sum(tList[i]) / len(tList[i])
        tSqAv[i] = sum(tSqList[i]) / len(tSqList[i])

    X, F, Fbar, r = computeIntegrals(pattern, diffcalc, nbinsPhase)

    zcp, deltaz = getZvals(x,y,qoverp,phi)

    #Initialising variables for fits and errors
    zcpFit, deltazFit, err_ReZcpFit, err_ImZcpFit, err_ReDzFit, err_ImDzFit = [[],[],[],[],[],[]] 

    #Loop over output files to store optimisation fit based on both implementations of chi2 function
    for i in range(2) :

        #Get fitted parameter values from minimising chi squared
        if (i == 0) :
            result = minimize(getChiSquared, [zcp.real, zcp.imag, deltaz.real, deltaz.imag], (tAv, tSqAv, r, X, lowerHists, upperHists))
        else:
            ratios = getRatiosAsymm(lowerHists, upperHists)
            result = minimize(getChiSquared_Test, [zcp.real, zcp.imag, deltaz.real, deltaz.imag], (tAv, tSqAv, r, X, ratios, nbinsTime))

        #Extract fitted values and errors
        zcpFit.append( complex(result.x[0], result.x[1]) )
        deltazFit.append( complex(result.x[2], result.x[3]) )
        err_ReZcpFit.append( result.hess_inv[0][0]**0.5 )
        err_ImZcpFit.append( result.hess_inv[1][1]**0.5 ) 
        err_ReDzFit.append( result.hess_inv[2][2]**0.5 )
        err_ImDzFit.append( result.hess_inv[3][3]**0.5 )

        #Store fitted values in text file
        outFiles[i].write("{} {} ".format(zcpFit[i].real, err_ReZcpFit[i]))
        outFiles[i].write("{} {} ".format(zcpFit[i].imag, err_ImZcpFit[i]))
        outFiles[i].write("{} {} ".format(deltazFit[i].real, err_ReDzFit[i]))
        outFiles[i].write("{} {}\n".format(deltazFit[i].imag, err_ImDzFit[i]))




    #Output to screen (set flags at top of file before running)

    if (verbose == 2) :
        print "-"*135, "\n"
        print "\t b", "\t"*4, "Xb", " \t "*4, " Fb", "\t"*3, " Fb bar", " \t "*2, "rb\n"
        print"-"*135, "\n"
        for i in range(nbinsPhase) :
            print "\t {}\t\t {}\t\t{}\t\t{}\t\t{}\n".format( i+1, X[0][i], F[0][i], Fbar[0][i], r[i] )
            print "\t{}\t\t {}\t\t{}\t\t{}\n\n".format(-1*(i+1), X[1][i], F[1][i], Fbar[1][i] )

    if (verbose >= 1) :
        print "\nSimulation parameters: \t\t zcp: {} \t\t deltaz: {}\n".format(zcp, deltaz)
        print "Fit parameters ('old' chi2): \t zcp (fit): {} \t deltaz (fit): {}".format(zcpFit[0], deltazFit[0])
        print "Fit errors ('old' chi2): \t zcp (error): {} \t deltaz (error): {}\n".format(complex(err_ReZcpFit[0], err_ImZcpFit[0]), complex(err_ReDzFit[0], err_ImDzFit[0]))
        print "Fit parameters ('new' chi2): \t zcp (fit): {} \t deltaz (fit): {}".format(zcpFit[0], deltazFit[1])
        print "Fit errors ('new' chi2): \t zcp (error): {} \t deltaz (error): {}\n".format(complex(err_ReZcpFit[1], err_ImZcpFit[1]), complex(err_ReDzFit[1], err_ImDzFit[1]))


    # Drawing ratio plots and fits - only really useful when testing on a single file
    #NOTE: Fit is drawn here only for 'old' getChiSquared fit, not getChiSquared_Test 
    if (drawRatioPlots) :
        ratioPlots = createRatioPlots(upperHists, lowerHists, tMax, fileNo)

        #Get fit from known parameters used in simulation
        RPlots = getFit(zcp, deltaz, tAv, tSqAv, r, X)

        #Calculate fit function values from fitted parameters
        RFits = getFit(zcpFit[0], deltazFit[0], tAv, tSqAv, r, X)

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

    print "File number {} processed.\n".format(fileNo) 


outFiles[0].close()
outFiles[1].close()
