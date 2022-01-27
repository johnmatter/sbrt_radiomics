import os
import gc
import argparse
import nrrd
import numpy as np
import itertools

'''
Combine a list of ROIs by OR-ing them together.
Parameters:
    cubes - a list of ndarrays whose entries are 1s and 0s
Returns:
    combined_cubes - the OR of the ROIs in 'cubes'
'''
def combine_cubes(cubes):
    # Initialize the array to be returned
    combined_cubes = np.zeros(cubes[0].shape)

    # Combine cubes by OR-ing them together
    for cube in cubes:
        combined_cubes = np.logical_or(combined_cubes, cube)

    # Convert bools to 1s and 0s
    combined_cubes = combined_cubes * 1

    return combined_cubes

if __name__=='__main__':

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=str, help='The patient directory to look in')
    args = parser.parse_args()

    # Where are the masks?
    mask_directory = os.path.join(args.directory, 'masks')

    # Materials in the CCR phantom
    materials=['050', '040', '030', '020', 'wood', 'rubber', 'acrylic', 'cork', 'resin', 'dcork', 'cork_dense']

    # This will contain a list of tuples, each containing (a mask, and its filename)
    masks = []

    # Loop over materials to generate masks
    for material in materials:
        print('Combining cubes for ' + material)

        # cubes contains the ndarrays
        cubes = []

        # Loop over cubes, adding them to the list one at a time
        for n in range(0,16):
            # ROI filenames look like dcork_04.nrrd
            roi_name = '%s_%02d.nrrd' % (material, n)
            roi_fullpath = os.path.join(mask_directory, roi_name)

            # Read the file
            try:
                mask, header = nrrd.read(roi_fullpath)
            except:
                print('!!! WARNING: Could not load %s' % roi_fullpath)
                continue

            # Add the mask to cubes
            cubes.append(mask)

            # Get the combination of the cubes
            mask = combine_cubes(cubes)

            # Write mask to disk
            mask_name = '%s_00_through_%02d.nrrd' % (material, n)

            filename = os.path.join(mask_directory, mask_name)
            print('Writing ' + filename)
            nrrd.write(filename, mask)

        # Garbage collection
        for cube in cubes:
            del cube
        if 'mask' in locals():
            del mask
        if 'cubes' in locals():
            del cubes
        gc.collect()
