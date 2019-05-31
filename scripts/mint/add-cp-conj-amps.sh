#!/bin/bash

echo >> $1
grep 'D0.*_[RI][em]' $1 | sed 's/D0/Dbar0/' | sed 's/\+/$/g' | sed 's/-\([^>0-9]\)/+\1/g' | sed 's/\$/-/g' >> $1
