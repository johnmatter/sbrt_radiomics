#!/bin/bash
# This is an attempt to study radiomic features in dose bins that have equal
# statistics.

min_dose=50
max_dose=60
n_bins=2

# TODO: not this. Horrible relative path practice.
patients_dir=../../../../data
patient=$1
mask_name=Aorta_wall_JM.nrrd

# Loop over timepoints.
# The array $@ contains command line arguments,
# and :2 tells the loop to skip the first element.
for timepoint in "${@:2}"; do
    echo
    this_timepoint=$patients_dir/$patient/$timepoint

    mask=$this_timepoint/masks/$mask_name
    dose=$this_timepoint/dose_in_CT_dimensions.nrrd

    bins=$(python find_bins_with_equal_statistics.py $dose $mask $n_bins $min_dose $max_dose)
    echo $timepoint : $bins

    # python ../../calculate_radiomic_features_by_dose_bin.py $this_timepoint ct_img.nrrd $mask_name $bins

done
