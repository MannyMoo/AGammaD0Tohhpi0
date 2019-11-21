'''
Production Info: 
    Configuration Name: LHCb
    Configuration Version: Collision18
    Event type: 90000000
-----------------------
 StepName: Stripping34-DV-v44r4-AppConfig-v3r361 
    StepId             : 133757
    ApplicationName    : DaVinci
    ApplicationVersion : v44r4
    OptionFiles        : $APPCONFIGOPTS/DaVinci/DV-Stripping34-Stripping.py;$APPCONFIGOPTS/DaVinci/DataType-2018.py;$APPCONFIGOPTS/DaVinci/InputType-RDST.py;$APPCONFIGOPTS/DaVinci/DV-RawEventJuggler-0_3-to-4_3.py;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py
    DDB                : dddb-20171030-3
    CONDDB             : cond-20180202
    ExtraPackages      : AppConfig.v3r361;Det/SQLDDDB.v7r10;TMVAWeights.v1r10
    Visible            : Y
-----------------------
Number of Steps   25609
Total number of files: 230481
         BHADRON.MDST:25609
         BHADRONCOMPLETEEVENT.DST:25609
         LOG:25609
         EW.DST:25609
         LEPTONIC.MDST:25609
         CHARM.MDST:25609
         CHARMCOMPLETEEVENT.DST:25609
         DIMUON.DST:25609
         SEMILEPTONIC.DST:25609
Number of events 0
Path:  /LHCb/Collision18/Beam6500GeV-VeloClosed-MagDown/Real Data/Reco18/Stripping34

'''

from Configurables import DaVinci
DaVinci().InputType = 'MDST'
DaVinci().DataType = '2018'

from Configurables import CondDB
CondDB().LatestGlobalTagByDataType = DaVinci().getProp('DataType')
