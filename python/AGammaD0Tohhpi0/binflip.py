#!/usr/bin/env python

import math, ROOT
from Mint2.utils import three_body_event
from ROOT import PhaseDifferenceCalc
from AGammaD0Tohhpi0.mint import pattern_D0Topipipi0, set_default_config
from AGammaD0Tohhpi0.mint import config
from AGammaD0Tohhpi0.variables import variables
import cmath

# Set the config file.
set_default_config()

# Get the phase difference calculator.
pattern = pattern_D0Topipipi0

def getPhaseDifference(evt, s13, s23, diffcalc, tag = 1) :
    '''Get the D0/D0bar amplitude phase difference for the given event. The binning is inverted
    in the lower half of the Dalitz plot, so the phase difference is inverted.'''
    phasediff = diffcalc.phase_difference(evt)
    # The binning is inverted in the lower half of the Dalitz plot, so invert the phase difference.
    #if tag == 1 :
    if s23 < s13 :
        phasediff *= -1
    #elif s23 < s13 :
    #    phasediff *= -1
        
    # Use the convention that phases run from 0 to 2pi rather than -pi to +pi.
    if phasediff < 0. :
        phasediff += 2*math.pi
    return phasediff

def getPhaseBin(phasediff, nbinsPhase) :
    '''Get the bin number for the given phase difference.'''
    return int( phasediff*( nbinsPhase/(2*math.pi)) + 0.5 ) + 1

def scanDalitzPlot(npoints,  pattern = pattern) :
    '''Iterate over the Dalitz plot in npoints in steps of size ds13 and ds23.'''
    s13min = pattern.sijMin(1, 3)
    s13max = pattern.sijMax(1, 3)
    s23min = pattern.sijMin(2, 3)
    s23max = pattern.sijMax(2, 3)
    ds13 = ( s13max - s13min ) / npoints
    ds23 = ( s23max - s23min ) / npoints
    for i in range( npoints ) : 
        s13 = s13min + (i+0.5) * ds13
        for j in range( npoints ) : 
            s23 = s23min + (j+0.5) * ds23
            evt = three_body_event(pattern, s13, s23)
            if evt :
                yield evt

def plotBinNumbers(config, nbinsPhase, npoints, pattern = pattern) :
    '''Make a plot of the bin numbers across the Dalitz plot.'''
    diffcalc = PhaseDifferenceCalc(pattern, config)
    s13min = pattern.sijMin(1, 3)
    s13max = pattern.sijMax(1, 3)
    s23min = pattern.sijMin(2, 3)
    s23max = pattern.sijMax(2, 3)
    histo = ROOT.TH2F('binnumbers', '', npoints, s13min, s13max, npoints, s23min, s23max)
    for evt in scanDalitzPlot(npoints, pattern) :
        s13 = evt.s(1, 3)
        s23 = evt.s(2, 3)
        phasediff = getPhaseDifference(evt, s13, s23, diffcalc)
        phasebin = getPhaseBin(phasediff, nbinsPhase)
        histo.Fill(s13, s23, phasebin)
    histo.SetStats(False)
    histo.GetZaxis().SetRangeUser(0.5, nbinsPhase + 0.5)
    histo.GetXaxis().SetTitle('{0} [{1}]'.format(variables['S13']['title'], variables['S13']['unit']))
    histo.GetYaxis().SetTitle('{0} [{1}]'.format(variables['S23']['title'], variables['S23']['unit']))
    return histo

