#!/usr/bin/env python

import Mint2, os, sys, argparse
from ROOT import FlexiFastAmplitudeIntegrator, FitAmpSum, DalitzEventPattern
from AGammaD0Tohhpi0.mint import set_default_config

argparser = argparse.ArgumentParser()
argparser.add_argument('--fname', default = '$AGAMMAD0TOHHPI0ROOT/scripts/mint/KKpi0.txt', help = 'Config file name.')
argparser.add_argument('--pattern', nargs = '*', default = (421, 321, -321, 111), help = 'Dalitz event pattern', type = int)
argparser.add_argument('--precision', default = 1e-2, type = float, help = 'Integrator precision')

args = argparser.parse_args()

set_default_config(os.path.expandvars(args.fname))

pattern = DalitzEventPattern(*args.pattern)

amps = FitAmpSum(pattern)
integ = FlexiFastAmplitudeIntegrator(pattern, amps)
integ.setPrecision(args.precision)
integ.doFractions()
print '\n'
print 'Fit fractions:'
for frac in integ.getFractions():
    print frac.name().ljust(40), frac.frac()
