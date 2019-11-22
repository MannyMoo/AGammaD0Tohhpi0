'''
Production Info: 
    Configuration Name: MC
    Configuration Version: 2012
    Event type: 27163403
-----------------------
 StepName: Sim08e - 2012 - MD - Pythia8 
    StepId             : 126084
    ApplicationName    : Gauss
    ApplicationVersion : v45r7
    OptionFiles        : $APPCONFIGOPTS/Gauss/Sim08-Beam4000GeV-md100-2012-nu2.5.py;$DECFILESROOT/options/@{eventType}.py;$LBPYTHIA8ROOT/options/Pythia8.py;$APPCONFIGOPTS/Gauss/G4PL_FTFP_BERT_EmNoCuts.py;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py
    DDB                : dddb-20130929-1
    CONDDB             : sim-20130522-1-vc-md100
    ExtraPackages      : AppConfig.v3r182;DecFiles.v27r17
    Visible            : Y
-----------------------
-----------------------
 StepName: Digi13 with G4 dE/dx 
    StepId             : 124620
    ApplicationName    : Boole
    ApplicationVersion : v26r3
    OptionFiles        : $APPCONFIGOPTS/Boole/Default.py;$APPCONFIGOPTS/Boole/DataType-2012.py;$APPCONFIGOPTS/Boole/Boole-SiG4EnergyDeposit.py;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py
    DDB                : dddb-20130929-1
    CONDDB             : sim-20130522-1-vc-md100
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
    CONDDB             : sim-20130522-1-vc-md100
    ExtraPackages      : AppConfig.v3r274
    Visible            : Y
-----------------------
Number of Steps   11928
Total number of files: 23856
         SIM:3976
         DIGI:7952
         LOG:11928
Number of events 0
Path:  /MC/2012/Beam4000GeV-2012-MagDown-Nu2.5-Pythia8/Sim08e/Digi13/Trig0x409f0045

'''

from Configurables import DaVinci
DaVinci().InputType = 'DST'
DaVinci().DataType = '2012'
DaVinci().Simulation = True
DaVinci().CondDBtag = 'sim-20130522-1-vc-md100'
DaVinci().DDDBtag = 'dddb-20130929-1'
