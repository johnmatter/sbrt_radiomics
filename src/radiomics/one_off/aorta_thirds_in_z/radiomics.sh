#!/usr/bin/env bash

# This argument should be something like LJ/Pre or WT/Post1.
patient=$1

# TODO: make this a little more elegant; this assumes we're running this from this directory
patients_dir=../../../../data

patient_dir=$patients_dir/$patient
mask_dir=$patient_dir/masks

for mask in $(ls $mask_dir/Aorta*.nrrd); do
    mask=$(basename $mask)
    python calculate.py $patient_dir ct_img.nrrd $mask 10
done
