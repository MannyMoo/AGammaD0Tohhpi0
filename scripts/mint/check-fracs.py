#!/usr/bin/env python

import Mint2, os, sys, argparse
from ROOT import FlexiFastAmplitudeIntegrator, FitAmpSum, DalitzEventPattern
from AGammaD0Tohhpi0.mint import set_default_config, ConfigFile

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

targets = {"D0->K*(1410)+(->K+,pi0),K-" : 3.7,
           "D0->K*(1410)bar-(->K-,pi0),K+": 4.8,
           "D0->K*(892)+(->K+,pi0),K-" : 45.2,
           "D0->K*(892)bar-(->K-,pi0),K+" : 16.,
           "D0->f(0)(980)0(->K+,K-),pi0" : 6.7,
           "D0->f(2)'(1525)0(->K+,K-),pi0" : 0.08,
           "D0->phi(1020)0(->K+,K-),pi0" : 19.3,
           "LassD0->K(0)*(1430)+(->K+,pi0),K-" : 16.3,
           "LassD0->K(0)*(1430)bar-(->K-,pi0),K+" : 2.7}

norm = "D0->K*(892)+(->K+,pi0),K-"
for frac in integ.getFractions():
    if frac.name()==norm:
        normfrac = frac.frac()
        break

print '\nScales:'
scales = {}
for frac in integ.getFractions():
    if frac.name()==norm:
        continue
    rexp = targets[frac.name()]/targets[norm]
    robs = frac.frac()/normfrac
    scale = (rexp/robs)**.5
    scales[frac.name()] = scale
    print frac.name().ljust(40), scale

print '\nNew pars:'
config = ConfigFile(args.fname)
for name, scale in scales.items():
    for suff in '_Re', '_Im':
        val = float(config[name + suff][1])
        print '{0:<50} 0 {1:.5f} 0.1'.format('"' + name + suff + '"', val*scale)