def binByPhase(evtData, evtlist, lowerHists, upperHists, tMax, lifetime, diffcalc) :
    """Function which takes set of events and bins according to strong phase difference, position on Dalitz plot, 
         D0/D0bar tag and phase difference. Also stores all decay times for later calculations of average time/time 
         squared. 

         Inputs are:
             - evtData, evtlist: nTuple and DalitzEventList, respectively, containing information about a set of events
             - diffcalc: PhaseDifferenceCalc instance with desired pattern
             - lowerHists, upperHists: lists of two 2D histograms (four total) to contain binned events seperated by D0/D0bar 
               and by above/below s13 = s23 line 
             - tMax: maximum time value in upperHists and lowerHists
  
         Function returns:
             - tList: list of all decay times, binned the same as lowerHists and upperHists
             - tSqList: list of all decay times squared, binned the same as lowerHists and upperHists 
             - nD0: number of D0 events in the file  
  """

    nbinsTime = upperHists[0].GetNbinsX()
    nD0 = 0

    #Initialise variables for binned lists of decay times and decay times squared
    tList = [] 
    tSqList = [] 
    for i in range( nbinsTime ) : 
        tList.append([])
        tSqList.append([])

    # Loop over events.
    i = 0
    for evt in evtData :
        s13 = evtlist[i].s(1, 3)
        s23 = evtlist[i].s(2, 3)
        tag = evt.tag
        if( tag == 1 ) :
            nD0 += 1
        #expressing here in terms of D0 mean lifetime (all times in ps)
        decayTime = evt.decaytime / lifetime

        phasediff = getPhaseDifference(evtlist[i], s13, s23, diffcalc, tag)

        #Split events into either above/below y=x for D0 and D0bar. 
        #(upperHists stores events with negative phase bin index b, lowerHists stores events with positive b)
        if (tag == 1) :
            if (s23 < s13) :
                lowerHists[0].Fill(decayTime, phasediff)
            else: 
                upperHists[0].Fill(decayTime, phasediff)
        elif (tag == -1) :
            if (s23 < s13) :
                upperHists[1].Fill(decayTime, phasediff)
            else: 
                lowerHists[1].Fill(decayTime, phasediff)

        #Storing times to find <t>, <t^2>, with same time binning as histograms but no phase binning
        tBinNo = int( ( nbinsTime * decayTime ) / float(tMax) )
        if (tBinNo < nbinsTime) : 
            tList[tBinNo].append( decayTime ) 
            tSqList[tBinNo].append( decayTime**2 ) 

        i += 1

    return tList, tSqList, nD0





def getZvals(x, y, qoverp, phi) :
    """Function which will calculate and return zcp and deltaz, given x, y, q/p, phi as inputs.

         Inputs are:
             -x,y,qoverp,phi: float/doubles containing mixing parameters

         Function returns:
             -zcp, deltaz: complex numbers calculated from the input mixing parameters.
    """

    poverq = 1/qoverp

    xcp = 0.5*( x*math.cos(phi) * ( qoverp + poverq ) + y*math.sin(phi) * ( qoverp - poverq ) )
    deltax = 0.5*( x*math.cos(phi) * ( qoverp - poverq ) + y*math.sin(phi) * ( qoverp + poverq ) )

    ycp = 0.5*( y*math.cos(phi) * ( qoverp + poverq ) - x*math.sin(phi) * ( qoverp - poverq )  ) 
    deltay = 0.5*( y*math.cos(phi) * ( qoverp - poverq ) - x*math.sin(phi) * ( qoverp + poverq ) )

    zcp = complex(-1*ycp, -1*xcp)
    deltaz = complex(-1*deltay, -1*deltax)

    return zcp, deltaz




def getFit(zcp, deltaz, tAv, tSqAv, r, X) :
    """Function to evaluate fit formula at discrete time steps for given zcp and deltaz.

         Inputs are:
             - zcp, deltaz: complex mixing parameters defined as (q/p)^(+-1) = zcp +- deltaz
             - tAv, tSqAv: list containing averages of t and t^2 in each decay time bin (i.e. <t> and <t^2>)
             - r, X: lists containing values of r(b) and X(b) functions required for the fit. X is 2D array where 0 index 
               refers to list of X(b) for positive b and 1 index refers to list of X(b) for negative b values. 

         Function returns:
             -RPlots: 2D array of TGraphs where first index is 0 for D0 and 1 for D0bar, with second index
               running over phase bins. Graphs contain plots of expected results for R(b, j) at time values
               given in tAv.
    """

    RPlots =[[],[]]
    nbinsPhase = len(r)
    nbinsTime = len(tAv)    

    for i in range(2) :
        for b in range(1, nbinsPhase+1) :  
            #0 index is Rplus (D0) and 1 is Rminus (D0bar)
            RPlots[i].append( ROOT.TGraph(nbinsTime) )   

            for j in range(1, nbinsTime+1) :

                num1 = r[b-1]*( 1 + 0.25 * tSqAv[j-1] * ( zcp**2 - deltaz**2 ).real )
                num2 = 0.25 * tSqAv[j-1] * (abs(zcp + ((-1)**i)*deltaz)**2)
                num3 = (r[b-1]**0.5) * tAv[j-1] * ( X[0][b-1].conjugate() * (zcp +((-1)**i)*deltaz) ).real
                numerator = num1 + num2 + num3

                den1 = 1 + 0.25 * tSqAv[j-1] * ( zcp**2 - deltaz**2 ).real
                den2 = r[b-1] * 0.25 * tSqAv[j-1] * (abs(zcp + ((-1)**i)*deltaz)**2)
                den3 = (r[b-1]**0.5) * tAv[j-1] * ( X[0][b-1] * (zcp + ((-1)**i)*deltaz) ).real
                denominator = den1 + den2 + den3

                Rval = numerator / denominator
                RPlots[i][b-1].SetPoint(j-1, tAv[j-1], Rval)

    return RPlots




