#!/bin/bash
patient=$1

find $1 -type f -name "*pickle" -exec rm {} \;
find $1 -type f -name "*nrrd" -exec rm {} \;
find $1 -type l -name "*nrrd" -exec rm {} \;
find $1 -type f -name "*csv" -exec rm {} \;
rm -rf $1/masks
