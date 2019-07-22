#!/usr/bin/env python

from math import sin, cos, pi
import ROOT, sys
from AGammaD0Tohhpi0.mint import get_config

jobname = sys.argv[1]
config = get_config(jobname)

x = float(config['x'][0])
y = float(config['y'][0])

qoverp = float(config['qoverp'][0])
phi = float(config['phi'][0])
eta = 1.
tau = float(config['lifetime'][0])

am = (qoverp**2 - 1)/(qoverp**2 + 1)
ag = 0.5 * am * y * cos(phi) - x * sin(phi)
print('AGamma from params', ag * 1000.)

# f = ROOT.TF2('ag', '([0] * (0.5 * (x^2 - 1)/(x^2 + 1) * [1] * cos(y) - [2] * sin(y))) * 1000.', 0.5, 1.5, -pi/2., pi/2.)
# f.SetParameters(eta, y, x)
# f.Draw('colz')
# f.GetXaxis().SetTitle('|q/p|')
# f.GetYaxis().SetTitle('#phi [rad]')
# f.SetTitle('A_{#Gamma} #times 1000')

# print('AGamma from params (TF2)', f.Eval(qoverp, phi))

gammap = 1./tau * (1 + qoverp * (y * cos(phi) - x * sin(phi)))
gammam = 1./tau * (1 + 1./qoverp * (y * cos(phi) + x * sin(phi)))
print('Tau minus', 1./gammam)
print('Tau plus', 1./gammap)
print('AGamma from taus', (gammap - gammam)/(gammap + gammam) * 1000.)
