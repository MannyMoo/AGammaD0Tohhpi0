#!/bin/bash

if [ -z "$(echo $PATH | grep $HOME/bin)" ] ; then
    export PATH=$HOME/bin:$PATH
fi
export QFT_PATH=~/lib/mint/qft
export MINT2=~/lib/mint/Mint2
export MINT2=~/lib/mint/Mint2
export LD_LIBRARY_PATH=${QFT_PATH}/lib:${MINT2}/lib:${LD_LIBRARY_PATH}
export DYLD_LIBRARY_PATH=${QFT_PATH}/lib:${MINT2}/lib:${LD_LIBRARY_PATH}

alias mint-find="find $MINT2 -name"
function mint-glimpse() {
    if [ $# = 2 ] ; then
	mint-find $1 -exec grep -H "$2" {} \;
    else
	find $MINT2 -type f -exec grep -H "$1" {} \;
    fi
}
