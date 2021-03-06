'''Functions to access all the relevant datasets for the analysis, both TTrees and RooDataSets.'''

import os, ROOT, pprint, glob, datetime
from AnalysisUtils.data import DataLibrary, BinnedFitData
from AGammaD0Tohhpi0.variables import variables
from AGammaD0Tohhpi0.selection import selections, masswindows, bdtsel
from AGammaD0Tohhpi0.workspace import workspace

datadir = os.environ.get('AGAMMAD0TOHHPI0DATADIR', 
                         '/nfs/lhcb/d2hh01/hhpi0/data/')
datasetsdir = os.path.join(datadir, 'Datasets')

workingdir = os.path.abspath(os.path.join(datadir, '..', 'workingdir'))
mintdatadir = os.path.join(datadir, 'mint')

filtereddatadir = os.path.join(datadir, 'data', 'filtered')
pythondir = os.path.expandvars('$AGAMMAD0TOHHPI0ROOT/python/AGammaD0Tohhpi0')
pydatasetsdir = os.path.join(pythondir, 'Datasets')

varnames = ('deltam', 'D0_mass')

oldaliases_R = {'lab0' : 'Dst',
                'lab1' : 'D0',
                'lab2' : 'Kst',
                'lab3' : 'h1',
                'lab4' : 'h2',
                'lab5' : 'pi0',
                'lab6' : 'gamma1',
                'lab7' : 'gamma2',
                'lab8' : 'piTag'}
oldaliases_M = dict(oldaliases_R)
oldaliases_M['lab6'] = oldaliases_M['lab8']
del oldaliases_M['lab7']
del oldaliases_M['lab8']
              

# All the TTree datasets, the tree names and file names (any number of file names can be given).
datapaths = {'MiniBias_2015' : {'tree' : 'pions_tuple_sel/DecayTree',
                                'files' : glob.glob(os.path.join(datadir, 'minibias/2015/DVTuples*.root'))},
             }

trees = {'pipipi0_Resolved' : 'DstarD0ToHHPi0_pipipi0_R_LineTuple/DecayTree',
         'pipipi0_Merged' : 'DstarD0ToHHPi0_pipipi0_M_LineTuple/DecayTree',
         'Kpipi0_Resolved' : 'DstarD0ToHHPi0_Kpipi0_R_LineTuple/DecayTree',
         'Kpipi0_Merged' : 'DstarD0ToHHPi0_Kpipi0_M_LineTuple/DecayTree'}
wgprodtrees = {'pipipi0_Resolved' : 'Dstr2DPiPiPi0R/DecayTree',
               'pipipi0_Merged' : 'Dstr2DPiPiPi0M/DecayTree',
               'Kpipi0_Resolved' : 'Dstr2DKPiPi0R/DecayTree',
               'Kpipi0_Merged' : 'Dstr2DKPiPi0M/DecayTree'}
mctrees = {'pipipi0_Unbiased' : 'DstTo_D0Toh1h2pi0_piTag_MCUnbiasedTuple_pipi/DecayTree',
           'Kpipi0_Unbiased' : 'DstTo_D0Toh1h2pi0_piTag_MCUnbiasedTuple_Kpi/DecayTree',
           'pipipi0_Generator' : 'DstTo_D0Toh1h2pi0_piTag_MCDecayTreeTuple_pipi/MCDecayTree',
           'Kpipi0_Generator' : 'DstTo_D0Toh1h2pi0_piTag_MCDecayTreeTuple_Kpi/MCDecayTree'}

wgprodaliases = {'Dstr' : 'Dst',
                 'Kstr' : 'Kst',
                 'H1' : 'h1',
                 'H2' : 'h2',
                 'piSoft' : 'piTag',
                 'D_' : 'D0_',
                 'Dstr_FIT' : 'Dst_DTF_vtx_D0Mass',
                 'Dstr_FIT_M' : 'Dst_DTF_vtx_D0Mass_M',
                 'Dstr_FIT_DM' : 'Dst_DTF_vtx_D0Mass_D0_M',
                 'pi0' : 'Pi0'
}

for fname in glob.glob(os.path.join(pydatasetsdir, '*URLs.py')):
    modname = os.path.split(fname)[1][:-3]
    mod = __import__('AGammaD0Tohhpi0.Datasets.' + modname, fromlist = ['urls'])
    files = [mod.urls[lfn][0] for lfn in mod.urls]
    dataname = modname[:-5]
    if 'MC' in dataname:
        _trees = trees
        aliases = {}
    else:
        _trees = wgprodtrees
        aliases = wgprodaliases
    for name, tree in _trees.items():
        datapaths[dataname + '_' + name] = {'tree' : tree, 'files' : files,
                                            'datasetdir' : datasetsdir,
                                            'aliases' : aliases}
    if not 'MC' in dataname:
        datapaths[dataname + '_Lumi'] = {'tree' : 'GetIntegratedLuminosity/LumiTuple',
                                         'files' : files, 'datasetdir' : datasetsdir}
        continue
    for name, tree in mctrees.items():
        datapaths[dataname + '_' + name] = {'tree' : tree, 'files' : files, 'datasetdir' : datasetsdir}

