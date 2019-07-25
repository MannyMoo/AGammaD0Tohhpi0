#!/usr/bin/env python

# Load Mint2 libraries.
import Mint2, ROOT, math, sys
from AGammaD0Tohhpi0.data import datalib
from ROOT import DalitzEventList, TFile, binflipChi2, FitAmpSum
from ROOT.MINT import NamedParameterBase, Minimiser
from AGammaD0Tohhpi0.binflip import *
from AGammaD0Tohhpi0.mint import get_config, set_default_config, pattern_D0Topipipi0

ROOT.TH1.SetDefaultSumw2(True)

if len(sys.argv) > 1 :
    name = sys.argv[1]
else :
    name = 'data_3SigmaCPV_fullModel'
print 'Dataset:', name
config = get_config(name)
set_default_config(config.fnames[0])
print 'Config file:', config.fnames[0]

model = FitAmpSum(pattern_D0Topipipi0)
print 'Amplitudes:'
model.printAllAmps()

#Simulation variables
x = config.float('x')
y = config.float('y')

qoverp = config.float('qoverp')
phi = config.float('phi')

lifetime = config.float('lifetime')

#Parameters for time/phase histogram setup
nbinsPhase = 8
phaseMin = 2*math.pi*(-0.5) / nbinsPhase
phaseMax = 2*math.pi*(nbinsPhase - 0.5) / nbinsPhase
nbinsTime = 10#Previously 50
tMax = 6#Previously 7.5

#These don't change with the data file, so just calculate once here
X, F, Fbar, r = computeIntegrals(nbinsPhase, config.fnames[0], True)
zcp, deltaz = getZvals(x,y,qoverp,phi)

success = 0
lim = 1
failed = []
drawRatioPlots = True

if not name.startswith('MINT_') :
    name = 'MINT_' + name
datainfo = datalib.get_data_info(name)

for fileNo in range(1, lim+1) :

    #Setting up variables and reading in events 

    #Retrieve the dataset as a DalitzEventList and nTuple
    print "Processing file number {}... \n".format(fileNo)
    fname = datainfo['files'][fileNo-1]
    print fname
    fdata = TFile.Open(fname)
    evtlist = DalitzEventList(fdata.Get('DalitzEventList'))
    evtData = fdata.Get('DalitzEventList')

    upperHists = []
    lowerHists = []
    #Here 0 index is D0 histogram, 1 is D0bar
    for i in range(2) :
        upperHists.append( ROOT.TH2F("upper hist i{} f{}".format(i, fileNo), "", nbinsTime, 0, tMax, nbinsPhase, phaseMin, phaseMax ) )
        lowerHists.append( ROOT.TH2F("lower hist i{} f{}".format(i, fileNo), "", nbinsTime, 0, tMax, nbinsPhase, phaseMin, phaseMax ) )

    #Calling function to perform phase binning and store all (binned) decay times
    tList, tSqList, nD0  = binByPhase(evtData, evtlist, lowerHists, upperHists, tMax, lifetime, config.fnames[0])

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
    fdata.Close()

    print "File number {} processed. ".format(fileNo)
    print "\nActual values are : \t Zcp : %e + %ei \t\t deltaZ : %e + %ei\n" % (zcp.real, zcp.imag, deltaz.real, deltaz.imag)


   #Draw plots
    if(drawRatioPlots) :
        dataPlots = createRatioPlots(upperHists, lowerHists, tMax, fileNo)
        canvas, fits, RPlots = setupPlots(nbinsPhase, binflipfitter, dataPlots)
        for i in range(2) :
            for b in range(1, nbinsPhase + 1) :
                canvas[i].cd(b)
                dataPlots[i][b-1].Draw()
                RPlots[i][b-1].Draw('Same P')
                fits[i][b-1].Draw('Same P')




if ( success != lim ) :
    print "\nWARNING : {} out of {} fits converged successfully.\n".format(success,lim)
    print "Fits which failed were: ", failed, "\n"
else :
    print "\nSuccess! All fits completed without error flags.\n"
   