def setPlotParameters(plot, tag, plotNo):
    """Simple function to set desired format options for plotting graphs of R(b,j).

         Inputs are:
             -plot: TH1 for which plotting options are to be set.
             -tag: integer (either 0 or 1) describing whether the plot refers to D0 or D0bar events.
             -plotNo: number describing which phase bin plot represents.
    """

    xAxis = plot.GetXaxis()
    xAxis.SetTitle("Decay Time / D0 mean lifetime")
    xAxis.SetLabelSize(0.06)
    xAxis.SetTitleSize(0.06)
    xAxis.SetTitleOffset(0.75)


    yAxis = plot.GetYaxis()
    if (tag == 0) :
        yAxis.SetTitle("N(D0,-{0}) / N(D0,{0})".format(plotNo))
    else :
        yAxis.SetTitle("N(D0bar,-{0}) / N(D0bar,{0})".format(plotNo))
    yAxis.SetLabelSize(0.06)
    yAxis.SetTitleSize(0.06)
    yAxis.SetTitleOffset(0.4)

    plot.SetStats(False)

    return




def getChiSquared(params, tAv, tSqAv, r, X, pHists, nHists) :
    """Function to calculate chi squared value for R(b,j) fit to data for given real and imaginary parts of zcp and 
         deltaz. 

        Inputs are:
            - params: list containing Re(zcp), Im(zcp), Re(deltaz), Im(deltaz)
            - tAv, tSqAv: list containing averages of t and t^2 in each decay time bin (i.e. <t> and <t^2>)
            - r, X: lists containing values of r(b) and X(b) functions required for the fit. X is 2D array where 0 index 
              refers to list of X(b) for positive b and 1 index refers to list of X(b) for negative b values. 
            - pHist: list containing 2D histograms of events for D0 and D0bar, binned by phase and decay time, with 
              positive b indexes.
            - nHist: equivalent of pHist, but with negative b

         Function returns:
             - chiSq: chi squared value for fit to measured data given by the values input in params.  
    """

    nbinsPhase = pHists[0].GetNbinsY()
    nbinsTime = pHists[0].GetNbinsX()

    #Input is setup this way with a list to allow minimisation with scipy.minimize on listed parameters
    re_zcp, im_zcp, re_dz, im_dz = params
    zcp = complex(re_zcp, im_zcp)
    deltaz = complex(re_dz, im_dz)    
 
    chiSq = 0
    fit = getFit(zcp, deltaz, tAv, tSqAv, r, X)

    for b in range(1,nbinsPhase+1) :
        #pl (plus) refers to D0 data, mi (minus) to D0bar
        Rvals_pl = fit[0][b-1].GetY()            
        Rvals_mi = fit[1][b-1].GetY()

        for j in range(1,nbinsTime+1) : 
            R_pl = Rvals_pl[j-1]
            R_mi = Rvals_mi[j-1]  

            D0_num = ( nHists[0].GetBinContent(j,b) - pHists[0].GetBinContent(j,b) * R_pl )**2
            D0_den =   ( nHists[0].GetBinError(j,b) )**2 + ( pHists[0].GetBinError(j,b) * R_pl )**2 
            if (D0_den != 0) :
                D0_term = D0_num / D0_den
            else:
                D0_term = 0

            D0bar_num = ( nHists[1].GetBinContent(j,b) - pHists[1].GetBinContent(j,b) * R_mi )**2
            D0bar_den =   ( nHists[1].GetBinError(j,b) )**2 + ( pHists[1].GetBinError(j,b) * R_mi )**2 
            if (D0bar_den != 0) :
                D0bar_term = D0bar_num / D0bar_den
            else:
                D0bar_term = 0

            chiSq += D0_term + D0bar_term

    return chiSq




