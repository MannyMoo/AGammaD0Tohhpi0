#!/bin/bash

config=$AGAMMAD0TOHHPI0ROOT/scripts/mint/pipipi0.txt
outputdir=$(grep integratorsDirectory $config | awk '{print $2;}')
name=$(basename $outputdir)
outputdir=$(dirname $outputdir)
if [ ! -e $outputdir ] ; then
    mkdir -p $outputdir
fi
echo $outputdir
genTimeDependent.exe < $config >& $outputdir/${name}_stdout