# for mag in 'Up', 'Down' :
#     datapaths['MC_2016_Unbiased_pipipi0_Dalitz_Mag' + mag] = \
#         {'tree' : 'Dstar_2010_plusTo_D0Topiminuspipluspi0_piplus_MCUnbiasedTuple/DecayTree',
#          'files' : glob.glob(os.path.join(datadir, 'mc', '2016', 'pipipi0_Dalitz_Mag' + mag, '*.root'))}
#     datapaths['MC_2016_S28_Resloved_pipipi0_Dalitz_Mag' + mag] = \
#         {'tree' : 'DstarD0ToHHPi0_pipipi0_R_LineTuple/DecayTree',
#          'files' : datapaths['MC_2016_Unbiased_pipipi0_Dalitz_Mag' + mag]['files']}
#     datapaths['MC_2016_S28_Merged_pipipi0_Dalitz_Mag' + mag] = \
#         {'tree' : 'DstarD0ToHHPi0_pipipi0_M_LineTuple/DecayTree',
#          'files' : datapaths['MC_2016_Unbiased_pipipi0_Dalitz_Mag' + mag]['files']}
#     datapaths['MC_2016_Generator_pipipi0_Dalitz_Mag' + mag] = \
#         {'tree' : 'Dstar_2010_plusTo_D0Topiminuspipluspi0_piplus_MCDecayTreeTuple/MCDecayTree',
#          'files' : datapaths['MC_2016_Unbiased_pipipi0_Dalitz_Mag' + mag]['files']}

for mag in 'Up', 'Down' :
    # 2015
    files2015 = sorted(glob.glob(os.path.join(datadir, 'data/2015/mag{0}_full/*Data.root'.format(mag.lower()))))
    # Kpipi0
    datapaths['Data_2015_Kpipi0_Resolved_Mag' + mag + '_full'] = \
        {'tree' : 'DstarD0ToHHPi0_Kpipi0_R_LineTuple/DecayTree',
         'files' : files2015,
         'friends' : ('Data_2015_Kpipi0_Resolved_Mag' + mag + '_full_Weights',),
         'aliases' : oldaliases_R}
    datapaths['Data_2015_Kpipi0_Resolved_Mag' + mag + '_full_Weights'] = \
        {'tree' : 'BDTTree',
         'files' : sorted(glob.glob(os.path.join(datadir, 'data/2015/mag{0}_full/*Kpipi0_BDT.root'.format(mag.lower()))))}
    datapaths['Data_2015_Kpipi0_Resolved_Mag' + mag] = {'tree' : 'DecayTree',
                                                        'files' : glob.glob(os.path.join(datadir, 'data/2015/mag' + mag.lower() + '/*.root')),
                                                        'aliases' : oldaliases_R}
    datapaths['Data_2015_Kpipi0_Merged_Mag' + mag + '_full'] = \
        {'tree' : 'DstarD0ToHHPi0_Kpipi0_M_LineTuple/DecayTree',
         'files' : files2015,
         'aliases' : oldaliases_M}

    # pipipi0
    datapaths['Data_2015_pipipi0_Resolved_Mag' + mag + '_full'] = \
        {'tree' : 'DstarD0ToHHPi0_pipipi0_R_LineTuple/DecayTree',
         'files' : files2015,
        'aliases' : oldaliases_R}
    datapaths['Data_2015_pipipi0_Merged_Mag' + mag + '_full'] = \
        {'tree' : 'DstarD0ToHHPi0_pipipi0_M_LineTuple/DecayTree',
         'files' : files2015,
         'aliases' : oldaliases_M}


    # # 2016
    # mod2016 = __import__('AGammaD0Tohhpi0.Reco16_Charm_Mag{0}_TupleURLs'.format(mag), fromlist = ['urls'])
    # # Kpipi0
    # urls2016 = [url[0] for url in mod2016.urls.values() if url]
    # datapaths['Data_2016_Kpipi0_Resolved_Mag' + mag + '_full'] = {'tree' : 'DstarD0ToHHPi0_Kpipi0_R_LineTuple/DecayTree',
    #                                                               'files' : urls2016}
    # datapaths['Data_2016_Kpipi0_Merged_Mag' + mag + '_full'] = {'tree' : 'DstarD0ToHHPi0_Kpipi0_M_LineTuple/DecayTree',
    #                                                             'files' : urls2016}
    # datapaths['Data_2016_Mag' + mag + '_lumi'] = {'tree' : 'GetIntegratedLuminosity/LumiTuple',
    #                                               'files' : urls2016}
    # datapaths['Data_2016_Kpipi0_Resolved_Mag' + mag] = {'tree' : 'DecayTree', 
    #                                                     'files' : glob.glob(os.path.join(datadir, 'data', '2016', 'mag' + mag.lower(), '*.root'))}

    # # pipipi0
    # datapaths['Data_2016_pipipi0_Resolved_Mag' + mag + '_full'] = {'tree' : 'DstarD0ToHHPi0_pipipi0_R_LineTuple/DecayTree',
    #                                                                'files' : urls2016}
    # datapaths['Data_2016_pipipi0_Merged_Mag' + mag + '_full'] = {'tree' : 'DstarD0ToHHPi0_pipipi0_M_LineTuple/DecayTree',
    #                                                              'files' : urls2016}

