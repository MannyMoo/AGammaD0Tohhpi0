from Configurables import TupleToolTISTOS, LoKi__Hybrid__TupleTool, DaVinci, TupleToolDecayTreeFitter, \
    TupleToolPropertime, TupleToolANNPID
from StrippingDoc import StrippingDoc
from Configurables import TupleToolMCTruth, MCTupleToolPrompt
from AnalysisUtils.Selections.mcselections import make_mc_unbiased_seq
from AnalysisUtils.ntupling import make_mc_tuple, make_tuple
from AnalysisUtils.DecayDescriptors.DecayDescriptors import parse_decay_descriptor
from collections import defaultdict
from PhysSelPython.Wrappers import StrippingData, TupleSelection, SelectionSequence
from PhysSelPython.MomentumScaling import MomentumScaling

linedocs = None
def get_line_docs() :
    '''Get the doc for the relevant stripping lines.'''
    
    # Make sure this is only called once.
    global linedocs
    if linedocs:
        return linedocs

    doc = StrippingDoc('stripping28')
    linedocs = doc.filter_lines(lambda line : (line.name.startswith('DstarD0ToHHPi0') 
                                           and not 'KK' in line.name 
                                           and not 'WIDEMASS' in line.name))
    aliases = {False : ['Dst', 'D0', 'Kst', 'h1', 'h2', 'pi0', 'piTag'],
               True : ['Dst', 'D0', 'Kst', 'h1', 'h2', 'pi0', 'gamma1', 'gamma2', 'piTag']}

    for linedoc in linedocs:
        branches = defaultdict(list)
        resolved = ('_R_' in linedoc.name)
        if resolved:
            for i, desc in enumerate(linedoc.decaydescriptors):
                linedoc.decaydescriptors[i] = desc.replace('pi0', '( pi0 -> gamma gamma )')
        parseddescs = []
        for desc in linedoc.decaydescriptors:
            parseddesc = parse_decay_descriptor(desc)
            parseddesc.set_aliases(aliases[resolved])
            for alias, brdesc in parseddesc.branches().items():
                branches[alias].append(brdesc)
            parseddescs.append(parseddesc)
        linedoc.parseddecaydescriptors = parseddescs
        linedoc.branches = {alias : '( ' + ' ) || ( '.join(descs) + ' )' for alias, descs in branches.items()}
    return linedocs

def add_tuples() :
    '''Make ntuples for the D0->hhpi0 stripping lines. Assumes the data settings have already
    been configured in DaVinci.'''

    # Normal data
    stream = 'Charm.mdst'
    simulation = DaVinci().getProp('Simulation')
    # For restripping
    if DaVinci().getProp('ProductionType') == 'Stripping' :
        stream = 'CharmCompleteEvent.dst'
    # For MC.
    elif simulation :
        stream = 'AllStreams.dst'

    fulldst = stream.endswith('.dst')
    streamname = '.'.join(stream.split('.')[:-1])

    tuples = []
    seqs = []
    for line in get_line_docs() :
        stripdata = StrippingData(line.name, stream = (stream if fulldst else None))
        if not simulation:
            stripdata = MomentumScaling(stripdata)
        dttsel = TupleSelection(line.name + 'Tuple', [stripdata], **line.tuple_config())
        dtt = dttsel.algorithm()
        dtt.addBranches(line.branches)
        tuples.append(dtt)
        add_tools(dtt)
        seq = SelectionSequence(line.name + 'Seq', TopSelection = dttsel)
        DaVinci().UserAlgorithms += [seq.sequence()]
    DaVinci(**line.davinci_config(stream))

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

    dtt.Dst.addTupleTool(tttistos)
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
        ttdtf.UseFullTreeInName = True
        dtt.Dst.addTupleTool(ttdtf)

    hybrid = dtt.Dst.addTupleTool('LoKi__Hybrid__TupleTool')
    # Real data
    if 'K*' in dtt.Decay :
        for i in 1, 2 :
            form = ' - '.join(['(CHILD(E, 1, 1, {0}) + CHILD(E, 1, 2))**2'.format(i)]
                              + ['(CHILD(P{1}, 1, 1, {0}) + CHILD(P{1}, 1, 2))**2'.format(i, p) for p in 'XYZ'])
            form = 'DTF_FUN({0}, False, "D0", "pi0", -1., LoKi.Constants.NegativeInfinity)'.format(form)
            hybrid.Variables['S{0}3'.format(i)] = form
    # MC
    else :
        for i in 1, 2 :
            form = ' - '.join(['(CHILD(E, 1, {0}) + CHILD(E, 1, 3))**2'.format(i)]
                              + ['(CHILD(P{1}, 1, {0}) + CHILD(P{1}, 1, 3))**2'.format(i, p) for p in 'XYZ'])
            form = 'DTF_FUN({0}, False, "D0", "pi0", -1., LoKi.Constants.NegativeInfinity)'.format(form)
            hybrid.Variables['S{0}3'.format(i)] = form

def mc_descriptors() :
    '''Get the MC decay descriptors.'''
    descs = []
    aliases = ['Dst', 'D0', 'h1', 'h2', 'pi0', 'piTag']
    for minus, plus in ('pi', 'pi'), ('K', 'K'), ('K', 'pi') :
        desc = parse_decay_descriptor('[ D*(2010)+ ==> ( D0 ==> {minus}-  {plus}+  pi0 )  pi+ ]CC'.format(minus = minus, plus = plus))
        desc.set_aliases(aliases)
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
    dtt.Dst.addTupleTool(ttmcmatch)
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
                                              'MCTupleToolReconstructed'])
    DaVinci().UserAlgorithms.append(mctuple)
    
    seq, selseq = make_mc_unbiased_seq(desc)
    dtt = make_tuple(desc, selseq.outputLocation(), suff = '_MCUnbiasedTuple')
    add_tools(dtt)
    add_mc_tools(dtt)
    seq.Members.append(dtt)
    DaVinci().UserAlgorithms.append(seq)

def configure() :
    '''Configure all DecayTreeTuple and MCDecayTreeTuple instances.'''
    tuples = add_tuples()
    if DaVinci().getProp('Simulation') :
        add_mc_tuples()
