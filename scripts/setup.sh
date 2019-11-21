#!/bin/bash

# Get the latest v4X version of DaVinci.
DaVinciVersion=$(lb-run --list DaVinci | grep v4 | head -n 1 | awk '{print $1;}')
github=0
if [ $github = 0 ] ; then
    PackageUrl=ssh://git@gitlab.cern.ch:7999/malexand/AGammaD0Tohhpi0.git
    AnalysisUtilsUrl=ssh://git@gitlab.cern.ch:7999/malexand/AnalysisUtils.git
else
    PackageUrl=git@github.com:MannyMoo/AGammaD0Tohhpi0.git
    AnalysisUtilsUrl=git@github.com:MannyMoo/AnalysisUtils.git
fi
urls="$PackageUrl $AnalysisUtilsUrl git@github.com:MannyMoo/qft.git git@github.com:MannyMoo/Mint2.git"

lb-dev DaVinci/$DaVinciVersion
cd DaVinciDev_$DaVinciVersion
for url in $urls ; do
    git clone $url
done
# For StrippingData selection.
git lb-use Phys
git lb-checkout Phys/malexand-strippingdata PhysSel/PhysSelPython

make
