'''
Production Info: 
    Configuration Name: MC
    Configuration Version: 2016
    Event type: 27163403
-----------------------
 StepName: Sim09c - 2016 - MU - Nu1.6 (Lumi 4 at 25ns) - 25ns spillover - Pythia8 - ReDecay01 
    StepId             : 133251
    ApplicationName    : Gauss
    ApplicationVersion : v49r9
    OptionFiles        : $APPCONFIGOPTS/Gauss/Beam6500GeV-mu100-2016-nu1.6.py;$APPCONFIGOPTS/Gauss/EnableSpillover-25ns.py;$APPCONFIGOPTS/Gauss/DataType-2016.py;$APPCONFIGOPTS/Gauss/RICHRandomHits.py;$DECFILESROOT/options/@{eventType}.py;$APPCONFIGOPTS/Gauss/ReDecay-100times.py;$APPCONFIGOPTS/Gauss/ReDecay-SignalRepeatedHadronization-fix.py;$LBPYTHIA8ROOT/options/Pythia8.py;$APPCONFIGOPTS/Gauss/G4PL_FTFP_BERT_EmNoCuts.py
    DDB                : dddb-20170721-3
    CONDDB             : sim-20170721-2-vc-mu100
    ExtraPackages      : AppConfig.v3r335;DecFiles.v30r9
    Visible            : Y
-----------------------
Number of Steps   131
Total number of files: 362
         SIM:131
         LOG:131
         GAUSSHIST:100
Number of events 0
Path:  /MC/2016/Beam6500GeV-2016-MagUp-Nu1.6-25ns-Pythia8/Sim09c-ReDecay01

'''

from Configurables import DaVinci
DaVinci().InputType = 'MDST'
DaVinci().DataType = '2016'
DaVinci().Simulation = True
DaVinci().CondDBtag = 'sim-20170721-2-vc-mu100'
DaVinci().DDDBtag = 'dddb-20170721-3'
