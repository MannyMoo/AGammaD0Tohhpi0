import sys
sys.path.insert(0, '/cvmfs/lhcb.cern.ch/lib/lhcb/STRIPPING/STRIPPING_v11r5p1/Phys/StrippingSelections/tests/users/')
from StrippingTuple import stripping_tuple_sequence_from_doc
from Configurables import TupleToolTISTOS, LoKi__Hybrid__TupleTool, DaVinci, TupleToolDecayTreeFitter, \
    TupleToolPropertime, TupleToolANNPID
from StrippingDoc import StrippingDoc
from Configurables import TupleToolMCTruth, MCTupleToolPrompt
from AnalysisUtils.Selections.mcselections import make_mc_unbiased_seq
from AnalysisUtils.ntupling import make_mc_tuple, make_tuple
from AnalysisUtils.DecayDescriptors.DecayDescriptors import parse_decay_descriptor

def get_line_docs() :
    '''Get the doc for the relevant stripping lines.'''
    doc = StrippingDoc('stripping28')
    return doc.filter_lines(lambda line : (line.name.startswith('DstarD0ToHHPi0') 
                                           and not 'KK' in line.name 
                                           and not 'WIDEMASS' in line.name))

def add_tuples() :
    '''Make ntuples for the D0->hhpi0 stripping lines. Assumes the data settings have already
    been configured in DaVinci.'''

    # Normal data
    stream = 'Charm.mdst'
    # For restripping
    if DaVinci().getProp('ProductionType') == 'Stripping' :
        stream = 'CharmCompleteEvent.dst'
    # For MC.
    elif DaVinci().getProp('Simulation') :
        stream = 'AllStreams.dst'

    tuples = []
    seqs = []
    for line in get_line_docs() :
        seq = stripping_tuple_sequence_from_doc(line, stream = stream)
        seqs.append(seq)
        tuples.append(seq.Members[-1])
        add_tools(seq.Members[-1])
        DaVinci().UserAlgorithms += [seq]
    DaVinci(**line.davinci_config(stream))

    if stream.endswith('.dst') :
        for dtt in tuples :
            dtt.Inputs[0] = stream.split('.')[0] + '/' + dtt.Inputs[0]

    DaVinci().TupleFile = 'DaVinciTuples.root'
    if DaVinci().getProp('Simulation') :
        for dtt in tuples :
            add_mc_tools(dtt)
    else :
        DaVinci().Lumi = True

    return tuples

def add_tools(dtt) :
    '''Add tools to the DecayTreeTuple.'''
    tttistos = TupleToolTISTOS(dtt.name() + '_tttistos',
                           VerboseHlt2 = True,
                           VerboseHlt1 = True)
    tttistos.TriggerList = [line + 'Decision' for line in ['Hlt2CharmHadInclDst2PiD02HHXBDT',
                                                           'Hlt2CharmHadDstp2D0Pip_D02KmKpPi0_Pi0M',
                                                           'Hlt2CharmHadDstp2D0Pip_D02KmKpPi0_Pi0R',
                                                           'Hlt2CharmHadDstp2D0Pip_D02KmPipPi0_Pi0M',
                                                           'Hlt2CharmHadDstp2D0Pip_D02KmPipPi0_Pi0R',
                                                           'Hlt2CharmHadDstp2D0Pip_D02KpPimPi0_Pi0M',
                                                           'Hlt2CharmHadDstp2D0Pip_D02KpPimPi0_Pi0R',
                                                           'Hlt2CharmHadDstp2D0Pip_D02PimPipPi0_Pi0M',
                                                           'Hlt2CharmHadDstp2D0Pip_D02PimPipPi0_Pi0R',
                                                           'Hlt1TrackMVA',
                                                           'Hlt1TwoTrackMVA',
                                                           'Hlt1TrackMVATight',
                                                           'Hlt1TwoTrackMVATight',
                                                           'Hlt1TrackMuon',
                                                           'Hlt1TrackMuonMVA',
                                                           'Hlt1CalibTrackingKK',
                                                           'Hlt1CalibTrackingKPi',
                                                           'Hlt1CalibTrackingKPiDetached',
                                                           'Hlt1CalibTrackingPiPi',]]

    tttime = TupleToolPropertime(dtt.name() + '_tttime')
    tttime.FitToPV = True

    ttpid = TupleToolANNPID(dtt.name() + '_ttpid')
    ttpid.ANNPIDTunes = ['MC15TuneV1']

    if '_R_' in dtt.name() :
        dtt.Decay = dtt.Decay.replace('pi0', '( pi0 -> ^gamma ^gamma )')
    dtt.addBranches({'lab0' : dtt.Decay.replace('^', '')})
    dtt.lab0.addTupleTool(tttistos)
    dtt.addTupleTool(tttime)
    # Still need TupleToolPid for the _ID branches.
    dtt.ToolList.remove('TupleToolANNPID')
    dtt.addTupleTool(ttpid)
    dtt.ToolList += ['TupleToolPrimaries',
                     'TupleToolTrackInfo']
    for name, attrs in {'DTF' : {'constrainToOriginVertex' : False,
                                 'daughtersToConstrain' : ['pi0']},
                        'DTF_vtx' : {'constrainToOriginVertex' : True,
                                     'daughtersToConstrain' : ['pi0']},
                        'DTF_vtx_D0Mass' : {'constrainToOriginVertex' : True,
                                            'daughtersToConstrain' : ['pi0', 'D0']},
                        'DTF_D0Mass' : {'constrainToOriginVertex' : False,
                                        'daughtersToConstrain' : ['pi0', 'D0']}}.items() :
        ttdtf = TupleToolDecayTreeFitter(name, **attrs)
        ttdtf.Verbose = True
        dtt.lab0.addTupleTool(ttdtf)

    hybrid = dtt.lab0.addTupleTool('LoKi__Hybrid__TupleTool')
    if 'K*' in dtt.Decay :
        for i in 1, 2 :
            form = ' - '.join(['(CHILD(E, 1, 1, {0}) + CHILD(E, 1, 2))**2'.format(i)]
                              + ['(CHILD(P{1}, 1, 1, {0}) + CHILD(P{1}, 1, 2))**2'.format(i, p) for p in 'XYZ'])
            form = 'DTF_FUN({0}, False, "D0", "pi0", -1., LoKi.Constants.NegativeInfinity)'.format(form)
            hybrid.Variables['S{0}3'.format(i)] = form
    else :
        for i in 1, 2 :
            form = ' - '.join(['(CHILD(E, 1, {0}) + CHILD(E, 1, 3))**2'.format(i)]
                              + ['(CHILD(P{1}, 1, {0}) + CHILD(P{1}, 1, 3))**2'.format(i, p) for p in 'XYZ'])
            form = 'DTF_FUN({0}, False, "D0", "pi0", -1., LoKi.Constants.NegativeInfinity)'.format(form)
            hybrid.Variables['S{0}3'.format(i)] = form

