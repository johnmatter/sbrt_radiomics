#!/bin/bash
# Generate radiomics slurm jobs for a patient
# USAGE: ./generate_radiomics.sh patient timepoint1 timepoint2 ...

patient=$1

# Loop over timepoints.
# The array $@ contains command line arguments,
# and :2 tells the loop to skip the first element.
for timepoint in "${@:2}"; do
    patient_dir=${patient}\\/${timepoint}
    patient_str=${patient}_${timepoint}
    filename=radiomics_${patient_str}.slurm

    cat ./radiomics_template_slurm.txt | \
    sed -e "s/PATIENTSTR/${patient_str}/" \
        -e "s/PATIENTDIR/${patient_dir}/" \
        > $filename
done
