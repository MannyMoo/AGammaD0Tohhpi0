#!/bin/bash

$ANALYSISUTILSROOT/scripts/aliases.sh
echo "alias interactive='run interactive.sh'"
echo "export AGAMMAD0TOHHPI0ROOT=$AGAMMAD0TOHHPI0ROOT"
echo "export DAVINCIDEV_PROJECT_ROOT=$DAVINCIDEV_PROJECT_ROOT"
for dname in workingdir datadir mintdatadir ; do
    dval=$(python -c "from AGammaD0Tohhpi0.data import $dname
print 'export AGAMMAD0TOHHPI0' + '$dname'.upper() + '=' + $dname
" | tail -n 1)
    eval "$dval"
    echo "$dval"
done
echo "alias ganga.py='$(which ganga.py) --ganga-version 7.1.15'"
echo "export GANGADIR=$AGAMMAD0TOHHPI0DATADIR/gangadir"
echo "export GANGASTARTUP='${GANGASTARTUP};from AGammaD0Tohhpi0.Ganga import *'"