def mc_descriptors() :
    '''Get the MC decay descriptors.'''
    descs = []
    for minus, plus in ('pi', 'pi'), ('K', 'K'), ('K', 'pi') :
        desc = parse_decay_descriptor('[ D*(2010)+ ==> ( D0 ==> {minus}-  {plus}+  pi0 )  pi+ ]CC'.format(minus = minus, plus = plus))
        descs.append(desc)
    return descs

def add_mc_tools(dtt) :
    '''Add MC tools to a DecayTreeTuple.'''
    
    ttmcmatch = LoKi__Hybrid__TupleTool(dtt.name() + '_ttmcmatch')
    ttmcmatch.Preambulo = ['from LoKiPhysMC.decorators import *', 'from LoKiPhysMC.functions import mcMatch']
    for minus, plus in ('pi', 'pi'), ('K', 'K'), ('K', 'pi') :
        ttmcmatch.Variables['MCMatch_' + minus + plus] = \
            'switch(mcMatch("[ D*(2010)+ ==> ( D0 ==> {minus}-  {plus}+  pi0 )  pi+ ]CC"), 1, 0)'.format(minus = minus, plus = plus)
    ttmctruth = TupleToolMCTruth(dtt.name() + '_ttmctruth')
    ttmctruth.addTupleTool(MCTupleToolPrompt(dtt.name() + '_ttmcprompt'))
    dtt.lab0.addTupleTool(ttmcmatch)
    dtt.addTupleTool(ttmctruth)
    dtt.ToolList.append('TupleToolMCBackgroundInfo')

def add_mc_tuples(desc = None) :
    '''Add MC tuples for the given DecayDescriptor.'''
    if not desc :
        for desc in mc_descriptors() :
            add_mc_tuples(desc)
        return

    mctuple = make_mc_tuple(desc, ToolList = ['MCTupleToolKinematic', 'TupleToolEventInfo',
                                              'MCTupleToolPrompt', 'MCTupleToolPID',
                                              'MCTupleToolReconstructed'],
                            UseLabXSyntax = True, RevertToPositiveID = False)
    DaVinci().UserAlgorithms.append(mctuple)
    
    seq, selseq = make_mc_unbiased_seq(desc)
    dtt = make_tuple(desc, selseq.outputLocation(), suff = '_MCUnbiasedTuple',
                     UseLabXSyntax = True, RevertToPositiveID = False)
    add_tools(dtt)
    add_mc_tools(dtt)
    seq.Members.append(dtt)
    DaVinci().UserAlgorithms.append(seq)

def configure() :
    '''Configure all DecayTreeTuple and MCDecayTreeTuple instances.'''
    tuples = add_tuples()
    if DaVinci().getProp('Simulation') :
        add_mc_tuples()
