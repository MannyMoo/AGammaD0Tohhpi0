'''Selections in TTree format.'''

from AnalysisUtils.selection import AND, OR

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
