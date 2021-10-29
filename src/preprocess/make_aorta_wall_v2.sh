#!/bin/bash
# Generate preprocessing slurm jobs for a patient
# USAGE: ./make_aorta_wall_v2.sh patient timepoint1 timepoint2 ...

patient=$1

# Where do your patients' data live?
# TODO: make this a little more elegant; this assumes we're running this from this directory
patients_dir=../../data

# Loop over timepoints.
# The array $@ contains command line arguments,
# and :2 tells the loop to skip the first element.
for timepoint in "${@:2}"; do
    echo $timepoint

    mask_dir=$patients_dir/$patient/${timepoint}/masks

    # Generate aorta wall mask
    # Use aorta grown by 1mm as "aorta", and the unaltered aorta as "blood" (i.e. the interior)
    aorta=$(ls $mask_dir | grep -i aorta | grep -v -i blood | grep -v -i wall | grep -i grow)
    blood=$(ls $mask_dir | grep -i aorta | grep -v -i blood | grep -v -i wall | grep -v -i shrink | grep -v -i grow)
    echo aorta=$aorta
    echo blood=$blood
    if [[ -f $mask_dir/$aorta && -f $mask_dir/$blood ]]; then
        python make_aorta_wall.py $mask_dir --aorta $aorta --blood $blood --output Aorta_wall_JM2.nrrd
    else
        echo "FATAL: Could not find masks to make aorta wall nrrd" && exit 69
    fi

    echo
done
