import numpy as np
import nrrd
import argparse

# Motivation: KW wanted to know how MJ1's lower dose bins would look if divided
# into bins with equal statistics. This requires finding e.g. the deciles in
# dose at each timepoint.

parser = argparse.ArgumentParser()
parser.add_argument('dose', type=str, help='The filename of the RTDOSE to partition')
parser.add_argument('mask', type=str, help='The filename of the mask to use')
parser.add_argument('bins', type=int, help='Number of bins to use')
parser.add_argument('min', type=float, help='min value of the range to bin')
parser.add_argument('max', type=float, help='max value of the range to bin')
args = parser.parse_args()

# Load dose
dose, header = nrrd.read(args.dose)
mask, header = nrrd.read(args.mask)

# Limit dose to mask
mask = np.where(mask==1, dose, np.nan)
mask_flattened = np.logical_not(np.isnan(mask.flatten()))

# Flatten dose
dose_flattened = dose.flatten()
dose = dose_flattened[mask_flattened]

# Limit the dose to the specified range
dose_in_range_idx = np.logical_and(args.min<=dose, dose<=args.max)
dose = dose[dose_in_range_idx]

# The outer bin edges will be the user-specified values
bin_edges = np.array([args.min, args.max])

# The inner edges will be the n/N percentiles, where n=1,2,...,N-1
# and N = args.bin
percentiles = [100*n/args.bins for n in range(1,args.bins)]
percentile_bins = np.percentile(dose, percentiles)

# Combine the two arrays and sort them
bin_edges = np.concatenate((bin_edges,  percentile_bins))
bin_edges = np.sort(bin_edges)

# Print to the screen for use with the radiomics script
print(*bin_edges)
