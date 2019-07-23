#!/usr/bin/env python

# Load Mint2 libraries.
import Mint2, ROOT, math, sys
from AGammaD0Tohhpi0.data import datalib
from ROOT import DalitzEventList, TFile, binflipChi2
from ROOT.MINT import NamedParameterBase, Minimiser
from scipy.optimize import minimize
from AGammaD0Tohhpi0.binflip import *
from AGammaD0Tohhpi0.mint import get_config, set_default_config

ROOT.TH1.SetDefaultSumw2(True)

#Simulation variables
name = sys.argv[1]
config = get_config(name)
set_default_config(config.fnames[0])

x = float(config['x'][0])
y = float(config['y'][0])

qoverp = float(config['qoverp'][0])
phi = float(config['phi'][0])

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

if not name.startswith('MINT_') :
    name = 'MINT_' + name
datainfo = datalib.get_data_info(name)

for fileNo in range(0, lim) :
 
    print "Processing file number {}... \n".format(fileNo)

    #Setting up variables and reading in events 

    fdata = TFile.Open(datainfo['files'][fileNo])

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
    #for i in xrange(1, 4) :
    #    parset.getParPtr(i).fixAndHide()

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
