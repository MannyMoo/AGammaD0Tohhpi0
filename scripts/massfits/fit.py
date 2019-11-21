#!/usr/bin/env python

from AGammaD0Tohhpi0.data import datalib
from AnalysisUtils.fit import multi_gauss, translate_scale_pdf
from AGammaD0Tohhpi0.workspace import workspace
from AnalysisUtils.plot import plot_fit
import ROOT
from ROOT import RooFit

mcdata = datalib.MC_2016_pipipi0_Dataset()
dm = workspace.roovar('deltam')
g1 = multi_gauss(workspace, 'g1', dm, 145.4, [(0.5, 0.5), (0.5, 1.5), 2.], 10.)
g1.fitTo(mcdata)

frame = dm.frame()
mcdata.plotOn(frame)
g1.plotOn(frame)

g2 = translate_scale_pdf(workspace, g1, 'g2', dm, workspace.roovar('trans', val = 0.5), workspace.roovar('scale', val = 1.5))
g2.plotOn(frame, RooFit.LineColor(ROOT.kRed))
