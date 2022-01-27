import os
import argparse
import nrrd
import random
import numpy as np

def generate_cube(mask, limits):

    # Generate size of the cube
    # I assume the z-direction is the narrowest, and sets the limit for the
    # size of a cube.
    # I also impose a lower bound on the size of a cube: 2x2x2 voxels
    side_length = random.randint(2,limits[2][1]-limits[2][0])

    # Pick a location for the corner
    x0 = random.randint(limits[0][0], limits[0][1] - side_length)
    y0 = random.randint(limits[1][0], limits[1][1] - side_length)
    z0 = random.randint(limits[2][0], limits[2][1] - side_length)

    # Initialize an empty roi with mask's dimensions
    roi = np.zeros(mask.shape)

    roi[x0:(x0+side_length),
        y0:(y0+side_length),
        z0:(z0+side_length)] = 1

    return roi

def generate_slab(mask, limits):

    # Pick boundaries for the cube
    bounds = [(),(),()]
    for n in range(3):
        # Generate two numbers within limits, using lesser for the lower limit
        # Note: randint is inclusive
        lo = random.randint(limits[n][0], limits[n][1])
        hi = random.randint(limits[n][0], limits[n][1])
        bounds[n] = (min(lo,hi), max(lo,hi))

    # Initialize an empty roi with mask's dimensions
    roi = np.zeros(mask.shape)

    roi[bounds[0][0]:bounds[0][1]+1,
        bounds[1][0]:bounds[1][1]+1,
        bounds[2][0]:bounds[2][1]+1] = 1

    return roi

if __name__=='__main__':
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('n_rois', type=int, help='Number of masks to generate')
    parser.add_argument('shape', type=str, choices=['cube', 'slab'], help='Shape to generate')
    parser.add_argument('mask', type=str, help='Mask defining the area in which to generate random ROIs')
    parser.add_argument('output', type=str, help='Where the generated masks will be saved')
    args = parser.parse_args()

    # read mask
    mask, header = nrrd.read(args.mask)

    # generate masks and write them to disk

    # First, find bounds of the mask.
    # I assume the mask is a rectangular prism, which is true for the CCR
    # phantom dataset.
    limits = []

    # x direction
    for n in range(mask.shape[0]):
        if mask[n,:,:].any():
            lo = n
            break

    for n in range(mask.shape[0]-1,-1,-1):
        if mask[n,:,:].any():
            hi = n
            break

    limits.append((lo,hi))

    # y direction
    for n in range(mask.shape[1]):
        if mask[:,n,:].any():
            lo = n
            break

    for n in range(mask.shape[1]-1,-1,-1):
        if mask[:,n,:].any():
            hi = n
            break

    limits.append((lo,hi))

    # z direction
    for n in range(mask.shape[2]):
        if mask[:,:,n].any():
            lo = n
            break

    for n in range(mask.shape[2]-1,-1,-1):
        if mask[:,:,n].any():
            hi = n
            break

    limits.append((lo,hi))

    # generate cubes
    mask_basename = os.path.basename(args.mask).replace(".nrrd","")

    for n in range(args.n_rois):

        if args.shape == 'cube':
            mask_filename_format = os.path.join(args.output, '%s_random_cube_%%d.nrrd' % mask_basename)
            roi = generate_cube(mask, limits)

        elif args.shape == 'slab':
            mask_filename_format = os.path.join(args.output, '%s_random_slab_%%d.nrrd' % mask_basename)
            roi = generate_slab(mask, limits)


        filename = mask_filename_format % n
        print('Writing ' + filename)
        print('Volume = %d voxels' % int(roi.sum()))
        print()
        nrrd.write(filename, roi)
