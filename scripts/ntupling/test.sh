#!/bin/bash

data=real/RealData_2018_Charm_MagUp
opts="$AGAMMAD0TOHHPI0ROOT/options/data/${data}.py $AGAMMAD0TOHHPI0ROOT/options/data/${data}_settings.py $AGAMMAD0TOHHPI0ROOT/options/data/${data}_catalog.py"
opts+=" $AGAMMAD0TOHHPI0ROOT/options/ntupling/tuples.py"
gaudirun.py --option="from Configurables import DaVinci;DaVinci().EvtMax = 1000" $opts >& stdout
