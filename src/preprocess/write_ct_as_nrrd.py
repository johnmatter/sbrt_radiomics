import argparse
import sys
import os

import numpy as np
import pydicom
import nrrd

from file_utils import find_dicom_directory, find_prefixed_files

'''
Loads a participant's 3D CT
Parameters:
    ct_info - a list of parsed 2D CT DICOM images
Returns:
    ct_img - the 3D CT image as an ndarray
'''
def load_ct(ct_info):
    # skip files with no SliceLocation (eg scout views)
    slices = []
    skipcount = 0
    for f in ct_info:
        if hasattr(f, 'SliceLocation') and (f.SOPClassUID=="1.2.840.10008.5.1.4.1.1.2"):
            slices.append(f)
        else:
            skipcount = skipcount + 1

    print("skipped, no SliceLocation or wrong SOPClassUID: {}".format(skipcount))

    # ensure they are in the correct order
    slices = sorted(slices, key=lambda s: s.SliceLocation)

    # pixel aspects, assuming all slices are the same
    ps = slices[0].PixelSpacing
    ss = slices[0].SliceThickness
    ax_aspect = ps[1]/ps[0]
    sag_aspect = ps[1]/ss
    cor_aspect = ss/ps[0]

    print('ax_aspect = %f/%f' % (ps[1], ps[0]))
    print('sag_aspect = %f/%f' % (ps[1], ss))
    print('cor_aspect = %f/%f' % (ss, ps[0]))

    # create 3D array
    img_shape = list(slices[0].pixel_array.shape)
    img_shape.append(len(slices))
    ct_img = np.zeros(img_shape)

    # fill 3D array with the images from the files
    for i, s in enumerate(slices):
        img2d = s.RescaleIntercept + s.RescaleSlope * s.pixel_array
        ct_img[:, :, i] = img2d

    return ct_img
'''
Write a participant's 3D CT in NRRD format
Parameters:
    ct_img - the 3D CT image as an ndarray
    directory - a list of parsed 2D CT DICOM images
'''
def write_ct(ct_img, directory):
    filename = os.path.join(directory, 'ct_img.nrrd')
    print('Writing ' + filename)
    nrrd.write(filename, ct_img)


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=str, help='The patient directory to look in')
    args = parser.parse_args()

    try:
        dcm_directory = find_dicom_directory(args.directory)
        ct_info = [pydicom.dcmread(f) for f in find_prefixed_files(dcm_directory, 'CT')]
        ct_img = load_ct(ct_info)
        write_ct(ct_img, args.directory)
    except Exception as ex:
        print(type(ex), ex)
        print('Could not write ct info')
        sys.exit(0)
