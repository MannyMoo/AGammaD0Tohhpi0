#!/usr/bin/env python

from AGammaD0Tohhpi0.backgrounds import gen_background
from AGammaD0Tohhpi0.data import datalib

histos = {}
for dataset in 'Data_2015_pipipi0_Resolved_Mag{mag}', :
    for mag in 'Up', 'Down':
        name = dataset.format(mag = mag)
        histos[name] = gen_background(datalib, name)
