#!/bin/bash

for name in $(grep '_Re' $1 | awk '{print $1;}') ; do
    name="$(echo $name | sed 's/_Re//' | sed 's/\[/\\[/g' | sed 's/\]/\\]/g' | sed 's/\*/\\*/g')"
    #echo $name
    grep "$name" AllKnownDecayTrees.txt > /dev/null
    if [ $? != 0 ] ; then
	echo "Not found: $name"
    fi
done