# Filtered data.
for dataset in os.listdir(filtereddatadir) :
    files = sorted(glob.glob(os.path.join(filtereddatadir, dataset, '*.root')))
    files = filter(lambda f : 'Dataset' not in f, files)
    datapaths[dataset] = {'files' : files,
                          'tree' : 'DecayTree'}
    if dataset.endswith('WrongPi'):
        datapaths[dataset]['variables'] = {'deltam' : dict(variables['deltam'], formula = 'deltam')}
        datapaths[dataset]['tree'] = 'wrongmasstree'
    elif dataset.startswith('RealData'):
        datapaths[dataset]['aliases'] = wgprodaliases
    # Aliases for old datasets.
    elif '2015' in dataset:
        if 'Resolved' in dataset:
            datapaths[dataset]['aliases'] = oldaliases_R
        else:
            datapaths[dataset]['aliases'] = oldaliases_M
    if dataset.endswith('TriggerFiltered'):
        datapaths[dataset]['selection'] = 'Dstr_FIT_CHI2 < 30 && Dstr_FIT_CHI2 > 0'

datapaths['MC_pipipi0_DecProdCut_Dalitz_2016_MagBoth_Resolved_TruthMatched']['aliases'] = oldaliases_R
datapaths['MC_pipipi0_DecProdCut_Dalitz_2016_MagBoth_Resolved_TruthMatched']['selection'] = bdtsel
datapaths['MC_2016_pipipi0'] = datapaths['MC_pipipi0_DecProdCut_Dalitz_2016_MagBoth_Resolved_TruthMatched']
             
# MINT data.
mintvariables = {}
for name in os.listdir(mintdatadir) :
    datapaths['MINT_' + name] = {'tree' : 'DalitzEventList',
                                 'files' : glob.glob(os.path.join(mintdatadir, name, '*pi0*.root')),
                                 'variables' : mintvariables}

class AGammaDataLibrary(DataLibrary):
    '''Add some analysis specific functions to DataLibrary.'''

    def get_deltam_in_mass_bins_dataset(self, dataset,
                                        massbins = [masswindows['R'][0], 1865-15, 1865+15, masswindows['R'][1]],
                                        update = False, nbinsDeltam = 100, name = None, regex = False,
                                        updatedataset = False, suffix = '', selection = ''):
        '''Get deltam RooDataHists in bins of D0_mass, in the form of a BinnedFitData instance for the given
        dataset. Several datasets can be combined then binned by passing a list of names as 'dataset',
        or by making it a regex and using regex = True.'''

        if regex:
            dataset = self.get_matching_datasets(dataset)

        now = datetime.datetime.today()
        if isinstance(dataset, (tuple,list)):
            roodata = self.get_merged_dataset(*dataset, update = updatedataset, 
                                              suffix = suffix, selection = selection)
            outputdir = self.dataset_dir(dataset[0])
            dataset = '_'.join(dataset)
            update = update or any(datalib.get_dataset_update_time(ds, suffix) >= now for ds in dataset)
        else:
            roodata = self.get_dataset(dataset, update = updatedataset, suffix = suffix, selection = selection)
            outputdir = self.dataset_dir(dataset)
            update = update or datalib.get_dataset_update_time(dataset, suffix) >= now
        if not name:
            name = dataset + suffix + '_DeltamInMassBinsDatasets'
        variable = workspace.roovar('deltam')
        binvariable = workspace.roovar('D0_mass')
        return BinnedFitData(name, outputdir, workspace, roodata, variable, binvariable, massbins,
                             nbinsx = nbinsDeltam, get = True, update = update)

    def add_magboth_datasets(self):
        '''Add merged datasets of MagUp and MagDown.'''
        self.add_merged_datasets('MagBoth', 'MagUp', 'MagDown')       

datalib = AGammaDataLibrary(datapaths, variables, varnames = varnames, ignorecompilefails = True)
