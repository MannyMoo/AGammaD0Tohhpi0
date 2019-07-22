
'''
Production Info: 
    Configuration Name: MC
    Configuration Version: 2016
    Event type: 27163404
-----------------------
 StepName: Digi14b for 2015 - 25ns spillover 
    StepId             : 132434
    ApplicationName    : Boole
    ApplicationVersion : v30r2p1
    OptionFiles        : $APPCONFIGOPTS/Boole/Default.py;$APPCONFIGOPTS/Boole/EnableSpillover.py;$APPCONFIGOPTS/Boole/DataType-2015.py;$APPCONFIGOPTS/Boole/Boole-SetOdinRndTrigger.py
    DDB                : dddb-20170721-3
    CONDDB             : sim-20170721-2-vc-mu100
    ExtraPackages      : AppConfig.v3r338
    Visible            : N
-----------------------
-----------------------
 StepName: L0 emulation for 2016 - TCK 0x160F - DIGI 
    StepId             : 130088
    ApplicationName    : Moore
    ApplicationVersion : v25r4
    OptionFiles        : $APPCONFIGOPTS/L0App/L0AppSimProduction.py;$APPCONFIGOPTS/L0App/L0AppTCK-0x160F.py;$APPCONFIGOPTS/L0App/ForceLUTVersionV8.py;$APPCONFIGOPTS/L0App/DataType-2016.py;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py
    DDB                : dddb-20170721-3
    CONDDB             : sim-20170721-2-vc-mu100
    ExtraPackages      : AppConfig.v3r297
    Visible            : N
-----------------------
-----------------------
 StepName: TCK-0x5138160F (HLT1) Flagged for 2016 - DIGI 
    StepId             : 130089
    ApplicationName    : Moore
    ApplicationVersion : v25r4
    OptionFiles        : $APPCONFIGOPTS/Moore/MooreSimProductionForSeparateL0AppStep2015.py;$APPCONFIGOPTS/Conditions/TCK-0x5138160F.py;$APPCONFIGOPTS/Moore/DataType-2016.py;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py;$APPCONFIGOPTS/Moore/MooreSimProductionHlt1.py
    DDB                : dddb-20170721-3
    CONDDB             : sim-20170721-2-vc-mu100
    ExtraPackages      : AppConfig.v3r297
    Visible            : N
-----------------------
-----------------------
 StepName: TCK-0x6139160F (HLT2) Flagged for 2016 - DIGI 
    StepId             : 130090
    ApplicationName    : Moore
    ApplicationVersion : v25r4
    OptionFiles        : $APPCONFIGOPTS/Moore/MooreSimProductionForSeparateL0AppStep2015.py;$APPCONFIGOPTS/Conditions/TCK-0x6139160F.py;$APPCONFIGOPTS/Moore/DataType-2016.py;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py;$APPCONFIGOPTS/Moore/MooreSimProductionHlt2.py
    DDB                : dddb-20170721-3
    CONDDB             : sim-20170721-2-vc-mu100
    ExtraPackages      : AppConfig.v3r297
    Visible            : Y
-----------------------
-----------------------
 StepName: Reco16 for MC 2016 
    StepId             : 130615
    ApplicationName    : Brunel
    ApplicationVersion : v50r2
    OptionFiles        : $APPCONFIGOPTS/Brunel/DataType-2016.py;$APPCONFIGOPTS/Brunel/MC-WithTruth.py;$APPCONFIGOPTS/Brunel/SplitRawEventOutput.4.3.py;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py
    DDB                : dddb-20170721-3
    CONDDB             : sim-20170721-2-vc-mu100
    ExtraPackages      : AppConfig.v3r314;SQLDDDB.v7r10
    Visible            : Y
-----------------------
-----------------------
 StepName: Turbo lines (MC), Turbo 2016 - Stripping28 - DST 
    StepId             : 131792
    ApplicationName    : DaVinci
    ApplicationVersion : v41r4p3
    OptionFiles        : $APPCONFIGOPTS/Turbo/Tesla_2016_LinesFromStreams_MC.py;$APPCONFIGOPTS/Turbo/Tesla_PR_Truth_2016.py;$APPCONFIGOPTS/Turbo/Tesla_Simulation_2016.py
    DDB                : dddb-20170721-3
    CONDDB             : sim-20170721-2-vc-mu100
    ExtraPackages      : AppConfig.v3r322;TurboStreamProd.v4r1p4
    Visible            : Y
-----------------------
-----------------------
 StepName: Stripping28r1-NoPrescalingFlagged for Sim09 - pp at 13 TeV - DST 
    StepId             : 132983
    ApplicationName    : DaVinci
    ApplicationVersion : v41r4p4
    OptionFiles        : $APPCONFIGOPTS/DaVinci/DV-Stripping28r1-Stripping-MC-NoPrescaling-DST.py;$APPCONFIGOPTS/DaVinci/DataType-2016.py;$APPCONFIGOPTS/DaVinci/InputType-DST.py
    DDB                : dddb-20170721-3
    CONDDB             : sim-20170721-2-vc-mu100
    ExtraPackages      : AppConfig.v3r348;TMVAWeights.v1r9
    Visible            : Y
-----------------------
Number of Steps   5523
Total number of files: 11046
         DIGI:3156
         LOG:5523
         DST:1578
         ALLSTREAMS.DST:789
Number of events
File Type           Number of events    Event Type          EventInputStat
ALLSTREAMS.DST      2000189             27163404            2000189
Path:  /MC/2016/Beam6500GeV-2016-MagUp-Nu1.6-25ns-Pythia8/Sim09c/Trig0x6138160F/Reco16/Turbo03/Stripping28r1NoPrescalingFlagged
/MC/2016/Beam6500GeV-2016-MagUp-Nu1.6-25ns-Pythia8/Sim09c/Trig0x6138160F/Reco16/Turbo03/Stripping28r1NoPrescalingFlagged/27163404/ALLSTREAMS.DST
'''

from Configurables import DaVinci
from Gaudi.Configuration import importOptions

importOptions('$APPCONFIGOPTS/DaVinci/DataType-2016.py')
DaVinci().InputType = 'DST'
DaVinci().CondDBtag = 'sim-20170721-2-vc-mu100'
DaVinci().DDDBtag = 'dddb-20170721-3'
DaVinci().Simulation = True

