'''
lb-run LHCbDirac/prod dirac-bookkeeping-get-files -B /MC/2016/Beam6500GeV-2016-MagUp-Nu1.6-25ns-Pythia8/Sim09c-ReDecay01/Trig0x6138160F/Reco16/Turbo03/Stripping28r1NoPrescalingFlagged/27163403/ALLSTREAMS.MDST --DQFlags OK

For BK query: {'Visible': 'Yes', 'ConfigName': 'MC', 'ConditionDescription': 'Beam6500GeV-2016-MagUp-Nu1.6-25ns-Pythia8', 'DataQuality': ['OK'], 'EventType': '27163403', 'FileType': 'ALLSTREAMS.MDST', 'ConfigVersion': '2016', 'ProcessingPass': '/Sim09c-ReDecay01/Trig0x6138160F/Reco16/Turbo03/Stripping28r1NoPrescalingFlagged', 'SimulationConditions': 'Beam6500GeV-2016-MagUp-Nu1.6-25ns-Pythia8'}
Nb of Files      : 15
Nb of Events     : 82'174
Total size       : 1.550 GB (18.9 kB per evt)
Luminosity       : 0.000 
Size  per /pb    : 0.0 GB


'''

from GaudiConf import IOHelper
IOHelper('ROOT').inputFiles(
['LFN:/lhcb/MC/2016/ALLSTREAMS.MDST/00075634/0000/00075634_00000001_7.AllStreams.mdst',
 'LFN:/lhcb/MC/2016/ALLSTREAMS.MDST/00075634/0000/00075634_00000002_7.AllStreams.mdst',
 'LFN:/lhcb/MC/2016/ALLSTREAMS.MDST/00075634/0000/00075634_00000003_7.AllStreams.mdst',
 'LFN:/lhcb/MC/2016/ALLSTREAMS.MDST/00075634/0000/00075634_00000004_7.AllStreams.mdst',
 'LFN:/lhcb/MC/2016/ALLSTREAMS.MDST/00075634/0000/00075634_00000005_7.AllStreams.mdst',
 'LFN:/lhcb/MC/2016/ALLSTREAMS.MDST/00075634/0000/00075634_00000006_7.AllStreams.mdst',
 'LFN:/lhcb/MC/2016/ALLSTREAMS.MDST/00075634/0000/00075634_00000007_7.AllStreams.mdst',
 'LFN:/lhcb/MC/2016/ALLSTREAMS.MDST/00075634/0000/00075634_00000008_7.AllStreams.mdst',
 'LFN:/lhcb/MC/2016/ALLSTREAMS.MDST/00075634/0000/00075634_00000009_7.AllStreams.mdst',
 'LFN:/lhcb/MC/2016/ALLSTREAMS.MDST/00075634/0000/00075634_00000010_7.AllStreams.mdst',
 'LFN:/lhcb/MC/2016/ALLSTREAMS.MDST/00075634/0000/00075634_00000011_7.AllStreams.mdst',
 'LFN:/lhcb/MC/2016/ALLSTREAMS.MDST/00075634/0000/00075634_00000012_7.AllStreams.mdst',
 'LFN:/lhcb/MC/2016/ALLSTREAMS.MDST/00075634/0000/00075634_00000013_7.AllStreams.mdst',
 'LFN:/lhcb/MC/2016/ALLSTREAMS.MDST/00075634/0000/00075634_00000014_7.AllStreams.mdst',
 'LFN:/lhcb/MC/2016/ALLSTREAMS.MDST/00075634/0000/00075634_00000015_7.AllStreams.mdst'],
clear=True)
