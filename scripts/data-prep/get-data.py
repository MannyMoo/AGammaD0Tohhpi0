#!/usr/bin/env python

from StrippingDoc import latest_pp_bkpaths_for_line
from AnalysisUtils.diracutils import get_bk_data
import os

for year in range(2015, 2019):
    for path in latest_pp_bkpaths_for_line('StrippingDstarD0ToHHPi0_pipipi0_M_Line', year):
        mag = 'Up' if 'MagUp' in path else 'Down'
        fout = os.path.join(os.environ['AGAMMAD0TOHHPI0ROOT'], 'options/data/real/{year}_Charm_Mag{mag}.py'.format(**locals()))
        print path
        print fout
        get_bk_data(path, fout, rootvar = 'AGAMMAD0TOHHPI0ROOT', nfiles = 20, ignore = True)
