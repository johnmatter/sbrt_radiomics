import os
import nrrd
import argparse
import numpy as np
from pydicom import dcmread

from file_utils import find_prefixed_file, find_dicom_directory, find_prefixed_files, load_rtdose_files

'''
Reshape the dose grid to match the CT scan.
Parameters:
    dose - the dose grid returned by load_rtdose_files
Returns:
    dose_reshaped - the dose grid reshaped to (hopefully) match the CT
'''
def reshape_dose(dose):
    dose = np.sum(dose,0)
    print(dose.shape)

    # dose_reshaped = np.zeros((dose.shape[1], dose.shape[0], dose.shape[2]))

    # for n in range(dose.shape[2]):
    #         dose_reshaped[:,:,n] = dose[:,:,:]

    return dose

'''
Write the dose grid in NRRD format
Parameters:
    dose - the dose grid
    directory - where to write the NRRD
'''
def write_dose(dose, directory):
    filename = os.path.join(directory, 'dose_in_CT_dimensions.nrrd')
    print('Writing ' + filename)
    nrrd.write(filename, dose)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=str, help='The patient directory to look in')
    parser.add_argument('--dose_prefix', type=str, default='RTDOSE', help='optional prefix for dose dcm')
    parser.add_argument('--output', type=str, help='Output directory')
    args = parser.parse_args()

    # Where are we writing the dose?
    if args.output is None:
        dose_directory = args.directory
    else:
        dose_directory = args.output

    # Load
    try:
        dcm_directory = find_dicom_directory(args.directory)
        dose_grids = load_rtdose_files(find_prefixed_files(dcm_directory, args.dose_prefix))
    except Exception as ex:
        print(type(ex), ex)
        print('Could not load dose')
        exit(0)

    # Reshape dose to align with CT
    dose = reshape_dose(dose_grids)

    # Write to disk
    write_dose(dose, dose_directory)
