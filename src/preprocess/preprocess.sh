#!/usr/bin/env bash

# This argument should be something like LJ/Pre or WT/Post1.
patient=$1

# Where do your patients' data live?
# TODO: make this a little more elegant; this assumes we're running this from this directory
patients_dir=../../data
mask_dir=$patients_dir/$patient/masks

# We need to convert the CT scan from DICOM to NRRD for pyradiomics.
python write_ct_as_nrrd.py $patients_dir/${patient}

# We need to convert the dose map from DICOM to NRRD for pyradiomics.
# This assumes your dose has already been resampled in Velocity to match the
# image dimensions and voxel size of the CT scan.
python convert_velocity_resampled_dose.py $patients_dir/${patient}

# Load the organ contours and save them
python load_structures.py $patients_dir/${patient} --prefix struct
python generate_masks.py $patients_dir/${patient}

# Flip and fill masks
python flip_and_fill_masks.py $patients_dir/$patient
for mask in $(ls $mask_dir/flipped_and_filled/*nrrd); do
    echo ln -s $(realpath $mask) $mask_dir/
    ln -s $(realpath $mask) $mask_dir/
done

# Generate aorta wall mask
aorta=$(ls $mask_dir | grep -i aorta | grep -v -i blood | grep -v -i wall | grep -i shrink)
blood=$(ls $mask_dir | grep -i aorta | grep -i blood)
if [[ -f $mask_dir/$aorta && -f $mask_dir/$blood ]]; then
    python make_aorta_wall.py $patients_dir/$patient/masks --aorta $aorta --blood $blood
else
    echo "FATAL: Could not find masks to make aorta wall nrrd" && exit 69
fi
