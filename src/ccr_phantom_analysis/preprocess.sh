#!/usr/bin/env bash

# This argument should be something like LJ/Pre or WT/Post1.
patient=$1

# Where do your patients' data live?
# TODO: make this a little more elegant; this assumes we're running this from this directory
patients_dir=./data
mask_dir=$patients_dir/$patient/masks

# # We need to convert the CT scan from DICOM to NRRD for pyradiomics.
# FILE=$patients_dir/$patient/ct_img.nrrd
# if test -f "$FILE"; then
#     echo "ERROR: $FILE exists" && exit 10
# else
#     python write_ct_as_nrrd.py $patients_dir/${patient}
# fi

# # Load the organ contours and save them in a pickle file as binary masks
# FILE=$patients_dir/$patient/contours.pickle
# if test -f "$FILE"; then
#     echo "ERROR: $FILE exists" && exit 30
# else
#     python load_structures.py $patients_dir/${patient} --prefix rtstruct
# fi

# python generate_masks.py $patients_dir/${patient}

# # Flip and fill masks; this fixes an orientation issue between Velocity and Python
# python flip_and_fill_masks.py $patients_dir/$patient
# for mask in $(ls $mask_dir/flipped_and_filled/*nrrd); do
#     echo ln -s $(realpath $mask) $mask_dir/
#     ln -s $(realpath $mask) $mask_dir/
# done

python combine_cube_rois.py $patients_dir/$patient
