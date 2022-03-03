#!/bin/bash
# Generate radiomics slurm jobs for a patient
# USAGE: ./generate_radiomics.sh patient

patient=$1

patient_dir=${patient}
patient_str=${patient}
filename=radiomics_${patient_str}.slurm

cat ./radiomics_template_slurm.txt | \
sed -e "s/PATIENTSTR/${patient_str}/" \
    -e "s/PATIENTDIR/${patient_dir}/" \
    > $filename
