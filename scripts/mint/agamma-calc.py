#!/usr/bin/env python

from math import sin, cos, pi
import ROOT

x = 0.0039
y = 0.0065
qoverp = 0.8
phi = -0.7
eta = 1.
tau = 0.4101

am = (qoverp**2 - 1)/(qoverp**2 + 1)
ag = 0.5 * am * y * cos(phi) - x * sin(phi)
print 'AGamma from params', ag * 1000.

f = ROOT.TF2('ag', '([0] * (0.5 * (x^2 - 1)/(x^2 + 1) * [1] * cos(y) - [2] * sin(y))) * 1000.', 0.5, 1.5, -pi/2., pi/2.)
f.SetParameters(eta, y, x)
f.Draw('colz')
f.GetXaxis().SetTitle('|q/p|')
f.GetYaxis().SetTitle('#phi [rad]')
f.SetTitle('A_{#Gamma} #times 1000')

print 'AGamma from params (TF2)', f.Eval(qoverp, phi)

gammap = 1./tau * (1 + qoverp * (y * cos(phi) - x * sin(phi)))
gammam = 1./tau * (1 + 1./qoverp * (y * cos(phi) + x * sin(phi)))
print 'Tau minus', 1./gammam
print 'Tau plus', 1./gammap
print 'AGamma from taus', (gammap - gammam)/(gammap + gammam) * 1000.
