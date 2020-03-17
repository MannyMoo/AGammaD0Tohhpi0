'''Formulae for variables from the TTrees. The variable dicts are in the format
needed by makeroodataset.make_roodataset, for converting TTrees to RooDataSets.'''

# Would be better to do it this way so it's not hard-coded, but this avoids importing MINT
# and having to initialise its particle DB.
# import Mint2
# from ROOT import DalitzEventPattern
# pattern_D0Topipipi0 = DalitzEventPattern(421, 211, -211, 111)
# si3Min = pattern_D0Topipipi0.sijMin(1, 3)
# si3Max = pattern_D0Topipipi0.sijMax(1, 3)
si3Min = 75375.93440836841
si3Max = 2975382.8839252326
si3Buffer = 10
_si3Min = si3Min - si3Buffer
_si3Max = si3Max + si3Buffer

def _true_si3(i) :
    '''Get the formula for the true s(i, 3), using the decay descriptor as in the ntuple.'''
    return ' - '.join(['(h{1}_TRUEP_{0}+pi0_TRUEP_{0})^2'.format(c, i) for c in 'EXYZ'])

def true_si3(i) :
    '''Get the formula for the true s(i, 3), using pi+ pi- pi0 as the descriptor.'''
    # Swap the indices for D*- as the decay descriptor is pi- pi+ pi0 instead of pi+ pi- pi0
    return '(h1_ID > 0 ? ({0}) : ({1}))'.format(_true_si3(i), _true_si3(i%2 + 1))

def si3(i) :
    '''Get the formula for s(i, 3), using pi+ pi- pi0 as the descriptor.'''
    return '(h1_ID > 0 ? Dst_S{0}3 : Dst_S{1}3)'.format(i, i%2 + 1)

variables = {'Dst_mass' : {'formula' : 'Dst_M',
                           'xmin' : 2000,
                           'xmax' : 2200,
                           'title' : 'D* mass', 
                           'unit' : 'MeV',
                           },
             'D0_mass' : {'formula' : 'D0_M',
                          'xmin' : 1700,
                          'xmax' : 2010,
                          'title' : 'D^{0} mass',
                          'unit' : 'MeV',
                          },
             'S13' : {'formula' : si3(1),
                      'xmin' : _si3Min,
                      'xmax' : _si3Max,
                      'title' : 'm^{2}(#pi^{+} #pi^{0})',
                      'unit' : 'MeV^{2}'},
             'S23' : {'formula' : si3(2),
                      'xmin' : _si3Min,
                      'xmax' : _si3Max,
                      'title' : 'm^{2}(#pi^{-} #pi^{0})',
                      'unit' : 'MeV^{2}'},
             'true_S13' : {'formula' : true_si3(1),
                           'xmin' : _si3Min,
                           'xmax' : _si3Max,
                           'title' : 'True m^{2}(#pi^{+} #pi^{0})',
                           'unit' : 'MeV^{2}'},
             'true_S23' : {'formula' : true_si3(2),
                           'xmin' : _si3Min,
                           'xmax' : _si3Max,
                           'title' : 'True m^{2}(#pi^{-} #pi^{0})',
                           'unit' : 'MeV^{2}'},
             'decaytime' : {'formula' : 'D_TAU * 1000.',
                            'xmin' : 0.,
                            'xmax' : 6.,
                            'title' : 'Decay time',
                            'unit' : 'ps'},
             'tag' : {'formula' : '(piTag_ID > 0 ? 1 : -1)',
                      'xmin' : -1,
                      'xmax' : 1,
                      'title' : 'Flavour tag',
                      'discrete' : True},
             }

# Deltam variables with various DTF configs.
deltammax = 155.
deltammin = 140.
for suff in '', '_vtx', '_D0Mass', '_vtx_D0Mass':
    if 'vtx' in suff:
        ind = '[0]'
    else:
        ind = ''
    variables['Dst_mass_DTF' + suff] = {'formula' : 'Dst_DTF{0}_M'.format(suff) + ind,
                                        'xmin' : 2000,
                                        'xmax' : 2200,
                                        'title' : 'D* mass', 
                                        'unit' : 'MeV'}
    variables['D0_mass_DTF' + suff] = {'formula' : 'Dst_DTF{0}_D0_M'.format(suff) + ind,
                                       'xmin' : 1700,
                                       'xmax' : 2010,
                                       'title' : 'D^{0} mass',
                                       'unit' : 'MeV'}
    variables['deltam_DTF' + suff] = {'formula' : 'Dst_mass_DTF{0} - D0_mass_DTF{0}'.format(suff),
                                      'xmin' : deltammin,
                                      'xmax' : deltammax,
                                      'title' : '#Deltam',
                                      'unit' : 'MeV'}
variables['deltam'] = variables['deltam_DTF_vtx_D0Mass']
