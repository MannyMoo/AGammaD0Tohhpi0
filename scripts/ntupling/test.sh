#!/bin/bash

#opts="$AGAMMAD0TOHHPI0ROOT/options/data/mc/pipipi0-MagDown-MCFlagged-1File.py $AGAMMAD0TOHHPI0ROOT/options/data/mc/pipipi0-MagDown-MCFlagged_DV.py $AGAMMAD0TOHHPI0ROOT/options/data/mc/pipipi0-MagDown-MCFlagged-1File_catalog.py"
#opts="$AGAMMAD0TOHHPI0ROOT/options/data/real/Reco16_Run182594.py $AGAMMAD0TOHHPI0ROOT/options/data/real/Reco16_Run182594_DV.py"
#opts+=" $AGAMMAD0TOHHPI0ROOT/options/ntupling/stripping.py"

data=real/RealData_2018_Charm_MagUp
opts="$AGAMMAD0TOHHPI0ROOT/options/data/${data}.py $AGAMMAD0TOHHPI0ROOT/options/data/${data}_settings.py $AGAMMAD0TOHHPI0ROOT/options/data/${data}_catalog.py"
opts+=" $AGAMMAD0TOHHPI0ROOT/options/ntupling/tuples.py"
gaudirun.py --option="from Configurables import DaVinci;DaVinci().EvtMax = 1000" $opts >& stdout
