'''
lb-run LHCbDirac/prod dirac-bookkeeping-get-files -B /MC/2015/Beam6500GeV-2015-MagUp-Nu1.6-25ns-Pythia8/Sim09c-ReDecay01/Trig0x411400a2/Reco15a/Turbo02/Stripping24r1NoPrescalingFlagged/27163403/ALLSTREAMS.MDST --DQFlags OK

For BK query: {'Visible': 'Yes', 'ConfigName': 'MC', 'ConditionDescription': 'Beam6500GeV-2015-MagUp-Nu1.6-25ns-Pythia8', 'DataQuality': ['OK'], 'EventType': '27163403', 'FileType': 'ALLSTREAMS.MDST', 'ConfigVersion': '2015', 'ProcessingPass': '/Sim09c-ReDecay01/Trig0x411400a2/Reco15a/Turbo02/Stripping24r1NoPrescalingFlagged', 'SimulationConditions': 'Beam6500GeV-2015-MagUp-Nu1.6-25ns-Pythia8'}
Nb of Files      : 7
Nb of Events     : 27'104
Total size       : 999.941 MB (36.9 kB per evt)
Luminosity       : 0.000 
Size  per /pb    : 0.0 GB


'''

from GaudiConf import IOHelper
IOHelper('ROOT').inputFiles(
['LFN:/lhcb/MC/2015/ALLSTREAMS.MDST/00075779/0000/00075779_00000001_6.AllStreams.mdst',
 'LFN:/lhcb/MC/2015/ALLSTREAMS.MDST/00075779/0000/00075779_00000002_6.AllStreams.mdst',
 'LFN:/lhcb/MC/2015/ALLSTREAMS.MDST/00075779/0000/00075779_00000003_6.AllStreams.mdst',
 'LFN:/lhcb/MC/2015/ALLSTREAMS.MDST/00075779/0000/00075779_00000004_6.AllStreams.mdst',
 'LFN:/lhcb/MC/2015/ALLSTREAMS.MDST/00075779/0000/00075779_00000006_6.AllStreams.mdst',
 'LFN:/lhcb/MC/2015/ALLSTREAMS.MDST/00075779/0000/00075779_00000007_6.AllStreams.mdst',
 'LFN:/lhcb/MC/2015/ALLSTREAMS.MDST/00075779/0000/00075779_00000008_6.AllStreams.mdst'],
clear=True)
