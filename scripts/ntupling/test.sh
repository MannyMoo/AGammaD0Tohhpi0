#!/bin/bash

#data=real/RealData_2018_Charm_MagUp

data=mc/pipipi0_DecProdCut_PHSP_2016_MC_2016_Beam6500GeV-2016-MagUp-Nu1.6-25ns-Pythia8_Sim09c_Trig0x6138160F_Reco16_Turbo03_Stripping28r1NoPrescalingFlagged_27163403_ALLSTREAMS.DST

opts="$AGAMMAD0TOHHPI0ROOT/options/data/${data}.py $AGAMMAD0TOHHPI0ROOT/options/data/${data}_settings.py $AGAMMAD0TOHHPI0ROOT/options/data/${data}_catalog.py"
opts+=" $AGAMMAD0TOHHPI0ROOT/options/ntupling/tuples.py"

opts+=" $ANALYSISUTILSROOT/options/VeloTrackAssoc.py"

gaudirun.py --option="from Configurables import DaVinci;DaVinci().EvtMax = 10000" $opts >& stdout
