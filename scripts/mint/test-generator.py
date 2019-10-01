#!/usr/bin/env python

import Mint2, ROOT, os
from ROOT import DalitzEvent, PhaseDifferenceCalc, TF1, TH1F, DiskResidentEventList
from AGammaD0Tohhpi0.mint import pattern_D0Topipipi0, get_config, set_default_config, pattern_D0barTopipipi0
from AGammaD0Tohhpi0.data import datalib
from cmath import rect
ROOT.TH1.SetDefaultSumw2()

name = 'test-large-mix-10'
config = get_config(name, 0)
set_default_config(config.fnames[0])

from ROOT import TimeDependentGenerator

def meanvalue(h, xmin, xmax) :
    binmin = h.GetXaxis().FindBin(xmin)
    binmax = h.GetXaxis().FindBin(xmax)
    mean = 0.
    weights = 0.
    for i in xrange(binmin+1, binmax-1) :
        weight = 1.
        mean += h.GetBinContent(i)
        weights += weight
    weightmin = (h.GetXaxis().GetBinUpEdge(binmin) - xmin)/h.GetXaxis().GetBinWidth(binmin)
    mean += h.GetBinContent(binmin) * weightmin
    weights += weightmin
    weightmax = (xmax - h.GetXaxis().GetBinLowEdge(binmax))/h.GetXaxis().GetBinWidth(binmin)
    mean += h.GetBinContent(binmax) * weightmax
    weights += weightmax
    return mean/weights

x = config.float('x')
y = config.float('y')
qoverp = config.float('qoverp')
phi = config.float('phi')
lifetime = config.float('lifetime')
width = 1./lifetime
deltam = x * width
deltagamma = y * 2 * width

rndm = ROOT.TRandom3(0)

generator = TimeDependentGenerator(pattern_D0Topipipi0, width, deltam, deltagamma, qoverp, phi, rndm)

tree = datalib.get_data('MINT_' + name)
evtlist = DiskResidentEventList(datalib.get_data_info('MINT_' + name)['files'][0], 'OPEN')

diffcalc = PhaseDifferenceCalc(pattern_D0Topipipi0, config.fnames[0])

for i in xrange(tree.GetEntries()) :
    tree.GetEntry(i)
    if tree.tag == 1 :
        evt = evtlist.getEvent(i)
        break
for i in xrange(tree.GetEntries()) :
    tree.GetEntry(i)
    if tree.tag == -1 :
        cpevt = evtlist.getEvent(i)
        break
print 'pattern size', evt.eventPattern().size()
s13 = evt.s(1, 2)
s23 = evt.s(2, 3)
print 's13', s13, 's23', s23

z = complex(-config.float('y'), -config.float('x'))
qoverp = rect(config.float('qoverp'), config.float('phi'))

print 'Pattern:'
#getattr(pattern_D0Topipipi0, 'print')()
#getattr(pattern_D0barTopipipi0, 'print')()
print 'Model amps:'
diffcalc.model().printAllAmps(evt)
print 'CP model amps:'
diffcalc.cp_model().printAllAmps(cpevt)

Fp = diffcalc.model().RealVal(evt)
Fm = diffcalc.cp_model().RealVal(evt)
Fmcp = diffcalc.model().RealVal(cpevt)
Fpcp = diffcalc.cp_model().RealVal(cpevt)
X = diffcalc.cross_term(evt)
X = complex(X.real(), X.imag())
X /= (Fp * Fm)**.5
Xcp = diffcalc.cross_term(cpevt)
Xcp = complex(Xcp.real(), Xcp.imag()).conjugate()
Xcp /= (Fpcp * Fmcp)**.5
lifetime = config.float('lifetime')

rezsq = (z**2).real
magsqz = abs(z)**2

print z, z**2
print 'Fp', Fp, 'Fm', Fm, 'Fpcp', Fpcp, 'Fmcp', Fmcp, 'X', X, 'Xcp', Xcp

fplotsvstime = ROOT.TFile(os.path.join(os.path.dirname(config.fnames[0]), 'plotsVsTime.root'))

gp = 'exp(-x/{lifetime})/{lifetime} * (1 + 0.25 * (x/{lifetime})^2 * {rezsq})'.format(**locals())
gm = '0.25 * exp(-x/{lifetime})/{lifetime} * (x/{lifetime})^2 * {magsqz}'.format(**locals())
gc = '0.5 * exp(-x/{lifetime})/{lifetime} * x/{lifetime}'.format(**locals())

