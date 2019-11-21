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
Number of Steps   80303
Total number of files: 722727
         BHADRON.MDST:80303
         BHADRONCOMPLETEEVENT.DST:80303
         LOG:80303
         EW.DST:80303
         LEPTONIC.MDST:80303
         CHARM.MDST:80303
         CHARMCOMPLETEEVENT.DST:80303
         DIMUON.DST:80303
         SEMILEPTONIC.DST:80303
Number of events 0
Path:  /LHCb/Collision18/Beam6500GeV-VeloClosed-MagUp/Real Data/Reco18/Stripping34

'''

from Configurables import DaVinci
DaVinci().InputType = 'MDST'
DaVinci().DataType = '2018'

from Configurables import CondDB
CondDB().LatestGlobalTagByDataType = DaVinci().getProp('DataType')
