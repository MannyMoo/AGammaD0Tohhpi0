#!/usr/bin/env python

import Mint2, ROOT
from ROOT import DalitzEvent, PhaseDifferenceCalc, DalitzEventList, TF1, TH1F
from AGammaD0Tohhpi0.mint import pattern_D0Topipipi0, get_config, set_default_config, pattern_D0barTopipipi0
from AGammaD0Tohhpi0.data import datalib
from cmath import rect

name = 'test-large-mix-2'
config = get_config(name)
set_default_config(config.fnames[0])

tree = datalib.get_data('MINT_' + name)
evtlist = DalitzEventList()
evtlist.fromNtuple(tree)

diffcalc = PhaseDifferenceCalc(pattern_D0Topipipi0, config.fnames[0])

s13 = (pattern_D0Topipipi0.sijMax(1, 3) + pattern_D0Topipipi0.sijMin(1, 3))*2/3.
s23 = (pattern_D0Topipipi0.sijMax(2, 3) + pattern_D0Topipipi0.sijMin(2, 3))*1/3.
evt = DalitzEvent(pattern_D0Topipipi0, s13, s23)
cpevt = DalitzEvent(pattern_D0barTopipipi0, s23, s13)

z = complex(-config.float('y'), -config.float('x'))
qoverp = rect(config.float('qoverp'), config.float('phi'))

Fp = diffcalc.model().RealVal(evt)
Fm = diffcalc.cp_model().RealVal(evt)
Fpcp = diffcalc.model().RealVal(cpevt)
Fmcp = diffcalc.cp_model().RealVal(cpevt)
X = diffcalc.cross_term(evt)
X = complex(X.real(), X.imag())
Xcp = diffcalc.cross_term(cpevt)
Xcp = complex(Xcp.real(), Xcp.imag())
lifetime = config.float('lifetime')

rezsq = (z**2).real
print z, z**2
print 'Fp', Fp, 'Fm', Fm, 'Fpcp', Fpcp, 'Fmcp', Fmcp, 'X', X, 'Xcp', Xcp

canvs = []
for tag in 1, -1 :
    _Fp = Fp
    _Fm = Fm
    _X = X
    if tag == -1 :
        _Fp, _Fm = _Fm, _Fp
        _X = Xcp
    c = ROOT.TCanvas()
    canvs.append(c)
    htime = TH1F('time_tag' + str(tag), '', 100, 0, 4.1)
    tree.Draw('decaytime >> ' + htime.GetName(), 'tag == ' + str(tag))
    t1 = 0.25 * abs(z)**2 * abs(qoverp)**(tag * 2) * _Fm
    t2 = (_Fp*_Fm)**.5 * (qoverp**tag * _X * z).real
    formstr = '[0] * {_Fp} * (1 + 0.25 * {rezsq} * (x/{lifetime})^2) + [0] * {t1} * (x/{lifetime})^2 + {t2} * x'.format(**locals())
    formstr = 'exp(-x/{1})/{1} * ({0})'.format(formstr, lifetime)
    print formstr
    form = TF1('form_tag' + str(tag), formstr, 0, 4.1)
    form.SetParameter(0, 1.)
    form.FixParameter(0, htime.Integral('width')/form.Integral(0, 4.1))
    htime.Draw()
    form.Draw('same')
    canvs.append([htime, form])
