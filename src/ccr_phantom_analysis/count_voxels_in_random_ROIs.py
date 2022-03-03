import os
import glob
import argparse
import numpy as np
import nrrd

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str, help='The patient directory to look in')
args = parser.parse_args()

counts = {}

for mask in glob.glob(os.path.join(args.directory, 'masks', '*random*nrrd')):
    print(mask)
    m,h=nrrd.read(mask)

    material = os.path.basename(mask).split('_')[0]
    if not material in counts.keys():
        counts[material] = []

    counts[material].append(m.sum())

print()
print('material,min,max,mean,std')
for material in counts:
    print('%s,%f,%f,%f,%f' %
          (material,
           np.min(counts[material]),
           np.max(counts[material]),
           np.mean(counts[material]),
           np.std(counts[material])))
