'''
Production Info: 
    Configuration Name: LHCb
    Configuration Version: Collision16
    Event type: 90000000
-----------------------
 StepName: Stripping28r1-DV-v41r4p4-AppConfig-v3r345 
    StepId             : 132874
    ApplicationName    : DaVinci
    ApplicationVersion : v41r4p4
    OptionFiles        : $APPCONFIGOPTS/DaVinci/DV-Stripping28r1-Stripping.py;$APPCONFIGOPTS/DaVinci/DataType-2016.py;$APPCONFIGOPTS/DaVinci/InputType-RDST.py;$APPCONFIGOPTS/DaVinci/DV-RawEventJuggler-0_3-to-4_2.py;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py
    DDB                : dddb-20150724
    CONDDB             : cond-20161004
    ExtraPackages      : AppConfig.v3r345;Det/SQLDDDB.v7r10;TMVAWeights.v1r9
    Visible            : Y
-----------------------
Number of Steps   95370
Total number of files: 1049070
         BHADRON.MDST:95370
         BHADRONCOMPLETEEVENT.DST:95370
         LOG:95370
         EW.DST:95370
         LEPTONIC.MDST:95370
         CALIBRATION.DST:95370
         CHARM.MDST:95370
         CHARMCOMPLETEEVENT.DST:95370
         DIMUON.DST:95370
         SEMILEPTONIC.DST:95370
         FTAG.DST:95370
Number of events 0
Path:  /LHCb/Collision16/Beam6500GeV-VeloClosed-MagDown/Real Data/Reco16/Stripping28r1

'''

from Configurables import DaVinci
DaVinci().InputType = 'MDST'
DaVinci().DataType = '2016'

from Configurables import CondDB
CondDB().LatestGlobalTagByDataType = DaVinci().getProp('DataType')
