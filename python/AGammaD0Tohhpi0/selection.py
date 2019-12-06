'''Selections in TTree format.'''

from AnalysisUtils.selection import AND, OR
import os, ROOT
from AnalysisUtils.addmva import make_mva_tree
from AnalysisUtils.treeutils import copy_tree

triggerform = ''

parts_R = ['Dst', 'D0', 'h1', 'h2', 'pi0', 'gamma1', 'gamma2', 'piTag']
parts_M = ['Dst', 'D0', 'h1', 'h2', 'pi0', 'piTag']
MC_sel_R = ' && '.join(['{0}_ID == {0}_TRUEID'.format(i) for i in parts_R])
MC_sel_M = ' && '.join(['{0}_ID == {0}_TRUEID'.format(i) for i in parts_M])

MC_sels = {}
for MR, sel in ('M', MC_sel_M), ('R', MC_sel_R):
    for name in 'pipipi0', 'Kpipi0', 'KKpi0':
        MC_sels[name + '_' + MR] = AND(sel, 'Dst_MCMatch_' + name[:-3])

masswindows = {'R' : (1825, 1905),
               'M' : (1800, 1930)}
sidebandwidth = 50
masswindowsels = {}
for MR, (low, high) in masswindows.items():
    masswindowsels[MR] = '{0} < D0_mass && D0_mass < {1}'.format(low, high)
    masswindowsels[MR + '_LowMass'] = '{0} < D0_mass && D0_mass < {1}'.format(low-sidebandwidth, low)
    masswindowsels[MR + '_HighMass'] = '{0} < D0_mass && D0_mass < {1}'.format(high, high+sidebandwidth)

# Should add L0 selection (if we actually need them?).
hlt1sel = OR('D0_Hlt1TrackMVADecision_TOS', 'D0_Hlt1TwoTrackMVADecision_TOS')
hlt2sel = OR('Dst_Hlt2CharmHadDstp2D0Pip_D02{finalstate}Pi0_Pi0{MR}Decision_TOS',
             'Dst_Hlt2CharmHadInclDst2PiD02HHXBDTDecision_TOS')
finalstates = {'pipipi0' : 'PimPip',
               'Kpipi0' : 'KmPip'}
hlt2sels = {}
for name, finalstate in finalstates.items():
    for MR in 'MR':
        hlt2sels[name + '_' + MR] = hlt2sel.format(**locals())

bdtcut = -0.1
bdtsel = 'BDT >= ' + str(bdtcut)

selections = {}
for MR in 'MR':
    for finalstate in finalstates:
        for masssel in '', '_LowMass', '_HighMass':
            selections[finalstate + '_' + MR + masssel] = AND(hlt1sel, hlt2sels[name + '_' + MR],
                                                             masswindowsels[MR + masssel])

kin_allowed_sel = 'S13 != {0!r} && S23 != {0!r}'.format(-3.4028234663852886e+38)

bdt_kin_file = os.path.expandvars('$AGAMMAD0TOHHPI0ROOT/tmva/20180702-Lewis/TMVAClassification_BDT_kinematic.weights.xml')

def add_bdt_kinematic(datalib, dataset) :
    '''Add the kinematic BDT to the given dataset.'''
    tree = datalib.get_data(dataset)
    bdttreename = 'BDT_kin'
    friendfilename = datalib.friend_file_name(dataset, dataset + '_' + bdttreename, bdttreename, makedir = True)
    make_mva_tree(tree, bdt_kin_file, 'BDT', bdttreename, friendfilename)

def trigger_filter(filtereddatadir, datalib, dataset, massrange = '', nthreads = 16):
    '''Filter the given dataset with the relevant HLT1, HLT2, and mass range requirements.'''
    if massrange and not massrange.startswith('_'):
        massrange = '_' + massrange
    outputname = dataset + massrange + '_TriggerFiltered' 
    outputdir = os.path.join(filtereddatadir, outputname)
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    if '_pipipi0' in dataset:
        finalstate = 'pipipi0'
    else:
        finalstate = 'Kpipi0'
    if 'Resolved' in dataset:
        MR = 'R'
    else:
        MR = 'M'
    sel = selections[finalstate + '_' + MR + massrange]
    if 'MC' in dataset:
        sel = AND(sel, MC_sels[finalstate + '_' + MR])
    print 'Copy dataset', dataset, 'with selection', repr(sel), 'to', outputdir
    success = datalib.filter_data(dataset + massrange, sel, outputname, filtereddatadir, nthreads = nthreads)
    print 'Success?', success
    return success
