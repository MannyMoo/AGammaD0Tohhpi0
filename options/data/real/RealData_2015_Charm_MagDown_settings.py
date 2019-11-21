'''
Production Info: 
    Configuration Name: LHCb
    Configuration Version: Collision15
    Event type: 90000000
-----------------------
 StepName: Stripping24r1-DV-v38r1p6-AppConfig-v3r343 
    StepId             : 132731
    ApplicationName    : DaVinci
    ApplicationVersion : v38r1p6
    OptionFiles        : $APPCONFIGOPTS/DaVinci/DV-Stripping24r1-Stripping.py;$APPCONFIGOPTS/DaVinci/DataType-2015.py;$APPCONFIGOPTS/DaVinci/InputType-RDST.py;$APPCONFIGOPTS/DaVinci/DV-RawEventJuggler-0_3-to-4_2.py;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py
    DDB                : dddb-20150724
    CONDDB             : cond-20150828
    ExtraPackages      : AppConfig.v3r343;Det/SQLDDDB.v7r10;TMVAWeights.v1r9
    Visible            : Y
-----------------------
Number of Steps   76815
Total number of files: 844965
         BHADRON.MDST:76815
         BHADRONCOMPLETEEVENT.DST:76815
         LOG:76815
         EW.DST:76815
         LEPTONIC.MDST:76815
         CALIBRATION.DST:76815
         CHARM.MDST:76815
         CHARMCOMPLETEEVENT.DST:76815
         DIMUON.DST:76815
         SEMILEPTONIC.DST:76815
         FTAG.DST:76815
Number of events 0
Path:  /LHCb/Collision15/Beam6500GeV-VeloClosed-MagDown/Real Data/Reco15a/Stripping24r1

'''

from Configurables import DaVinci
DaVinci().InputType = 'MDST'
DaVinci().DataType = '2015'

from Configurables import CondDB
CondDB().LatestGlobalTagByDataType = DaVinci().getProp('DataType')
