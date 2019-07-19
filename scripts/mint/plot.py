#!/usr/bin/env python

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.TH1.SetDefaultSumw2()
ROOT.gStyle.SetOptFit()
from uncertainties import ufloat
from AGammaD0Tohhpi0.data import datalib, workingdir

mp = '((_1_pi#_E + _3_pi0_E)^2 - (_1_pi#_Px + _3_pi0_Px)^2 - (_1_pi#_Py + _3_pi0_Py)^2 - (_1_pi#_Pz + _3_pi0_Pz)^2)'
mm = mp.replace('1_pi#', '2_pi~')
m0 = mp.replace('3_pi0', '2_pi~')

mpi0 = 134.5
mpip = 139.6
mdz = 1864.84
mcmin = mpi0**2 + mpip**2 - 50
mcmax = mdz**2 - mcmin + 100
mzmin = 2*mpip**2 - 50
mzmax = mdz**2 - mzmin + 100

#tree = datalib.get_data('MINT_data_NoCPV_x=2.5')
tree = datalib.get_data('MINT_test-new')
#tree = datalib.get_data('MINT_test-new-2')
#datalib.datapaths['MINT_data_3SigmaCPV']['files'] = datalib.datapaths['MINT_data_3SigmaCPV']['files'][:10]
#tree = datalib.get_data('MINT_data_3SigmaCPV')

canv = ROOT.TCanvas('canv', '', 600, 600)
plots = {}
for name, form in {'dalitz' : '{0} : {1} >> h(100, {2}, {3}, 100, {2}, {3})'.format(mm, mp, mcmin, mcmax),
                   'mplus' : '{0} >> h(100, {1}, {2})'.format(mp, mcmin, mcmax),
                   'mminus' : '{0} >> h(100, {1}, {2})'.format(mm, mcmin, mcmax),
                   'mzero' : '{0} >> h(100, {1}, {2})'.format(m0, mzmin, mzmax),
                   'time' : 'decaytime >> h(100, 0, 4.1)'}.items() :
    plots[name] = {}
    for tag in '-1', '+1' :
        tree.Draw(form, 'tag == ' + tag, 'colz')
        h = ROOT.gDirectory.Get('h')
        h.SetName(name + '_tag_' + str(tag))
        plots[name][tag] = h
        canv.SaveAs(name + '_tag_' + tag + '.pdf')
        nbins = 41
        binwidth = 0.1
        #nbins = 2
        #binwidth = 5.
        #nbins = 0
        if name == 'time' :
            continue
        # for i in xrange(nbins) :
        #     time = i*binwidth
        #     tree.Draw(form, 'tag == ' + tag + ' && {0} < decaytime && decaytime <= {1}'.format(time, time+binwidth), 'colz')
        #     canv.SaveAs('timebins/' + name + '_tag_' + tag + '_timebin_' + str(i).zfill(2) + '.pdf')

for name, hp, hm in (('mplus', plots['mplus']['+1'], plots['mminus']['-1']),
                     ('mminus', plots['mminus']['+1'], plots['mplus']['-1']),
                     ('mzero', plots['mzero']['+1'], plots['mzero']['-1'])) :
    hp.SetLineColor(ROOT.kBlack)
    hp.Draw()
    hm.SetLineColor(ROOT.kBlue)
    hm.Draw('same')
    canv.SaveAs(name + '_comparetags.pdf')

asym = ROOT.TH1F(plots['time']['+1'])
asym.SetName('asym')
for i in xrange(1, asym.GetNbinsX()+1) :
    np = ufloat(plots['time']['+1'].GetBinContent(i), plots['time']['+1'].GetBinError(i))
    nm = ufloat(plots['time']['-1'].GetBinContent(i), plots['time']['-1'].GetBinError(i))
    try :
        abin = (np - nm)/(np + nm)
    except ZeroDivisionError :
        abin = ufloat(0., 0.)
    asym.SetBinContent(i, abin.nominal_value)
    asym.SetBinError(i, abin.std_dev)
fit = ROOT.TF1('fit', '[0] - [1] * x / 0.4101', 0, asym.GetXaxis().GetXmax())
asym.Fit(fit)
asym.Draw()
canv.SaveAs('time_asym.pdf')
print 'AGamma from asym. fit: ({0:.2f} +/- {1:.2f}) x 1e-3 - {2:.2f} sigma'.format(fit.GetParameter(1)*1000.,
                                                                    fit.GetParError(1)*1000.,
                                                                    fit.GetParameter(1)/fit.GetParError(1))
taup = ufloat(plots['time']['+1'].GetMean(), plots['time']['+1'].GetMeanError())
taum = ufloat(plots['time']['-1'].GetMean(), plots['time']['-1'].GetMeanError())
ag = (taum - taup)/(taum + taup)
print 'taup', taup, 'taum', taum
print 'AGamma from taus: ({0:.2f} +/- {1:.2f}) x 1e-3 - {2:.2f} sigma'.format(ag.nominal_value*1000.,
                                                                              ag.std_dev*1000.,
                                                                              ag.nominal_value/ag.std_dev)
