'''
Production Info: 
    Configuration Name: MC
    Configuration Version: 2015
    Event type: 27263400
-----------------------
 StepName: Sim09c - 2015 Nominal - MU - Nu1.6 (Lumi 4 at 25ns) - 25ns spillover - Pythia8 
    StepId             : 132713
    ApplicationName    : Gauss
    ApplicationVersion : v49r8
    OptionFiles        : $APPCONFIGOPTS/Gauss/Beam6500GeV-mu100-2015-nu1.6.py;$APPCONFIGOPTS/Gauss/EnableSpillover-25ns.py;$APPCONFIGOPTS/Gauss/DataType-2015.py;$APPCONFIGOPTS/Gauss/RICHRandomHits.py;$DECFILESROOT/options/@{eventType}.py;$LBPYTHIA8ROOT/options/Pythia8.py;$APPCONFIGOPTS/Gauss/G4PL_FTFP_BERT_EmNoCuts.py
    DDB                : dddb-20170721-3
    CONDDB             : sim-20161124-vc-mu100
    ExtraPackages      : AppConfig.v3r335;DecFiles.v30r6
    Visible            : Y
-----------------------
Number of Steps   878
Total number of files: 1856
         SIM:878
         LOG:878
         GAUSSHIST:100
Number of events 0
Path:  /MC/2015/Beam6500GeV-2015-MagUp-Nu1.6-25ns-Pythia8/Sim09c

'''

from Configurables import DaVinci
DaVinci().InputType = 'DST'
DaVinci().DataType = '2015'
DaVinci().Simulation = True
DaVinci().CondDBtag = 'sim-20161124-vc-mu100'
DaVinci().DDDBtag = 'dddb-20170721-3'
