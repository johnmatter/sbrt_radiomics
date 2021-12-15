import os
import sys
import csv
import six
import argparse

import warnings

import numpy as np
import SimpleITK as sitk
import nrrd
from radiomics import featureextractor

def cleanup(radiomic_features):
    keys_to_remove = []
    keys_to_remove.append('diagnostics_Configuration_Settings')
    keys_to_remove.append('diagnostics_Configuration_EnabledImageTypes')
    keys_to_remove.append('diagnostics_Image-original_Spacing')
    keys_to_remove.append('diagnostics_Image-original_Size')
    keys_to_remove.append('diagnostics_Mask-original_Spacing')
    keys_to_remove.append('diagnostics_Mask-original_Size')
    keys_to_remove.append('diagnostics_Mask-original_BoundingBox')
    keys_to_remove.append('diagnostics_Mask-original_CenterOfMassIndex')
    keys_to_remove.append('diagnostics_Mask-original_CenterOfMass')

    for key in keys_to_remove:
        radiomic_features.pop(key, None)

    return radiomic_features

def write_mask(mask, low_z, high_z, directory):
    # create a copy, because python arrays are effectively passed by value
    new_mask = np.copy(mask)

    # Set region outside [low_z, high_z] (inclusive) to zero
    low_slice = max(0, low_z-1)
    high_slice = min(new_mask.shape[2]-1, high_z+1)
    new_mask[:,:, 0:low_slice] *= 0
    new_mask[:,:, high_slice:(new_mask.shape[2]-1)] *= 0

    # Write mask to disk
    mask_filename = args.mask
    mask_splitext = os.path.splitext(mask_filename)
    output_filename = '%s_z_slice_%d_to_%d%s' % (mask_splitext[0], low_z, high_z, mask_splitext[1])
    output_filename = output_filename.replace(' ','_')

    binned_mask_directory=os.path.join(directory, 'binned_by_z')
    if (not(os.path.exists(binned_mask_directory))):
        print('Creating directory ' + binned_mask_directory)
        os.mkdir(binned_mask_directory)

    output_filename = os.path.join(binned_mask_directory, output_filename)
    nrrd.write(output_filename, new_mask)
    print('Wrote ' + output_filename)

    return output_filename

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=str, help='The patient directory to look in /somewhere/fullpath/PATIENT/')
    parser.add_argument('image', type=str, help='The patient CT to use (assumed to be in PATIENT/')
    parser.add_argument('mask', type=str, help='The name of the mask to use (assumed to be in PATIENT/masks/)')
    parser.add_argument('--output_directory', type=str, help='Where to write output CSV')
    args = parser.parse_args()

    # Assume directory name of form args.directory=/somewhere/patients/AJ/TimePoint
    # i.e. we need to drop the last directory in the path, as well as the beginning bit
    patient_initials = os.path.basename(os.path.dirname(args.directory))
    mask_name = os.path.splitext(args.mask)[0]

    # Try to load data
    # TODO: It would be wise to make sure the user hasn't specified a full path for the mask/CT
    try:
        # Read mask
        mask_directory = os.path.join(args.directory, 'masks')
        mask_filename = os.path.join(mask_directory, args.mask)
        mask, hdr = nrrd.read(mask_filename)
    except Exception as ex:
        print(type(ex), ex)
        print('Failed to load mask: ' + mask_filename)
        sys.exit(1)

    # Check if CT exists
    image_filename = os.path.join(args.directory, args.image)
    if not(os.path.exists(image_filename)):
        print('CT img does not exist')
        sys.exit(1)

    # Create feature extractor
    extractor = featureextractor.RadiomicsFeatureExtractor()

    # Find locations in Z at which to 'slice', create a mask, and then calculate radiomic features
    nonzero_z = np.nonzero(mask)[2]
    top = max(nonzero_z)
    bottom = min(nonzero_z)
    z_bins = np.arange(4)*int((top-bottom)/3) + bottom


    radiomic_features = {}

    bin_labels = ['low_z', 'mid_z', 'high_z']
    bin_idx = 0
    for (low_z,high_z) in zip(z_bins, z_bins[1:]):
        z_bin = bin_labels[bin_idx]
        bin_idx+=1

        z_bin_mask_filename = write_mask(mask, low_z, high_z, mask_directory)

        try:
            radiomic_features[z_bin] = extractor.execute(image_filename, z_bin_mask_filename)
            radiomic_features[z_bin]['success'] = True
        except ValueError:
            print('ERROR PROCESSING ' + str(z_bin))
            radiomic_features[z_bin] = {'success' : False}

        radiomic_features[z_bin]['patient'] = patient_initials
        radiomic_features[z_bin]['mask'] = args.mask
        radiomic_features[z_bin]['z_bin'] = z_bin

    # For good measure, let's also calculate features for the full aorta
    z_bin = "full"
    bin_labels.append(z_bin)
    try:
        radiomic_features[z_bin] = extractor.execute(image_filename, mask_filename)
        radiomic_features[z_bin]['success'] = True
    except ValueError:
        print('ERROR PROCESSING ' + str(z_bin))
        radiomic_features[z_bin] = {'success' : False}

    radiomic_features[z_bin]['patient'] = patient_initials
    radiomic_features[z_bin]['mask'] = args.mask
    radiomic_features[z_bin]['z_bin'] = "full"

    # Clean up the dictionary
    radiomic_features = cleanup(radiomic_features)

    # Save features to csv
    # generate CSV filename and make output directory if it doesn't exist
    csv_filename = '_'.join([patient_initials, mask_name, 'radiomics.csv'])
    if args.output_directory is None:
        output_directory = os.path.join(args.directory, 'radiomics')
    else:
        output_directory = args.output_directory

    csv_filename = os.path.join(output_directory, csv_filename)

    if (not(os.path.exists(output_directory))):
        print('Creating directory ' + output_directory)
        os.mkdir(output_directory)

    # We need to get a list of the header names from one of the successful iterations
    # If non of the iterations were successful, warn user
    fieldnames=[]
    for z_bin in bin_labels:
        if radiomic_features[z_bin]['success'] == False:
            continue
        else:
            fieldnames = list(radiomic_features[z_bin].keys())
            break

    if len(fieldnames)>0:
        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()

            for z_bin in bin_labels:
                writer.writerow(radiomic_features[z_bin])
    else:
        print('Could not write csvs because `fieldnames` is empty.')
        print('Check to see if your mask is empty!')
