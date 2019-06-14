#!/usr/bin/env python

# Load Mint2 libraries.
import Mint2, ROOT, math
from AGammaD0Tohhpi0.data import datalib
from ROOT import PhaseDifferenceCalc, DalitzEventList, TFile, DalitzEventPattern
from ROOT.MINT import NamedParameterBase
from AGammaD0Tohhpi0.mint import config
from Mint2.utils import three_body_event
from AGammaD0Tohhpi0.mint import pattern_D0Topipipi0, set_default_config
from scipy.optimize import minimize

# Set the config file.
# NamedParameterBase.setDefaultInputFile(config)
set_default_config()

ROOT.TH1.SetDefaultSumw2(True)

# Get the phase difference calculator.
#pattern = DalitzEventPattern(421, 211, -211, 111)
pattern = pattern_D0Topipipi0
diffcalc = PhaseDifferenceCalc(pattern, config)

drawRatioPlots = False
drawFitErrors = True

xHist = ROOT.TH1F("x fit error histogram", "x fit error histogram", 20, -5, 5)
yHist = ROOT.TH1F("y fit error histogram", "y fit error histogram", 20, -5, 5)
qoverpHist = ROOT.TH1F("qoverp fit error histogram", "qoverp fit error histogram", 20, -5, 5)
phiHist = ROOT.TH1F("phi fit error histogram", "phi fit error histogram", 20, -5, 5)


