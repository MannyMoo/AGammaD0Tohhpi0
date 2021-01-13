#!/usr/bin/env python

from StrippingDoc import latest_pp_bkpaths_for_line
from AnalysisUtils.diracutils import get_bk_data, get_bk_decay_paths
import os

evttypes = {27163400 : 'Kpipi0_DecProdCut_PHSP',
            27163403 : 'pipipi0_DecProdCut_PHSP',
            27163404 : 'pipipi0_DecProdCut_Dalitz',
            27163405 : 'Kpipi0_DecProdCut_Dalitz',
            27263400 : 'Kpipi0_cocktail_DecProdCut',
            27163401 : 'KKpi0_phipi0_TightCut',
            27163470 : 'KKpi0_phipi0_TighterCut',
            }

def get_real_data():
    for year in range(2015, 2019):
        for path in latest_pp_bkpaths_for_line('StrippingDstarD0ToHHPi0_pipipi0_M_Line', year):
            mag = 'Up' if 'MagUp' in path else 'Down'
            fout = os.path.join(os.environ['AGAMMAD0TOHHPI0ROOT'], 'options/data/real/{year}_Charm_Mag{mag}.py'.format(**locals()))
            print path
            print fout
            get_bk_data(path, fout, rootvar = 'AGAMMAD0TOHHPI0ROOT', nfiles = 20, ignore = True)

def get_mc_paths(namecheck = None, exclusions = ('GAUSSHIST', 'STRIP', 'LDST', 'XDIGI', 'Stripping24[^r]', 'Stripping28[^r]')) :
    if not namecheck:
        namecheck = lambda x : True
    for evttype, name in evttypes.items() :
        if not namecheck(name):
            continue
        fname = os.path.expandvars('$AGAMMAD0TOHHPI0ROOT/python/AGammaD0Tohhpi0/MCBKPaths/MCBKPaths_{0}.py'.format(name))
        get_bk_decay_paths(evttype, exclusions = exclusions,
                           outputfile = fname)

def get_mc_data() :
    for evttype, name in evttypes.items() :
        modname = 'AGammaD0Tohhpi0.MCBKPaths.MCBKPaths_{0}'.format(name)
        mod = __import__(modname, fromlist = ['decaypaths'])
        for year, paths in mod.decaypaths.items() :
            if not year in ('2011', '2012', '2015', '2016', '2017', '2018') :
                continue
            for path in paths :
                fname = os.path.expandvars('$AGAMMAD0TOHHPI0ROOT/options/data/mc/{0}_{1}_{2}.py'.format(name, year, path['path'][1:].replace('/', '_')))
                print fname, path
                get_bk_data(path['path'], fname, nfiles = 20, ignore = True)

if __name__ == '__main__' :
    #get_real_data()
    get_mc_paths((lambda n : n.startswith('pipipi0')),
                 exclusions = ('GAUSSHIST', 'XDIGI', 'Stripping24[^r]', 'Stripping28[^r]', 'D2HMUNU'))
    #get_mc_data()
