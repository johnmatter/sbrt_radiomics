#!/bin/bash
# Generate preprocessing slurm jobs for a patient
# USAGE: ./generate_preprocessing patient

patient=$1

patient_dir=${patient}
patient_str=${patient}
filename=preprocess_${patient_str}.slurm

cat ./preprocess_template_slurm.txt | \
sed -e "s/PATIENTSTR/${patient_str}/" \
    -e "s/PATIENTDIR/${patient_dir}/" \
    > $filename
