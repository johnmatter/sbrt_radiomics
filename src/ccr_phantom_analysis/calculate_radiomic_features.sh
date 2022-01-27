#!/bin/bash

top_dir=$1
image=$top_dir/ct_img.nrrd
radiomics_dir=$top_dir/radiomics

if [ ! -f $radiomics_dir ]; then
    mkdir $radiomics_dir
fi

masks=$(find $top_dir/masks -maxdepth 1 -mindepth 1 -type f -name "*nrrd")

for mask in ${masks[@]}; do
    echo Calculating radiomic features for $mask
    radiomics_output=$radiomics_dir/$(basename $mask .nrrd).csv
    pyradiomics $image $mask -o $radiomics_output -f csv
done
