#!/usr/bin/env python

# Load Mint2 libraries.
import Mint2, ROOT, math, sys
from AGammaD0Tohhpi0.data import datalib
from ROOT import PhaseDifferenceCalc, DalitzEventList, TFile, DalitzEventPattern
from ROOT.MINT import NamedParameterBase
from AGammaD0Tohhpi0.mint import config, set_default_config, get_config
from AGammaD0Tohhpi0.binflip import plotBinNumbers

if len(sys.argv) > 1 :
    name = sys.argv[1]
    config = get_config(name).fnames[0]

# Set the config file.
set_default_config(config)

h = plotBinNumbers(config, 8, 1000)
c = ROOT.TCanvas('c', '', 600, 600)
h.Draw('colz')
c.SaveAs('binnumber-vs-dalitz.pdf')