def createRatioPlots(upperHists, lowerHists, tMax, fileNo) :
    """Function to take histograms in lower/upper region for D0/D0bar and produce plots of measured R(b,j).

         Inputs are:
             - upperHists, lowerHists: lists of two 2D histograms (four total) to contain binned events seperated by D0/D0bar 
               and by above/below s13 = s23 line 
             - tMax: maximum time value in upperHists and lowerHists
             - fileNo: number of current file being processed

         Function returns:
             - ratioPlots: a list of TH1Fs containing measured values of R(b,j), with the first index given by 0 for D0 and 1 for 
               D0bar. Second index goes over the phase difference bins. Bins within each histogram refer to different decay times.
    """

    ratioPlots = [[],[]]
    nbinsTime = upperHists[0].GetNbinsX()
    nbinsPhase = upperHists[0].GetNbinsY()

    for i in range(2) :
        for b in range(1, nbinsPhase + 1) :

            ratioPlots[i].append(ROOT.TH1F("Plot b{}, t{} f{}".format(b,i,fileNo), "Plot b{}, t{} f{}".format(b,i,fileNo), nbinsTime, 0, tMax))

            #Take slices of 2D histograms in one phase bin
            upperHist = upperHists[i].ProjectionX("upper b{}, t{} f{}".format(b,i,fileNo), b, b)
            lowerHist = lowerHists[i].ProjectionX("lower b{}, t{} f{}".format(b,i,fileNo), b, b)

            #Create plot by ratio of counts in each bin
            ratioPlots[i][b-1] = upperHist
            ratioPlots[i][b-1].Divide(lowerHist)

    return ratioPlots




def computeIntegrals(nbinsPhase, diffcalc, normaliseF=False) :
    """Function to compute integrals F(b), Fbar(b) and X(b) and then calculate r(b), to be used for fit of R(b,j).
        
         Inputs are:
             - pattern: relevant pattern for event type being considered (here D0 -> 3pi)
             - diffcalc: PhaseDifferenceCalc instance with desired pattern
             - nbinsPhase: number of phase bins used to divide measured data

          Function returns:
              - X, F, Fbar: 2D lists containing values for functions X(b), F(b) and Fbar(b), respectively, with first index 0 
                for positive b and 1 for negative b. Second index goes over b.
              - r: list containing values of r(b), for positive b, defined as: r(b) = F(-b)/F(b).
    """

    s13min = pattern.sijMin(1, 3)
    s13max = pattern.sijMax(1, 3)
    s23min = pattern.sijMin(2, 3)
    s23max = pattern.sijMax(2, 3)

    #Setting parameters for grid spacing of integration
    npoints = 1000
    ds13 = ( s13max - s13min ) / npoints
    ds23 = ( s23max - s23min ) / npoints

    #0 indice here represents lower half of plot (positive b) and 1 upper half (negative b)
    X = [[0]*nbinsPhase,[0]*nbinsPhase]
    F = [[0]*nbinsPhase,[0]*nbinsPhase]
    Fbar = [[0]*nbinsPhase,[0]*nbinsPhase]

    sumF = 0
    sumFbar = 0

    #Looping over grid points to numerically evaluate X(b), F(b) and Fbar(b)
    for i in range( npoints ) : 
        s13 = s13min + (i+0.5) * ds13
        for j in range( npoints ) : 
            s23 = s23min + (j+0.5) * ds23

            evt = three_body_event(pattern, s13, s23)

            #Exclude kinematically impossible points
            if (evt == None):
                continue

            #crossTerm is A*(s13,s23)Abar(s13,s23)
            cpp_crossTerm = diffcalc.cross_term(evt)
            crossTerm = complex( cpp_crossTerm.real(), cpp_crossTerm.imag() )      

            #ampSq and cp_ampSq are |A(s13,s23)|^2 and |Abar(s13,s23)|^2
            model = diffcalc.model()
            cp_model = diffcalc.cp_model() 
            ampSq = model.RealVal(evt)
            cp_ampSq = cp_model.RealVal(evt)

            phasediff = getPhaseDifference(evt, s13, s23, diffcalc)

            #Calculating phase bin number of event
            b = getPhaseBin(phasediff, nbinsPhase)

            #Exclude events outside range of bins
            if (b > 8) or (b < 1):
                continue
            
            if (s23 < s13) :
                X[0][b-1] += crossTerm * ds13 * ds23
                F[0][b-1] += ampSq * ds13 * ds23
                Fbar[1][b-1] += cp_ampSq * ds13 * ds23
            elif(s23 > s13) :
                X[1][b-1] += crossTerm * ds13 * ds23
                F[1][b-1] += ampSq * ds13 * ds23
                Fbar[0][b-1] += cp_ampSq * ds13 * ds23  
            else :
                for k in range(2) :
                    X[k][b-1] += 0.5 * crossTerm * ds13 * ds23
                    F[k][b-1] += 0.5 * ampSq * ds13 * ds23
                    Fbar[k][b-1] += 0.5 * cp_ampSq * ds13 * ds23  

            sumF += ampSq * ds13 * ds23
            sumFbar += cp_ampSq * ds13 * ds23 

    for i in range( len(X[0]) ) :
        X[0][i] /= ( F[0][i] * Fbar[1][i] )**0.5
        X[1][i] /= ( F[1][i] * Fbar[0][i] )**0.5

    if (normaliseF) :
        for i in range( len(F[0]) ) :
            for k in range(2) :
                F[k][i] /= sumF
                Fbar[k][i] /= sumFbar

    r = [0]*nbinsPhase
    for i in range(nbinsPhase) :
         r[i] = F[1][i] / F[0][i]
    
    return X, F, Fbar, r




