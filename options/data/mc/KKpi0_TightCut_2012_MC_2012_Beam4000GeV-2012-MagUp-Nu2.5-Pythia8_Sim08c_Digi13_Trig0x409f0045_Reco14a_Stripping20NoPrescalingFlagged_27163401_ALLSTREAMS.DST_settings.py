'''
Production Info: 
    Configuration Name: MC
    Configuration Version: 2012
    Event type: 27163401
-----------------------
 StepName: Sim08c - 2012 - MU - Pythia8 
    StepId             : 125795
    ApplicationName    : Gauss
    ApplicationVersion : v45r5
    OptionFiles        : $APPCONFIGOPTS/Gauss/Sim08-Beam4000GeV-mu100-2012-nu2.5.py;$DECFILESROOT/options/@{eventType}.py;$LBPYTHIA8ROOT/options/Pythia8.py;$APPCONFIGOPTS/Gauss/G4PL_FTFP_BERT_EmNoCuts.py;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py
    DDB                : dddb-20130929-1
    CONDDB             : sim-20130522-1-vc-mu100
    ExtraPackages      : AppConfig.v3r179;DecFiles.v27r14p1
    Visible            : Y
-----------------------
-----------------------
 StepName: Digi13 with G4 dE/dx 
    StepId             : 124620
    ApplicationName    : Boole
    ApplicationVersion : v26r3
    OptionFiles        : $APPCONFIGOPTS/Boole/Default.py;$APPCONFIGOPTS/Boole/DataType-2012.py;$APPCONFIGOPTS/Boole/Boole-SiG4EnergyDeposit.py;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py
    DDB                : dddb-20130929-1
    CONDDB             : sim-20130522-1-vc-mu100
    ExtraPackages      : AppConfig.v3r274
    Visible            : Y
-----------------------
-----------------------
 StepName: TCK-0x409f0045 Flagged for Sim08 2012 
    StepId             : 124632
    ApplicationName    : Moore
    ApplicationVersion : v14r8p1
    OptionFiles        : $APPCONFIGOPTS/Moore/MooreSimProductionWithL0Emulation.py;$APPCONFIGOPTS/Conditions/TCK-0x409f0045.py;$APPCONFIGOPTS/Moore/DataType-2012.py;$APPCONFIGOPTS/L0/L0TCK-0x0045.py
    DDB                : dddb-20130929-1
    CONDDB             : sim-20130522-1-vc-mu100
    ExtraPackages      : AppConfig.v3r274
    Visible            : Y
-----------------------
-----------------------
 StepName: Reco14a for MC 
    StepId             : 124834
    ApplicationName    : Brunel
    ApplicationVersion : v43r2p7
    OptionFiles        : $APPCONFIGOPTS/Brunel/DataType-2012.py;$APPCONFIGOPTS/Brunel/MC-WithTruth.py;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py
    DDB                : dddb-20130929-1
    CONDDB             : sim-20130522-1-vc-mu100
    ExtraPackages      : AppConfig.v3r164
    Visible            : Y
-----------------------
-----------------------
 StepName: Stripping20-NoPrescalingFlagged for Sim08 
    StepId             : 124630
    ApplicationName    : DaVinci
    ApplicationVersion : v32r2p1
    OptionFiles        : $APPCONFIGOPTS/DaVinci/DV-Stripping20-Stripping-MC-NoPrescaling.py;$APPCONFIGOPTS/DaVinci/DataType-2012.py;$APPCONFIGOPTS/DaVinci/InputType-DST.py;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py
    DDB                : dddb-20130929-1
    CONDDB             : sim-20130522-1-vc-mu100
    ExtraPackages      : AppConfig.v3r164
    Visible            : Y
-----------------------
Number of Steps   15130
Total number of files: 30260
         SIM:3026
         DIGI:6052
         LOG:15130
         DST:3026
         ALLSTREAMS.DST:3026
Number of events 0
Path:  /MC/2012/Beam4000GeV-2012-MagUp-Nu2.5-Pythia8/Sim08c/Digi13/Trig0x409f0045/Reco14a/Stripping20NoPrescalingFlagged

'''

from Configurables import DaVinci
DaVinci().InputType = 'DST'
DaVinci().DataType = '2012'
DaVinci().Simulation = True
DaVinci().CondDBtag = 'sim-20130522-1-vc-mu100'
DaVinci().DDDBtag = 'dddb-20130929-1'
