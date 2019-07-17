#!/usr/bin/env python

# Load Mint2 libraries.
import Mint2, ROOT, math
from AGammaD0Tohhpi0.data import datalib
from ROOT import DalitzEventList, TFile, binflipChi2
from ROOT.MINT import NamedParameterBase, Minimiser
from scipy.optimize import minimize
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
nbinsTime = 50
tMax = 7.5

#These don't change with the data file, so just calculate once here
X, F, Fbar, r = computeIntegrals(nbinsPhase, True)
zcp, deltaz = getZvals(x,y,qoverp,phi)

success = 0
lim = 1
failed = []

for fileNo in range(1, lim+1) :
 
    print "Processing file number {}... \n".format(fileNo)

    #Setting up variables and reading in events 

    fdata = TFile.Open('/nfs/lhcb/d2hh01/hhpi0/data/mint/data_3SigmaCPV_prec=3e-4_simpleModel/pipipi0_{}.root'.format(fileNo)) 

    #Retrieve the dataset as a DalitzEventList and nTuple
    evtlist = DalitzEventList(fdata.Get('DalitzEventList'))
    evtData = fdata.Get('DalitzEventList')

    tAv = [0]*nbinsTime
    tSqAv = [0]*nbinsTime

    upperHists = []
    lowerHists = []
    #Here 0 index is D0 histogram, 1 is D0bar
    for i in range(2) :
        upperHists.append( ROOT.TH2F("upper hist i{} f{}".format(i, fileNo), "", nbinsTime, 0, tMax, nbinsPhase, phaseMin, phaseMax ) )
        lowerHists.append( ROOT.TH2F("lower hist i{} f{}".format(i, fileNo), "", nbinsTime, 0, tMax, nbinsPhase, phaseMin, phaseMax ) )
 
    nD0 = 0
    for evt in evtData :
        if (evt.tag == 1) :
            nD0 += 1

    #Processing data 

    #Calling function to perform phase binning and store all (binned) decay times
    tList, tSqList = binByPhase(evtData, evtlist, lowerHists, upperHists, tMax)

    #Calculating parameters required for fit to data
    for i in range( nbinsTime ) : 
        tAv[i] = sum(tList[i]) / len(tList[i])
        tSqAv[i] = sum(tSqList[i]) / len(tSqList[i])

    X_cpp, r_cpp, Fm_cpp, Fp_cpp, tAv_cpp, tSqAv_cpp = getcppVecs(X, r, F, tAv, tSqAv, nD0)
    binflipfitter = binflipChi2(X_cpp, r_cpp, tAv_cpp, tSqAv_cpp, lowerHists[0], lowerHists[1], upperHists[0], upperHists[1], zcp.real, zcp.imag, deltaz.real, deltaz.imag, 0.0001, fileNo, Fm_cpp, Fp_cpp)
    parset = binflipfitter.getParSet()
    for i in [0,2,3] :
        parset.getParPtr(i).fixAndHide()

    minimiser = Minimiser(binflipfitter, 1.)
    minimiser.doFit()

    if minimiser.isConverged() :
        success += 1
    else :
        failed.append(fileNo)

    resultsfile = TFile("rootOut/fit_{}.root".format(fileNo), "recreate")

    resultstree = parset.makeNewNtpForOwner(resultsfile)
    parset.fillNtp(resultsfile, resultstree)
    resultstree.Write()
    resultsfile.Close()

    print "File number {} processed. ".format(fileNo)
    print "\nActual values are : \t Zcp : %e + %ei \t\t deltaZ : %e + %ei\n" % (zcp.real, zcp.imag, deltaz.real, deltaz.imag)


if ( success != lim ):
    print "\n\nWARNING : {} out of {} fits converged successfully.\n".format(success,lim)
    print failed
