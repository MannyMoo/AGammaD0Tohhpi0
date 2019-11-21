#!/bin/bash

$ANALYSISUTILSROOT/scripts/aliases.sh
echo "alias interactive='run interactive.sh'"
echo "export AGAMMAD0TOHHPI0ROOT=$AGAMMAD0TOHHPI0ROOT"
echo "export DAVINCIDEV_PROJECT_ROOT=$DAVINCIDEV_PROJECT_ROOT"
for dname in workingdir datadir mintdatadir ; do
    python -c "from AGammaD0Tohhpi0.data import $dname
print 'export AGAMMAD0TOHHPI0' + '$dname'.upper() + '=' + $dname
" | tail -n 1
done
