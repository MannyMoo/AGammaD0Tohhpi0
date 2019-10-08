'''Functions to access all the relevant datasets for the analysis, both TTrees and RooDataSets.'''

import os, ROOT, pprint, glob
from AnalysisUtils.data import DataLibrary
from AGammaD0Tohhpi0.variables import variables
from AGammaD0Tohhpi0.selection import selection_R

datadir = os.environ.get('AGAMMAD0TOHHPI0DATADIR', 
                         '/nfs/lhcb/d2hh01/hhpi0/data/')
workingdir = os.path.abspath(os.path.join(datadir, '..', 'workingdir'))
mintdatadir = os.path.join(datadir, 'mint')

filtereddatadir = os.path.join(datadir, 'data', 'filtered')

varnames = ('deltam', 'D0_mass')

# All the TTree datasets, the tree names and file names (any number of file names can be given).
datapaths = {'MC_2016_pipipi0' : {'tree' : 'DecayTree', 
                                  'files' : [os.path.join(datadir, 'mc/2016/DaVinciTuples_MC_S28_Matched_pipipi0.root')]},
             'MiniBias_2015' : {'tree' : 'pions_tuple_sel/DecayTree',
                                'files' : glob.glob(os.path.join(datadir, 'minibias/2015/DVTuples*.root'))},
             }
for mag in 'Up', 'Down' :
    datapaths['MC_2016_Unbiased_pipipi0_Dalitz_Mag' + mag] = \
        {'tree' : 'Dstar_2010_plusTo_D0Topiminuspipluspi0_piplus_MCUnbiasedTuple/DecayTree',
         'files' : glob.glob(os.path.join(datadir, 'mc', '2016', 'pipipi0_Dalitz_Mag' + mag, '*.root'))}
    datapaths['MC_2016_S28_Resloved_pipipi0_Dalitz_Mag' + mag] = \
        {'tree' : 'DstarD0ToHHPi0_pipipi0_R_LineTuple/DecayTree',
         'files' : datapaths['MC_2016_Unbiased_pipipi0_Dalitz_Mag' + mag]['files']}
    datapaths['MC_2016_S28_Merged_pipipi0_Dalitz_Mag' + mag] = \
        {'tree' : 'DstarD0ToHHPi0_pipipi0_M_LineTuple/DecayTree',
         'files' : datapaths['MC_2016_Unbiased_pipipi0_Dalitz_Mag' + mag]['files']}
    datapaths['MC_2016_Generator_pipipi0_Dalitz_Mag' + mag] = \
        {'tree' : 'Dstar_2010_plusTo_D0Topiminuspipluspi0_piplus_MCDecayTreeTuple/MCDecayTree',
         'files' : datapaths['MC_2016_Unbiased_pipipi0_Dalitz_Mag' + mag]['files']}

for mag in 'Up', 'Down' :
    # 2015
    files2015 = sorted(glob.glob(os.path.join(datadir, 'data/2015/mag{0}_full/*Data.root'.format(mag.lower()))))
    # Kpipi0
    datapaths['Data_2015_Kpipi0_Resolved_Mag' + mag + '_full'] = \
        {'tree' : 'DstarD0ToHHPi0_Kpipi0_R_LineTuple/DecayTree',
         'files' : files2015,
         'friends' : ('Data_2015_Kpipi0_Resolved_Mag' + mag + '_full_Weights',)}
    datapaths['Data_2015_Kpipi0_Resolved_Mag' + mag + '_full_Weights'] = \
        {'tree' : 'BDTTree',
         'files' : sorted(glob.glob(os.path.join(datadir, 'data/2015/mag{0}_full/*Kpipi0_BDT.root'.format(mag.lower()))))}
    datapaths['Data_2015_Kpipi0_Resolved_Mag' + mag] = {'tree' : 'DecayTree',
                                                        'files' : glob.glob(os.path.join(datadir, 'data/2015/mag' + mag.lower() + '/*.root'))}
    datapaths['Data_2015_Kpipi0_Merged_Mag' + mag + '_full'] = \
        {'tree' : 'DstarD0ToHHPi0_Kpipi0_M_LineTuple/DecayTree',
         'files' : files2015}

    # pipipi0
    datapaths['Data_2015_pipipi0_Resolved_Mag' + mag + '_full'] = \
        {'tree' : 'DstarD0ToHHPi0_pipipi0_R_LineTuple/DecayTree',
         'files' : files2015}
    datapaths['Data_2015_pipipi0_Merged_Mag' + mag + '_full'] = \
        {'tree' : 'DstarD0ToHHPi0_pipipi0_M_LineTuple/DecayTree',
         'files' : files2015}


    # 2016
    mod2016 = __import__('AGammaD0Tohhpi0.Reco16_Charm_Mag{0}_TupleURLs'.format(mag), fromlist = ['urls'])
    # Kpipi0
    urls2016 = [url[0] for url in mod2016.urls.values() if url]
    datapaths['Data_2016_Kpipi0_Resolved_Mag' + mag + '_full'] = {'tree' : 'DstarD0ToHHPi0_Kpipi0_R_LineTuple/DecayTree',
                                                                  'files' : urls2016}
    datapaths['Data_2016_Kpipi0_Merged_Mag' + mag + '_full'] = {'tree' : 'DstarD0ToHHPi0_Kpipi0_M_LineTuple/DecayTree',
                                                                'files' : urls2016}
    datapaths['Data_2016_Mag' + mag + '_lumi'] = {'tree' : 'GetIntegratedLuminosity/LumiTuple',
                                                  'files' : urls2016}
    datapaths['Data_2016_Kpipi0_Resolved_Mag' + mag] = {'tree' : 'DecayTree', 
                                                        'files' : glob.glob(os.path.join(datadir, 'data', '2016', 'mag' + mag.lower(), '*.root'))}

    # pipipi0
    datapaths['Data_2016_pipipi0_Resolved_Mag' + mag + '_full'] = {'tree' : 'DstarD0ToHHPi0_pipipi0_R_LineTuple/DecayTree',
                                                                   'files' : urls2016}
    datapaths['Data_2016_pipipi0_Merged_Mag' + mag + '_full'] = {'tree' : 'DstarD0ToHHPi0_pipipi0_M_LineTuple/DecayTree',
                                                                 'files' : urls2016}

# Filtered data.
for dataset in os.listdir(filtereddatadir) :
    files = glob.glob(os.path.join(filtereddatadir, dataset, '*.root'))
    files = filter(lambda f : not f.endswith('_Dataset.root'), files)
    datapaths[dataset] = {'files' : files,
                          'tree' : 'DecayTree'}
    if dataset.endswith('WrongPi'):
        datapaths[dataset]['variables'] = {'deltam' : dict(variables['deltam'], formula = 'deltam')}
        datapaths[dataset]['tree'] = 'wrongmasstree'

# MINT data.
for name in os.listdir(mintdatadir) :
    datapaths['MINT_' + name] = {'tree' : 'DalitzEventList',
                                 'files' : glob.glob(os.path.join(mintdatadir, name, 'pipipi0*.root'))}

datalib = DataLibrary(datapaths, variables, varnames = varnames, selection = selection_R, ignorecompilefails = True)
datalib.add_merged_datasets('MagBoth', 'MagUp', 'MagDown')
