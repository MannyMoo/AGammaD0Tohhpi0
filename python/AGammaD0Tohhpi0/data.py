'''Functions to access all the relevant datasets for the analysis, both TTrees and RooDataSets.'''

import os, ROOT, pprint, glob
from AnalysisUtils.data import DataLibrary
from AGammaD0Tohhpi0.variables import variables
from AGammaD0Tohhpi0.selection import selection_R

datadir = os.environ.get('AGAMMAD0TOHHPI0DATADIR', 
                         '/nfs/lhcb/d2hh01/hhpi0/')
varnames = ('deltam',)

# All the TTree datasets, the tree names and file names (any number of file names can be given).
datapaths = {'Data_2015_pipipi0' : ('DecayTree', os.path.join(datadir, 'data/DaVinciTuples_S24r1_part_pipipi0.root')),
             'Data_2016_pipipi0_HLT2TIS' : ('DecayTree', os.path.join(datadir, 'data/DaVinciTuples_HLT2TIS.root')),
             'MC_2016_pipipi0_HLT2TIS' : ('DecayTree', os.path.join(datadir, 'mc/DaVinciTuples_MC_Matched.root')),
             'MC_2016_pipipi0' : ('DecayTree', os.path.join(datadir, 'mc/DaVinciTuples_MC_S28_Matched_pipipi0.root')),
             'MiniBias_2015' : ('pions_tuple_sel/DecayTree',) \
                 + tuple(glob.glob(os.path.join(datadir, '../minibias/2015/*/DVTuples*.root'))),
             
             'Data_2016_Kpipi0_MagDown' : ('DecayTree', os.path.join(datadir, 'data/Data_2016_Kpipi0_MagDown.root')),
             }

for mag in 'Up', 'Down' :
    datapaths['Data_2015_Kpipi0_Mag' + mag + '_full'] = \
        {'tree' : 'DstarD0ToHHPi0_Kpipi0_R_LineTuple/DecayTree',
         'files' : sorted(glob.glob(os.path.join(datadir, 'data/2015/mag{0}_full/*Data.root'.format(mag.lower())))),
         'friends' : ('Data_2015_Kpipi0_Mag' + mag + '_full_Weights',)}
    datapaths['Data_2015_Kpipi0_Mag' + mag + '_full_Weights'] = \
        {'tree' : 'BDTTree',
         'files' : sorted(glob.glob(os.path.join(datadir, 'data/2015/mag{0}_full/*Kpipi0_BDT.root'.format(mag.lower()))))}

    datapaths['Data_2015_Kpipi0_Mag' + mag] = ('DecayTree',) + tuple(glob.glob(os.path.join(datadir, 'data/2015/mag' + mag.lower() + '/*.root')))

    mod2016 = __import__('AGammaD0Tohhpi0.Reco16_Charm_Mag{0}_TupleURLs'.format(mag), fromlist = ['urls'])
    datapaths['Data_2016_Kpipi0_Mag' + mag + '_full'] = {'tree' : 'DstarD0ToHHPi0_Kpipi0_R_LineTuple/DecayTree',
                                                         'files' : [url[0] for url in mod2016.urls.values() if url]}
    datapaths['Data_2016_Mag' + mag + '_lumi'] = {'tree' : 'GetIntegratedLuminosity/LumiTuple',
                                                         'files' : datapaths['Data_2016_Kpipi0_Mag' + mag + '_full']['files']}
    datapaths['Data_2016_Kpipi0_Mag' + mag] = {'tree' : 'DecayTree', 
                                               'files' : glob.glob(os.path.join(datadir, 'data', '2016', 'mag' + mag.lower(), '*.root'))}

datalib = DataLibrary(datapaths, variables, varnames = varnames, selection = selection_R)
