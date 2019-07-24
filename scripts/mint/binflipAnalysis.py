#!/usr/bin/env python

# Load Mint2 libraries.
import Mint2, ROOT, math
from AGammaD0Tohhpi0.data import datalib
from ROOT import DalitzEventList, TFile, binflipChi2
from ROOT.MINT import NamedParameterBase, Minimiser
from AGammaD0Tohhpi0.binflip import *

ROOT.TH1.SetDefaultSumw2(True)

#Simulation variables
x = 0.0039
y = 0.0065
qoverp = 0.8
phi = -0.7

#Parameters for time/phase histogram setup
nbinsPhase = 8
phaseMin = 2*math.pi*(-0.5) / nbinsPhase
phaseMax = 2*math.pi*(nbinsPhase - 0.5) / nbinsPhase
nbinsTime = 10#Previously 50
tMax = 6#Previously 7.5

#These don't change with the data file, so just calculate once here
X, F, Fbar, r = computeIntegrals(nbinsPhase, False)
zcp, deltaz = getZvals(x,y,qoverp,phi)

success = 0
lim = 1
failed = []
drawRatioPlots = True

for fileNo in range(1, lim+1) :

    #Setting up variables and reading in events 

    #Retrieve the dataset as a DalitzEventList and nTuple
    print "Processing file number {}... \n".format(fileNo)
    fdata = TFile.Open('/nfs/lhcb/d2hh01/hhpi0/data/mint/data_3SigmaCPV_fullModel/pipipi0_{}.root'.format(fileNo)) 
    evtlist = DalitzEventList(fdata.Get('DalitzEventList'))
    evtData = fdata.Get('DalitzEventList')

    upperHists = []
    lowerHists = []
    #Here 0 index is D0 histogram, 1 is D0bar
    for i in range(2) :
        upperHists.append( ROOT.TH2F("upper hist i{} f{}".format(i, fileNo), "", nbinsTime, 0, tMax, nbinsPhase, phaseMin, phaseMax ) )
        lowerHists.append( ROOT.TH2F("lower hist i{} f{}".format(i, fileNo), "", nbinsTime, 0, tMax, nbinsPhase, phaseMin, phaseMax ) )

    #Calling function to perform phase binning and store all (binned) decay times
    lifetime = 0.4101
    tList, tSqList, nD0  = binByPhase(evtData, evtlist, lowerHists, upperHists, tMax, lifetime)

    #Averaging all values of tSq and t to get <t^2> and <t>
    tAv = averageElements(tList)
    tSqAv = averageElements(tSqList)

    #Processing data

    #Initialise binflipChi2 instance to perform fitting. Need to first setup variables suitable for passing to c++
    X_cpp, r_cpp, Fm_cpp, Fp_cpp, tAv_cpp, tSqAv_cpp = getcppVecs(X, r, F, tAv, tSqAv, nD0)
    binflipfitter = binflipChi2(X_cpp, r_cpp, tAv_cpp, tSqAv_cpp, lowerHists[0], lowerHists[1], upperHists[0], upperHists[1], zcp.real, zcp.imag, deltaz.real, deltaz.imag, 0.0001)#, fileNo, Fm_cpp, Fp_cpp)
    parset = binflipfitter.getParSet()

    #Initialise Minimiser and perform fit 
    minimiser = Minimiser(binflipfitter, 1.)
    minimiser.doFit()

    if minimiser.isConverged() :
        success += 1
    else :
        failed.append(fileNo)
        print "\nWARNING: FAILED FIT\n"

    #Open output file and setup tree to write 
    resultsfile = TFile("rootOutTest/fit_{}.root".format(fileNo), "recreate")
    resultstree = parset.makeNewNtpForOwner(resultsfile)

    #Write to file and cleanup
    parset.fillNtp(resultsfile, resultstree)
    resultstree.Write()
    resultsfile.Close()

    print "File number {} processed. ".format(fileNo)
    print "\nActual values are : \t Zcp : %e + %ei \t\t deltaZ : %e + %ei\n" % (zcp.real, zcp.imag, deltaz.real, deltaz.imag)

   #Draw plots
    if(drawRatioPlots) :
        dataPlots = createRatioPlots(upperHists, lowerHists, tMax, fileNo)
        canvas, fits, RPlots = setupPlots(nbinsPhase, binflipfitter, dataPlots, fileNo)
        for i in range(2) :
            for b in range(1, nbinsPhase + 1) :
                canvas[i].cd(b)
                dataPlots[i][b-1].Draw()
                RPlots[i][b-1].Draw('Same P')
                fits[i][b-1].Draw('Same P')

    fdata.Close()




if ( success != lim ) :
    print "\nWARNING : {} out of {} fits converged successfully.\n".format(success,lim)
    print "Fits which failed were: ", failed, "\n"
else :
    print "\nSuccess! All fits completed without error flags.\n"
   
