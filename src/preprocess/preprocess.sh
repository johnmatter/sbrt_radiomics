#!/usr/bin/env bash

# This argument should be something like LJ/Pre or WT/Post1.
patient=$1

# Where do your patients' data live?
# TODO: make this a little more elegant; this assumes we're running this from this directory
patients_dir=../../data
mask_dir=$patients_dir/$patient/masks

# We need to convert the CT scan from DICOM to NRRD for pyradiomics.
FILE=$patients_dir/$patient/ct_img.nrrd
if test -f "$FILE"; then
    echo "ERROR: $FILE exists" && exit 10
else
    python write_ct_as_nrrd.py $patients_dir/${patient}
fi

# We need to convert the dose map from DICOM to NRRD for pyradiomics.
# This assumes your dose has already been resampled in Velocity to match the
# image dimensions and voxel size of the CT scan.
FILE=$patients_dir/$patient/dose_in_CT_dimensions.nrrd
if test -f "$FILE"; then
    echo "ERROR: $FILE exists" && exit 20
else
    python convert_velocity_resampled_dose.py $patients_dir/${patient}
fi

# Load the organ contours and save them in a pickle file as binary masks
FILE=$patients_dir/$patient/contours.pickle
if test -f "$FILE"; then
    echo "ERROR: $FILE exists" && exit 30
else
    python load_structures.py $patients_dir/${patient} --prefix struct
fi

# Convert the binary masks into nrrd files for use with pyradiomics
if [ "$(ls masks)" ]; then
    echo "ERROR: Masks directory is not empty. Please empty it and try again." && exit 40
else echo nope;
    python generate_masks.py $patients_dir/${patient}

    # Flip and fill masks; this fixes an orientation issue between Velocity and Python
    python flip_and_fill_masks.py $patients_dir/$patient
    for mask in $(ls $mask_dir/flipped_and_filled/*nrrd); do
        echo ln -s $(realpath $mask) $mask_dir/
        ln -s $(realpath $mask) $mask_dir/
    done

    # Generate aorta wall mask
    aorta=$mask_dir/Aorta_-_Shrink__1.00mm.nrrd
    blood=$mask_dir/Aorta_blood.nrrd
    if [[ -f $mask_dir/$aorta && -f $mask_dir/$blood ]]; then
        echo Using the following masks for aorta wall:
        echo outer : $aorta
        echo inner : $blood
        python make_aorta_wall.py $patients_dir/$patient/masks --aorta $aorta --blood $blood
    else
        echo "FATAL: Could not find masks to make aorta wall nrrd" && exit 50
    fi

    # Generate the new version
    # Use aorta grown by 1mm as "aorta", and the unaltered aorta as "blood" (i.e. the interior)
    aorta=$mask_dir/Aorta_-_Grow__1.00mm.nrrd
    blood=$mask_dir/Aorta
    if [[ -f $mask_dir/$aorta && -f $mask_dir/$blood ]]; then
        echo Using the following masks for aorta wall v2:
        echo outer : $aorta
        echo inner : $blood
        python make_aorta_wall.py $mask_dir --aorta $aorta --blood $blood --output Aorta_wall_JM2.nrrd
    else
        echo "FATAL: Could not find masks to make aorta wall 2 nrrd" && exit 60
    fi
fi
