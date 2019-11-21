'''
Production Info: 
    Configuration Name: LHCb
    Configuration Version: Collision17
    Event type: 90000000
-----------------------
 StepName: Stripping29r2-DV-v42r7p2-AppConfig-v3r353 
    StepId             : 133314
    ApplicationName    : DaVinci
    ApplicationVersion : v42r7p2
    OptionFiles        : $APPCONFIGOPTS/DaVinci/DV-Stripping29r2-Stripping.py;$APPCONFIGOPTS/DaVinci/DataType-2017.py;$APPCONFIGOPTS/DaVinci/InputType-RDST.py;$APPCONFIGOPTS/DaVinci/DV-RawEventJuggler-0_3-to-4_2.py;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py
    DDB                : dddb-20170721-3
    CONDDB             : cond-20170724
    ExtraPackages      : AppConfig.v3r353;Det/SQLDDDB.v7r10;TMVAWeights.v1r9
    Visible            : Y
-----------------------
Number of Steps   60072
Total number of files: 540648
         BHADRON.MDST:60072
         BHADRONCOMPLETEEVENT.DST:60072
         LOG:60072
         EW.DST:60072
         LEPTONIC.MDST:60072
         CHARM.MDST:60072
         CHARMCOMPLETEEVENT.DST:60072
         DIMUON.DST:60072
         SEMILEPTONIC.DST:60072
Number of events 0
Path:  /LHCb/Collision17/Beam6500GeV-VeloClosed-MagDown/Real Data/Reco17/Stripping29r2

'''

from Configurables import DaVinci
DaVinci().InputType = 'MDST'
DaVinci().DataType = '2017'

from Configurables import CondDB
CondDB().LatestGlobalTagByDataType = DaVinci().getProp('DataType')
