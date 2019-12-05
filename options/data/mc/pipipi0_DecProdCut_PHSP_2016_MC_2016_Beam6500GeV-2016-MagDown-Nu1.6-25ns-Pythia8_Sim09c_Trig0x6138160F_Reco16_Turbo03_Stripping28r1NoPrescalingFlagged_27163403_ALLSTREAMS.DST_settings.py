'''
Production Info: 
    Configuration Name: MC
    Configuration Version: 2016
    Event type: 27163403
-----------------------
 StepName: Sim09c - 2016 - MD - Nu1.6 (Lumi 4 at 25ns) - 25ns spillover - Pythia8 
    StepId             : 132910
    ApplicationName    : Gauss
    ApplicationVersion : v49r8
    OptionFiles        : $APPCONFIGOPTS/Gauss/Beam6500GeV-md100-2016-nu1.6.py;$APPCONFIGOPTS/Gauss/EnableSpillover-25ns.py;$APPCONFIGOPTS/Gauss/DataType-2016.py;$APPCONFIGOPTS/Gauss/RICHRandomHits.py;$DECFILESROOT/options/@{eventType}.py;$LBPYTHIA8ROOT/options/Pythia8.py;$APPCONFIGOPTS/Gauss/G4PL_FTFP_BERT_EmNoCuts.py
    DDB                : dddb-20170721-3
    CONDDB             : sim-20170721-2-vc-md100
    ExtraPackages      : AppConfig.v3r335;DecFiles.v30r7
    Visible            : Y
-----------------------
Number of Steps   5192
Total number of files: 10484
         SIM:5192
         LOG:5192
         GAUSSHIST:100
Number of events 0
Path:  /MC/2016/Beam6500GeV-2016-MagDown-Nu1.6-25ns-Pythia8/Sim09c

'''

from Configurables import DaVinci
DaVinci().InputType = 'DST'
DaVinci().DataType = '2016'
DaVinci().Simulation = True
DaVinci().CondDBtag = 'sim-20170721-2-vc-md100'
DaVinci().DDDBtag = 'dddb-20170721-3'