def getRatiosAsymm(pHists, nHists) : 
    """Function to produce array of plots of ratio of counts given in pHists and nHists, as a ROOT TGraphAsymmErrors 
        object.

        Inputs are:
            - pHists: list containing two 2D histograms (one for D0, one for D0bar) binned by decay time and strong phase
              difference. Contains events with positive bin index b.
            - nHists: same as pHists, but for events binned with negative index b.    

        Function returns:
            - ratios: 2D array of plots separated by D0/D0bar tag and strong phase difference binning. Plots are of type 
              TGraphAsymmErrors, in order to allow for Poisson error propogation on division.
    """

    ratios = [[],[]]
    nbinsPhase = pHists[0].GetNbinsY()

    for i in range(2): 
        
        for b in range (1, nbinsPhase + 1) :
              
            ratios[i].append(ROOT.TGraphAsymmErrors())

            numerator = nHists[i].ProjectionX("numerator b{} i{}".format(b,i), b, b)
            denominator = pHists[i].ProjectionX("denominator b{} i{}".format(b,i), b, b)
            ratios[i][b-1].Divide(numerator, denominator, "pois")
    
    return ratios




def getChiSquaredPoisson(params, tAv, tSqAv, r, X, ratios) :
    """Function to calculate chi squared value for R(b,j) fit to data for given real and imaginary parts of zcp and 
         deltaz, using Poisson statistics for errors. 

        Inputs are:
            - params: list containing Re(zcp), Im(zcp), Re(deltaz), Im(deltaz)
            - tAv, tSqAv: list containing averages of t and t^2 in each decay time bin (i.e. <t> and <t^2>)
            - r, X: lists containing values of r(b) and X(b) functions required for the fit. X is 2D array where 0 index 
              refers to list of X(b) for positive b and 1 index refers to list of X(b) for negative b values. 
            - ratios: 2D array of TGraphAysmmErrors, containing measured values of R(b,j). Can be generated using 
              the function getRatiosAsymm.

         Function returns:
             - chiSq: chi squared value for fit to data in ratios given by the values input in params.  
    """

    nbinsPhase = len(ratios[0])
    nbinsTime = len(tAv)
    count = 0

    #Input is setup this way with a list to allow minimisation with scipy.minimize on listed parameters
    re_zcp, im_zcp, re_dz, im_dz = params
    zcp = complex(re_zcp, im_zcp)
    deltaz = complex(re_dz, im_dz)    
 
    chiSq = 0
    fit = getFit(zcp, deltaz, tAv, tSqAv, r, X)

    for i in range(2) :

        for b in range(1,nbinsPhase+1) :

            #pl (plus) refers to D0 data, mi (minus) to D0bar
            expVals = fit[i][b-1].GetY()

            for j in range(ratios[i][b-1].GetN()) :

                expected = expVals[j]
                x = ROOT.Double()
                measured = ROOT.Double() 
                ratios[i][b-1].GetPoint(j, x, measured)

                if (expected < measured) :
                    err_measured = ratios[i][b-1].GetErrorYlow(j)
                    if ( err_measured != 0) :
                        chiSq += ( (measured - expected) / err_measured )**2 
                    else :
                        print "WARNING : Data point ignored (zero error below)"
                        count += 1
                else :
                    err_measured = ratios[i][b-1].GetErrorYhigh(j)
                    if ( err_measured != 0) :
                        chiSq += ( (measured - expected) / err_measured )**2
                    else :
                        print "WARNING : Data point ignored (zero error above)"
                        count += 1

    if(count != 0) :
        print "\nWARNING : {} data points skipped this call (getChiSquaredPoisson).\n".format(count)

    return chiSq



