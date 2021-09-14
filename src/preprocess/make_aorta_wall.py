import numpy as np
import argparse
import os
import nrrd


parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str, help='full path location of masks directory')
parser.add_argument('--aorta', type=str, help='name of aorta mask')
parser.add_argument('--blood', type=str, help='name of blood mask')
args = parser.parse_args()


aorta_filename = os.path.join(args.directory, args.aorta)
blood_filename = os.path.join(args.directory, args.blood)

aorta, aorta_header = nrrd.read(aorta_filename)
blood, blood_header = nrrd.read(blood_filename)

wall = 1*np.logical_and(aorta, np.logical_not(np.logical_and(aorta,blood)))

wall_filename = os.path.join(args.directory, "Aorta_wall_JM.nrrd")
nrrd.write(wall_filename, wall)
