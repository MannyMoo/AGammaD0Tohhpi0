from AnalysisUtils.combinatorics import wrong_event_masses, total_mass
import os
from AGammaD0Tohhpi0.variables import variables
from AGammaD0Tohhpi0.data import filtereddatadir

def deltam(pvecs):
    tot = total_mass(pvecs)
    dmass = pvecs['lab1'].M()
    return tot - dmass

def gen_background(datalib, dataset, nbins = 100):
    '''Generate background by combining D0 candidates with pi+ candidates from the next event.'''

    tree = datalib.get_data(dataset)
    outputdir = os.path.join(filtereddatadir, dataset + '_WrongPi')
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    outputfile = os.path.join(outputdir, dataset + '_WrongPi.root')
    
    parts = ('lab1',)
    if 'Resolved' in dataset:
        parts += ('lab8',)
    else:
        parts += ('lab6',)

    return wrong_event_masses(tree, outputfile, nbins, variables['Dst_mass'], parts,
                              combinations = {'deltam' : {'function' : deltam,
                                                          'xmin' : variables['deltam']['xmin'],
                                                          'xmax' : variables['deltam']['xmax']}},
                              requireall = False, 
                              targetstats = tree.GetEntries(),
                              selection = 'deltam > 150',
                              )