canvs = []
tmax = 8.2
nbins = 300
for tag in 1, -1 :
    _Fp = Fp
    _Fm = Fm
    _X = X
    _evt = evt
    qoverpsq = abs(qoverp)**2
    crossterm = (qoverp * _X * z).real
    if tag == -1 :
        _Fp, _Fm = _Fm, _Fp
        _X = Xcp
        _evt = cpevt
        qoverpsq = 1./qoverpsq
        crossterm = (1./qoverp * _X * z).real
    c = ROOT.TCanvas()
    canvs.append(c)
    htime = TH1F('time_tag' + str(tag), '', nbins, 0, tmax)
    tree.Draw('decaytime >> ' + htime.GetName(), 'tag == ' + str(tag))
    # t1 = 0.25 * abs(z)**2 * abs(qoverp)**(tag * 2) * _Fm
    # t2 = (_Fp*_Fm)**.5 * (qoverp**tag * _X * z).real
    # formstr = '[0] * {_Fp} * (1 + 0.25 * {rezsq} * (x/{lifetime})^2) + [0] * {t1} * (x/{lifetime})^2 + {t2} * x'.format(**locals())
    # formstr = 'exp(-x/{1})/{1} * ({0})'.format(formstr, lifetime)
    formstr = '[0] * ({_Fp} * {gp} + {qoverpsq} * {_Fm} * {gm} + 2 * sqrt({_Fm}*{_Fp}) * {gc} * {crossterm})'.format(**locals())
    print formstr
    form = TF1('form_tag' + str(tag), formstr, 0, tmax)
    form.SetParameter(0, 1.)
    form.FixParameter(0, htime.Integral('width')/form.Integral(0, tmax))
    htime.Draw()
    form.SetLineWidth(4)
    form.SetLineColor(ROOT.kBlue)
    form.Draw('same')

    # hform = TH1F('hform_tag' + str(tag), '', nbins * 10, 0, tmax)
    # henv = TH1F('henv_tag' + str(tag), '', nbins * 10, 0, tmax)
    # for i in xrange(1, hform.GetNbinsX()+1) :
    #     t = hform.GetXaxis().GetBinCenter(i)
    #     val = generator.pdf_value(tag, t, _evt)
    #     hform.SetBinContent(i, val)
    #     hform.SetBinError(i, 0.)
    #     val2 = generator.envelope_value(t, _evt)
    #     henv.SetBinContent(i, val2)
    #     henv.SetBinError(i, 0.)
    #     # if val > val2 :
    #     #     print 'tag', tag, 'time', t, 'pdf val', val, 'env val', val2, 'ratio', val/val2

    hform = fplotsvstime.Get('pdf_vs_time_tag' + str(tag))
    henv = fplotsvstime.Get('env_vs_time_tag' + str(tag))

    scale = htime.Integral('width')/hform.Integral('width')
    hform.Scale(scale)
    hform.SetLineColor(ROOT.kGreen+2)
    hform.SetLineWidth(2)
    hform.Draw('same')
    henv.Scale(scale)
    henv.SetLineColor(ROOT.kRed+2)
    henv.SetLineWidth(3)
    henv.Draw('same')

    hpull = ROOT.TH1F('pull_tag' + str(tag), '', nbins, 0, tmax)
    for i in xrange(1, hpull.GetNbinsX()+1) :
        t = hpull.GetXaxis().GetBinCenter(i)
        try :
            mean = meanvalue(hform, htime.GetXaxis().GetBinLowEdge(i), htime.GetXaxis().GetBinUpEdge(i))
            hpull.SetBinContent(i, (htime.GetBinContent(i) - mean)/htime.GetBinError(i))
        except ZeroDivisionError :
            hpull.SetBinContent(i, 0.)
        hpull.SetBinError(i, 0.)
    cpull = ROOT.TCanvas('pull_tag' + str(tag), 'pull_tag' + str(tag))
    hpull.Draw()
    
    canvs.append([htime, form, hform, henv, hpull, cpull])
    print 'Histo mean:', htime.GetMean(), '+/-', htime.GetMeanError(), 'form mean:', form.Mean(0, tmax), 'hform mean:', hform.GetMean(), 'mean diff pull:', (htime.GetMean() - hform.GetMean())/htime.GetMeanError()