for fileNo in range(1, 100) :
    print "\n Processing file number {}... \n".format(fileNo)
    # Retrieve the dataset as a DalitzEventList
    fdata = TFile.Open('/nfs/lhcb/d2hh01/hhpi0/data/mint/data_3SigmaCPV/pipipi0_{}.root'.format(fileNo)) 
    evtlist = DalitzEventList(fdata.Get('DalitzEventList'))
    evtData = fdata.Get('DalitzEventList')

    nbinsPhase = 8
    phaseMin = 2*math.pi*(-0.5) / nbinsPhase
    phaseMax = 2*math.pi*(nbinsPhase - 0.5) / nbinsPhase
    upperHists = []
    lowerHists = []


    nbinsTime = 25
    tMax = 3

    tList = [] 
    tSqList = [] 
    tAv = []
    tSqAv = [] 

    for i in range( nbinsTime ) : 
        tList.append([])
        tSqList.append([])
        tAv.append(0)
        tSqAv.append(0)

    #Here 0 index is D0 histogram, 1 is D0bar
    for i in range(2) :
        upperHists.append( ROOT.TH2F("upper hist i{} f{}".format(i, fileNo), "", nbinsTime, 0, tMax, nbinsPhase, phaseMin, phaseMax ) )
        lowerHists.append( ROOT.TH2F("lower hist {} f{}".format(i, fileNo), "", nbinsTime, 0, tMax, nbinsPhase, phaseMin, phaseMax ) )

    # Loop over events.
    i = 0
    for evt in evtData :
        phasediff = diffcalc.phase_difference(evtlist[i])
        s13 = evtlist[i].s(1, 3)
        s23 = evtlist[i].s(2, 3)
        tag = evt.tag
        decayTime = evt.decaytime

        # The binning is inverted in the lower half of the Dalitz plot, so invert the phase difference.
        if s23 < s13 :
            phasediff *= -1
        # Use the convention that phases run from 0 to 2pi rather than -pi to +pi.
        if phasediff < 0. :
            phasediff += 2*math.pi

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


        #Storing times to find <t>, <t^2>, with same binning as histograms 
        tBinNo = int( ( nbinsTime * decayTime ) / float(tMax) )
        if (tBinNo < nbinsTime) : 
            tList[tBinNo].append(decayTime) 
            tSqList[tBinNo].append( decayTime**2 ) 

        i += 1


    #Calculate <t> and <t^2> from binned list of decay times
    for i in range( nbinsTime ) : 
        tAv[i] = sum(tList[i]) / len(tList[i])
        tSqAv[i] = sum(tSqList[i]) / len(tSqList[i])


    s13min = pattern.sijMin(1, 3)
    s13max = pattern.sijMax(1, 3)
    s23min = pattern.sijMin(2, 3)
    s23max = pattern.sijMax(2, 3)

    npoints = 1000
    ds13 = ( s13max - s13min ) / npoints
    ds23 = ( s23max - s23min ) / npoints


    #0 indice here represents lower half of plot (positive b) and 1 upper half (negative b)
    X = [[0]*nbinsPhase,[0]*nbinsPhase]
    F = [[0]*nbinsPhase,[0]*nbinsPhase]
    Fbar = [[0]*nbinsPhase,[0]*nbinsPhase]

    for i in range( npoints ) : 
        s13 = s13min + i * ds13
        for j in range( npoints ) : 
            s23 = s23min + j * ds23

            evt = three_body_event(pattern, s13, s23)

            #Exclude kinematically impossible points
            if (evt == None):
                continue

            #crossTerm is |A*(s13,s23) Abar(s13,s23)|
            cpp_crossTerm = diffcalc.cross_term(evt)
            crossTerm = complex( cpp_crossTerm.real(), cpp_crossTerm.imag() )      

            #ampSq and cp_ampSq are |A(s13,s23)|^2 and |Abar(s13,s23)|^2
            model = diffcalc.model()
            cp_model = diffcalc.cp_model() 
            ampSq = model.RealVal(evt)
            cp_ampSq = cp_model.RealVal(evt)

            phasediff = diffcalc.phase_difference(evt)
            # The binning is inverted in the lower half of the Dalitz plot, so invert the phase difference.
            if s23 < s13 :
                phasediff *= -1
            # Use the convention that phases run from 0 to 2pi rather than -pi to +pi.
            if phasediff < 0. :
                phasediff += 2*math.pi

            b = int( phasediff*(nbinsPhase/(2*math.pi)) + 0.5 ) + 1
            #Exclude events outside range of bins
            if (b > 8) or (b < 1):
                continue

            if (s23 < s13) :
                X[0][b-1] += crossTerm * ds13 * ds23
                F[0][b-1] += ampSq * ds13 * ds23
                Fbar[1][b-1] += cp_ampSq * ds13 * ds23
            elif (s23 > s13):
                X[1][b-1] += crossTerm * ds13 * ds23
                F[1][b-1] += ampSq * ds13 * ds23
                Fbar[0][b-1] += cp_ampSq * ds13 * ds23  

    for i in range( len(X[0]) ) :
        X[0][i] /= ( F[0][i] * Fbar[1][i] )**0.5
        X[1][i] /= ( F[1][i] * Fbar[0][i] )**0.5

    r = [0]*nbinsPhase
    for i in range(nbinsPhase) :
        r[i] = F[1][i] / F[0][i]


    # print "-"*135, "\n"
    # print "\t b", "\t"*4, "Xb", " \t "*4, " Fb", "\t"*3, " Fb bar", " \t "*2, "rb\n"
    # print"-"*135, "\n"
    # for i in range(nbinsPhase) :
    #     print "\t {}\t\t {}\t\t{}\t\t{}\t\t{}\n".format( i+1, X[0][i], F[0][i], Fbar[0][i], r[i] )
    #     print "\t{}\t\t {}\t\t{}\t\t{}\n".format(-1*(i+1), X[1][i], F[1][i], Fbar[1][i] )


    #3Sigma_CPV simulation variables
    x = 0.0039
    y = 0.0065
    qoverp = 0.8
    phi = -0.7

    def getZvals(x, y, qoverp, phi) :
        poverq = 1/qoverp

        xcp = 0.5*( x*math.cos(phi) * ( qoverp + poverq ) + y*math.sin(phi) * ( qoverp - poverq ) )
        deltax = 0.5*( x*math.cos(phi) * ( qoverp - poverq ) + y*math.sin(phi) * ( qoverp + poverq ) )

        ycp = 0.5*( y*math.cos(phi) * ( qoverp + poverq ) - x*math.sin(phi) * ( qoverp - poverq )  ) 
        deltay = 0.5*( y*math.cos(phi) * ( qoverp - poverq ) - x*math.sin(phi) * ( qoverp + poverq ) )

        zcp = complex(-1*ycp, -1*xcp)
        deltaz = complex(-1*deltay, -1*deltax)

        return zcp, deltaz

    zcp, deltaz = getZvals(x,y,qoverp,phi)

    def getFit(zcp, deltaz, nbinsTime, nbinsPhase) :

        RPlots =[[],[]]

        for i in range(2) :
            for b in range(1, nbinsPhase+1) :  
                #0 index is Rplus (D0) and 1 is Rminus (D0bar)
                RPlots[i].append( ROOT.TGraph(nbinsTime) )   

                for j in range(1, nbinsTime+1) :

                    num1 = r[b-1]*( 1 + 0.25*tSqAv[j-1] * (zcp**2 - deltaz**2 ).real )
                    num2 = 0.25*tSqAv[j-1]*(abs(zcp + ((-1)**i)*deltaz)**2)
                    num3 = (r[b-1]**0.5) * tAv[j-1] * ( X[0][b-1].conjugate() * (zcp +((-1)**i)*deltaz) ).real
                    numerator = num1 + num2 + num3

                    den1 = 1 + 0.25*tSqAv[j-1] * ( zcp**2 - deltaz**2 ).real
                    den2 = r[b-1] * 0.25 * (abs(zcp + ((-1)**i)*deltaz))**2
                    den3 = (r[b-1]**0.5) * tAv[j-1] * ( X[0][b-1] * (zcp + ((-1)**i)*deltaz) ).real
                    denominator = den1 + den2 + den3

                    Rval = numerator / denominator
                    RPlots[i][b-1].SetPoint(j-1, tAv[j-1], Rval)

        return RPlots

    def getChiSquared(params, nbinsTime, nbinsPhase, pHist, nHist) :
        #pHist is array containing 2D D0 and D0bar histograms of decay times and phases with +ve b indexes
        #nHist is equivalent with negative b
        x, y, qoverp, phi  = params

        zcp, deltaz = getZvals(x,y,qoverp,phi)

        chiSq = 0
        fit = getFit(zcp, deltaz, nbinsTime, nbinsPhase)

        for b in range(1,nbinsPhase+1) :
            Rvals_pl = fit[0][b-1].GetY()            
            Rvals_mi = fit[1][b-1].GetY()

            for j in range(1,nbinsTime+1) : 
                R_pl = Rvals_pl[j-1]
                R_mi = Rvals_mi[j-1]  

                D0_num = ( nHist[0].GetBinContent(j,b) - pHist[0].GetBinContent(j,b) * R_pl )**2
                D0_den =   ( nHist[0].GetBinError(j,b) )**2 + ( pHist[0].GetBinError(j,b) * R_pl )**2 
                if (D0_den != 0) :
                    D0_term = D0_num / D0_den
                else:
                    D0_term = 0

                D0bar_num = ( nHist[1].GetBinContent(j,b) - pHist[1].GetBinContent(j,b) * R_mi )**2
                D0bar_den =   ( nHist[1].GetBinError(j,b) )**2 + ( pHist[1].GetBinError(j,b) * R_mi )**2 
                if (D0bar_den != 0) :
                    D0bar_term = D0bar_num / D0bar_den
                else:
                    D0bar_term = 0

                chiSq += D0_term + D0bar_term

        return chiSq

    RPlots = getFit(zcp, deltaz, nbinsTime, nbinsPhase)
    result = minimize(getChiSquared, [0.0039, 0.0065, 0.8, -0.7], (nbinsTime, nbinsPhase, lowerHists, upperHists))
    xFit, yFit, qoverpFit, phiFit = result.x
    opt_zcp, opt_deltaz = getZvals( xFit, yFit, qoverpFit, phiFit )
    optFits = getFit(opt_zcp, opt_deltaz, nbinsTime, nbinsPhase)
    print "Optimisation results:\t x: {}\t y: {}\t qoverp: {}\t phi: {}".format(result.x[0], result.x[1], result.x[2], result.x[3])
    print "Optimisation Errors: \t errx: {}\t erry: {}\t errqoverp: {}\t errphi: {}".format(result.hess_inv[0][0]**0.5,result.hess_inv[1][1]**0.5,result.hess_inv[2][2]**0.5,result.hess_inv[3][3]**0.5)
    print "Simulation parameters:\t x: {}\t\t y: {}\t\t qoverp: {}\t\t phi: {}".format(x, y, qoverp, phi) 

    xHist.Fill( (x - xFit) / x)
    yHist.Fill( (y - yFit) / y)
    qoverpHist.Fill( (qoverp - qoverpFit) / qoverp)
    phiHist.Fill( (phi - phiFit) / phi)


    def setPlotParameters(plot, tag, plotNo):

        xAxis = plot.GetXaxis()
        xAxis.SetTitle("Decay Time (ps)")
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



    if (drawRatioPlots) :

        ratioPlots = [[],[]]
        canvas = []
        canvas.append( ROOT.TCanvas("c1 f{}".format(fileNo), "D0 ratios by bin") )
        canvas[0].Divide(2,4)
        canvas.append( ROOT.TCanvas("c2 f{}".format(fileNo), "D0bar ratios by bin") )
        canvas[1].Divide(2,4)

        for i in range(2) :
            for b in range(1, nbinsPhase + 1) :

                ratioPlots[i].append(ROOT.TH1F("Plot b{}, t{} f{}".format(b,i,fileNo), "Plot b{}, t{} f{}".format(b,i,fileNo), nbinsTime, 0, tMax))

                #Take slices of 2D histograms in one phase bin
                upperHist = upperHists[i].ProjectionX("upper b{}, t{} f{}".format(b,i,fileNo), b, b)
                lowerHist = lowerHists[i].ProjectionX("lower b{}, t{} f{}".format(b,i,fileNo), b, b)

                #Create plot by ratio of counts in each bin
                ratioPlots[i][b-1] = upperHist
                ratioPlots[i][b-1].Divide(lowerHist)

                #Drawing plot
                canvas[i].cd(b)
                setPlotParameters(ratioPlots[i][b-1], i, b)
                ratioPlots[i][b-1].Draw()

                #Drawing fit with simulation parameters
                RPlots[i][b-1].SetMarkerStyle(5)
                RPlots[i][b-1].Draw('Same P')

                #Drawing fit with fitted parameters
                optFits[i][b-1].SetMarkerStyle(4)
                optFits[i][b-1].SetMarkerColor(2)
                optFits[i][b-1].Draw('Same P')


    print "File number {} processed.".format(fileNo) 




if (drawFitErrors) :
    errCanvas = ROOT.TCanvas("c3", "Fit errors")
    errCanvas.Divide(2,2)
    errCanvas.cd(1)
    xHist.Draw()
    errCanvas.cd(2)
    yHist.Draw()
    errCanvas.cd(3)
    qoverpHist.Draw()
    errCanvas.cd(4)
    phiHist.Draw()
    errCanvas.SaveAs("/home/ppe/n/nmchugh/SummerProject/ErrPlot.png")
