'''Selections in TTree format.'''

from AnalysisUtils.selection import AND, OR
import os
from AnalysisUtils.addmva import make_mva_tree

MC_sel_R = ' && '.join(['lab{0}_ID == lab{0}_TRUEID'.format(i) for i in (0, 1, 3, 4, 5, 6, 7, 8)])
MC_sel_M = ' && '.join(['lab{0}_ID == lab{0}_TRUEID'.format(i) for i in (0, 1, 3, 4, 5, 6)])

MC_sel_pipi_R = AND(MC_sel_R, 'lab0_MCMatch_pipi')
MC_sel_KK_R = AND(MC_sel_R, 'lab0_MCMatch_KK')
MC_sel_Kpi_R = AND(MC_sel_R, 'lab0_MCMatch_Kpi')

MC_sel_pipi_M = AND(MC_sel_M, 'lab0_MCMatch_pipi')
MC_sel_KK_M = AND(MC_sel_M, 'lab0_MCMatch_KK')
MC_sel_Kpi_M = AND(MC_sel_M, 'lab0_MCMatch_Kpi')

masswindow_R = (1825, 1905)
masswindow_R_sel = '{0} < D0_mass && D0_mass < {1}'.format(*masswindow_R)

bdtcut = -0.1
bdtsel = 'BDT >= ' + str(bdtcut)

selection_R = AND(masswindow_R_sel, bdtsel)

kin_allowed_sel = 'S13 != {0!r} && S23 != {0!r}'.format(-3.4028234663852886e+38)

# Should add L0 selection (if we actually need them?).
triggersel = OR('lab0_Hlt2CharmHadDstp2D0Pip_D02{finalstate}Pi0_Pi0MDecision_TOS',
                'lab0_Hlt2CharmHadDstp2D0Pip_D02{finalstate}Pi0_Pi0RDecision_TOS',
                'lab0_Hlt2CharmHadInclDst2PiD02HHXBDTDecision_TOS')
triggersel_pipi = triggersel.format(finalstate = 'PimPip')
triggersel_kpi = triggersel.format(finalstate = 'KmPip')

bdt_kin_file = os.path.expandvars('$AGAMMAD0TOHHPI0ROOT/tmva/20180702-Lewis/TMVAClassification_BDT_kinematic.weights.xml')

def add_bdt_kinematic(datalib, dataset) :
    '''Add the kinematic BDT to the given dataset.'''
    tree = datalib.get_data(dataset)
    bdttreename = 'BDT_kin'
    friendfilename = datalib.friend_file_name(dataset, dataset + '_' + bdttreename, bdttreename, makedir = True)
    make_mva_tree(tree, bdt_kin_file, 'BDT', bdttreename, friendfilename)
