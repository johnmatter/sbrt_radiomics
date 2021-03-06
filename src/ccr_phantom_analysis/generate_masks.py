import os
import pickle
import argparse
import pydicom
import nrrd
import numpy as np
import itertools
from scipy import ndimage

from sys import exit
from file_utils import find_prefixed_file, find_dicom_directory, implay, find_prefixed_files

basic_mask_dicts = []

# materials=['050', '040', '030', '020', 'wood', 'rubber', 'dcork', 'acrylic', 'cork', 'resin']
materials=['020']
# materials=['cork_dense'] # needed for one set of mismatched label's in CCR1_T2's RTSTRUCT
for material in itertools.product(materials, range(0,16)):
    roi_name = '%s_%02d' % material
    mdict = {}
    mdict['NameStrings'] = [roi_name]
    if material == "cork":
        mdict['StartsWith'] = "cork"
    if material == "dcork":
        mdict['StartsWith'] = "dcork"
    basic_mask_dicts.append(mdict)

'''
Find the index for a given organ in the contours structure
Parameters:
	contours - The contours structure to look in
	dct - A dictionary descrbing the mask, such as basic_mask_dicts
Returns:
	The index of the matching contour in the structure
'''
def find_matching_contour_idx(contours, dct, exact_match=False):
    if exact_match:
        if len(dct['NameStrings'])>1:
            print('WARNING: multiple strings specified in dictionary with exact_match=True')
            print(dct)
        for i, nm in enumerate(contours['ROIName']):
            if nm.lower() == dct['NameStrings'][0]:
                return i
    else:
        for i, nm in enumerate(contours['ROIName']):
            lnm = nm.lower()
            found = True
            for j in dct['NameStrings']:
                # Check if the strings in the mask dictionary are found in
                # the name of this contour from RTSTRUCT
                if not j.lower() in lnm:
                    found = False
            if 'InvalidNStrings' in dct:
                for k in dct['InvalidNStrings']:
                    # Check if any of the 'invalid strings' are in
                    # this contour name
                    if k.lower() in lnm:
                        found = False
            if 'StartsWith' in dct:
                if not lnm.startswith(mdict['StartsWith']):
                    found = false
            if found:
                return i

    return -1

'''
Find the first CT frame in the z-direction
Parameters:
	ct_infos - A list of loaded CT dicom files
Returns:
	The index of the first CT slice in the z-direction
'''
def get_first_CT_frame(ct_infos):
	first = ct_infos[0]
	for i in ct_infos:
		if float(i.ImagePositionPatient[2]) < float(first.ImagePositionPatient[2]):
			first = i
	return first

'''
Print information about the mask structure
Parameters:
	mask - The mask structure to print information about
'''
def print_mask(mask):
	print('Organ %s' % (mask['Name']))
	for key in mask.keys():
		if isinstance(mask[key], np.ndarray) or key == 'Name':
			continue
		print('  %15s:\t%g' % (key, mask[key]))


'''
Write a mask in NRRD format
Parameters:
	mask - a mask dictinoary whose keys are Name and Mask
	directory - where to write the mask
'''
def write_mask(mask, directory):
	# Generate filename
	filename = os.path.join(directory, mask['Name']+'.nrrd')

	# Remove trouble characters from filename
	filename = filename.replace(' ', '_')
	filename = filename.replace('(', '')
	filename = filename.replace(')', '')

	print('Writing ' + filename)
	nrrd.write(filename, 1*mask['Mask'])

'''
Generate a masks structure given a set of contours and information about the dose files
Parameters:
	contours - The result from structure_loading.load_structures
	ct_info - Header information from a CT file
	mask_dicts - Information about which masks to include
		Entries in mask_dicts have the format:
			NameStrings - search for ROIs in contours which have these name strings (use lowercase)
Returns:
	masks - A set of dictionaries, each containing:
		Name: The name of the organ
		Mask: A boolean mask with the same dimensions as the dose files
'''
def mask_generation(
	contours,
	ct_infos,
	mask_dicts=basic_mask_dicts):

	masks = []
	other_organs_ind = -1
	used_voxels = None
	z = 0
	for i, dct in enumerate(mask_dicts):
		print('dct', dct['NameStrings'])

		contour_idx = find_matching_contour_idx(contours, dct, True)
		if contour_idx < 0:
			z += 1
			continue

		mdict = {}
		mdict['Name'] = contours['ROIName'][contour_idx]

		print('Creating mask for organ %s' % mdict['Name'])

		mdict['Mask'] = contours['Segmentation'][contour_idx]
		mdict['Mask'] = ndimage.rotate(mdict['Mask'], -90, reshape=False)
		mdict['Mask'] = np.fliplr(mdict['Mask'])

		masks.append(mdict)

        # # Keeping this for now, in case we want to make the "other organs" mask in the future
		# if masks[i-z]['CardiacOutput'] == -1:
			# other_organs_ind = i
		# else:
			# if used_voxels is None:
				# used_voxels = np.copy(masks[i-z]['Mask'])
			# else:
				# used_voxels = np.logical_or(used_voxels, masks[i-z]['Mask'])

    # Keeping this for now, in case we want to make the "other organs" mask in the future
	##Now remove duplicated voxels in other organs
	#if other_organs_ind != -1:
	#	masks[other_organs_ind]['Mask'] = np.logical_and(
	#		masks[other_organs_ind]['Mask'], np.logical_not(used_voxels))

	return masks

if __name__=='__main__':

	# Parse arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('directory', type=str, help='The patient directory to look in')
	parser.add_argument('--output', type=str, help='Output directory for masks')
	args = parser.parse_args()

	# Where are we writing the masks?
	if args.output is None:
		mask_directory = os.path.join(args.directory, 'masks')
	else:
		mask_directory = args.output

	# Load the contouss.pickle file generated by structure_loading.py
	with open(os.path.join(args.directory, 'contours.pickle'), 'rb') as infile:
		contours = pickle.load(infile)

	# Load CT info
	try:
		dcm_directory = find_dicom_directory(args.directory)
		ct_prefix = 'CT'
		ct_infos = [pydicom.dcmread(f) for f in find_prefixed_files(dcm_directory, ct_prefix)]
	except Exception as ex:
		print(type(ex), ex)
		print('Could not load ct info')
		exit(0)

	# Generate masks
	masks = mask_generation(contours, ct_infos, basic_mask_dicts)

	# I'm commenting this paragraph out for now, because we're low on space on Rivanna
	# and I'm not currently using the pickle files.
	# ---------
	# # Dump masks as pickle
	# with open(os.path.join(args.directory, 'masks_in_CT_dimensions.pickle'), 'wb') as outfile:
	# 	pickle.dump(masks, outfile)

	# Write masks as NRRD for pyradiomics
	if (not(os.path.exists(mask_directory))):
		print('Creating directory ' + mask_directory)
		os.mkdir(mask_directory)
	for mask in masks:
		write_mask(mask, mask_directory)