def getcppVecs(X, r, F, tAv, tSqAv, nD0) :
    """
        Function to create vectors from lists, suitable for passing to c++.
           
        Inputs are:
            - X, r, F, tAv, tSqAv : Lists/Nested lists which are to be converted to vectors
            - nD0: scale factor for F

        Function returns:
            - X_cpp, r_cpp, Fm_cpp, Fp_cpp, tAv_cpp, tSqAv_cpp: Vectors suitable for passing
               to c++ functions which contain the values passed in the lists X, r, F, tAv, tSqAv

    """

    nbinsPhase = len(F[0])
    nbinsTime = len(tAv)

    X_cpp = ROOT.vector("complex<double>")()
    r_cpp = ROOT.vector("double")()
    Fm_cpp = ROOT.vector("double")()
    Fp_cpp = ROOT.vector("double")()
    for b in range(nbinsPhase) :
        Xval = ROOT.complex("double")(X[0][b].real, X[0][b].imag)
        X_cpp.push_back(Xval)        
        r_cpp.push_back(r[b])
        Fm_cpp.push_back(F[1][b]*nD0)
        Fp_cpp.push_back(F[0][b]*nD0)

    tAv_cpp = ROOT.vector("double")()
    tSqAv_cpp = ROOT.vector("double")() 
    for j in range(nbinsTime) :
        tAv_cpp.push_back(tAv[j])
        tSqAv_cpp.push_back(tSqAv[j])

    return X_cpp, r_cpp, Fm_cpp, Fp_cpp, tAv_cpp, tSqAv_cpp



def setupPlots(nbinsPhase, binflipfitter, dataPlots, fileNo) :
    """
        Simple function to retrieve fits from an instance of binflipChi2, and setup canvases/plot
        parameters.

        Inputs are:
            - nbinsPhase: number of phase bins
            - binflipfitter: instance of binflipChi2 class from which fits will be obtained. Should have 
              already been minimised using an instance of Minimiser before passing here.
            - dataPlots: list of TH1Fs containing phase binned ratio plots from data

        Function returns:
            - canvas: List of two subdivided canvases for D0/D0bar, divided into one area for each phase bin
            - fits: list of TGraphs containing fit values from fitted parameters
            - RPlots: list of TGraphs containing fit values from known simulation parameters
    """

    #Fits are calculated with fitted Zcp, deltaZ
    fits = [[],[]]
    for i in range(2) :
        for b in range(nbinsPhase) :
            fits[i].append( binflipfitter.getFit(i,b) )

    #RPlots are calculated using known Zcp, deltaZ used for simulation, hence reset paramaters here
    parset = binflipfitter.getParSet()
    for i in range(4) :
        par = parset.getParPtr(i)
        par.resetToInit()

    RPlots = [[],[]]
    for i in range(2) :
        for b in range(nbinsPhase) :
            RPlots[i].append( binflipfitter.getFit(i,b) )

    canvas = []
    canvas.append( ROOT.TCanvas("c1 f{}".format(fileNo), "D0 ratios by bin") )
    canvas[0].Divide(2,4)
    canvas.append( ROOT.TCanvas("c2 f{}".format(fileNo), "D0bar ratios by bin") )
    canvas[1].Divide(2,4)

    for i in range(2) :
        for b in range(1, nbinsPhase + 1) :
            #Data plot
            setPlotParameters(dataPlots[i][b-1], i, b)

            #Fit with simulation parameters
            RPlots[i][b-1].SetMarkerStyle(5)
            RPlots[i][b-1].SetMarkerColor(ROOT.kBlack)

            #Fit with fitted parameters
            fits[i][b-1].SetMarkerStyle(4)
            fits[i][b-1].SetMarkerColor(ROOT.kGreen+3)

    return canvas, fits, RPlots



def averageElements(nestList) :
    """
        Simple function to take a nested(2d) list and return a list containing the average values 
        of each element in the input list.
    """
    avList = []
    for i in range(len(nestList)) :
        avList.append( sum(nestList[i])/len(nestList[i]) )
        
    return avList

