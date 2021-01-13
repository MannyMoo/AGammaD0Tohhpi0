#!usr/bin/env python

from AGammaD0Tohhpi0.data import datalib
from AnalysisUtils.addmva import add_mva_friend

method = "BDT"
for dataset in datalib.get_matching_datasets('^RealData.*pipipi0_(Merged|Resolved)_TriggerFiltered$'):
    print '\nAdding BDT result to dataset '+dataset+'...\n'
    datatype = 'merged' if 'Merged' in dataset else 'resolved'
    add_mva_friend(datalib, dataset, 'classifiers/'+datatype+'_'+method+'.xml', 
                    method, method, perfile = False, overwrite = True)
