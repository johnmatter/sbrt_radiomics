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

def write_mask(dose, mask, dose_bin, dose_bin_label, directory):
    # Mask mask by dose
    lo_mask = np.ma.masked_where(dose > float(dose_bin[0]), dose).mask
    hi_mask = np.ma.masked_where(dose <= float(dose_bin[1]), dose).mask
    dose_mask = np.logical_and(lo_mask, hi_mask)
    new_mask = np.logical_and(dose_mask, mask)

    # Need to convert from bool to int for nrrd
    new_mask = new_mask * 1

    # Write mask to disk
    mask_filename = args.mask
    mask_splitext = os.path.splitext(mask_filename)
    output_filename = '%s_%s%s' % (mask_splitext[0], dose_bin_label, mask_splitext[1])
    output_filename = output_filename.replace(' ','_')

    binned_mask_directory=os.path.join(directory, 'binned_by_dose')
    if (not(os.path.exists(binned_mask_directory))):
        print('Creating directory ' + binned_mask_directory)
        os.mkdir(binned_mask_directory)

    output_filename = os.path.join(binned_mask_directory, output_filename)
    nrrd.write(output_filename, new_mask)
    print('Wrote ' + output_filename)

    return output_filename

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=str, help='The patient directory to look in')
    parser.add_argument('image', type=str, help='The patient CT to use (assumed to be in PATIENT/')
    parser.add_argument('mask', type=str, help='The name of the mask to use (assumed to be in PATIENT/masks/)')
    parser.add_argument('dose_bins', type=float, nargs='*', help='a list of dose bin edges')
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

    try:
        # Read dose
        dose_filename = os.path.join(args.directory, "dose_in_CT_dimensions.nrrd")
        dose, hdr = nrrd.read(dose_filename)
    except Exception as ex:
        print(type(ex), ex)
        print('Failed to load dose: ' + dose_filename)
        sys.exit(1)

    # Check if CT exists
    image_filename = os.path.join(args.directory, args.image)
    if not(os.path.exists(image_filename)):
        print('CT img does not exist')
        sys.exit(1)

    # Create feature extractor
    extractor = featureextractor.RadiomicsFeatureExtractor()

    # What dose values are we interested in?
    dose_bin_edges = args.dose_bins
    dose_bin_edges.append(np.inf)

    # Loop over dose bins, create a mask, and then calculate radiomic features for it
    radiomic_features = {}
    for dose_bin in zip(dose_bin_edges, dose_bin_edges[1:]):
        dose_bin_label = '%d to %d Gy' % dose_bin if np.isfinite(dose_bin).all() else '%d to inf Gy' % dose_bin[0]
        dose_mask_filename = write_mask(dose, mask, dose_bin, dose_bin_label, mask_directory)
        try:
            radiomic_features[dose_bin] = extractor.execute(image_filename, dose_mask_filename)
            radiomic_features[dose_bin]['success'] = True
        except ValueError:
            print('ERROR PROCESSING DOSE LIMIT ' + str(dose_bin))
            radiomic_features[dose_bin] = {'success' : False}

        radiomic_features[dose_bin]['patient'] = patient_initials
        radiomic_features[dose_bin]['mask'] = args.mask
        radiomic_features[dose_bin]['dose_bin'] = dose_bin_label


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
    for dose_bin in zip(dose_bin_edges, dose_bin_edges[1:]):
        if radiomic_features[dose_bin]['success'] == False:
            continue
        else:
            fieldnames = list(radiomic_features[dose_bin].keys())
            break

    if len(fieldnames)>0:
        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for dose_bin in zip(dose_bin_edges, dose_bin_edges[1:]):
                writer.writerow(radiomic_features[dose_bin])
    else:
        print('Could not write csvs because `fieldnames` is empty.')
        print('Check to see if your mask is empty!')
