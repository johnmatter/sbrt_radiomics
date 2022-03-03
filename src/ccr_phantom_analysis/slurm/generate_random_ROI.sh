#!/bin/bash
# Generate preprocessing slurm jobs for a patient
# USAGE: ./generate_preprocessing patient

patient=$1

patient_dir=\\/nv\\/vol141\\/phys_nrf\\/JohnMatter\\/ccr_phantom\\/data\\/${patient}
patient_str=${patient}

materials=()
materials+=(020)
materials+=(030)
materials+=(040)
materials+=(050)
materials+=(acrylic)
materials+=(cork)
materials+=(dcork)
materials+=(resin)
materials+=(rubber)
materials+=(wood)

for material in ${materials[@]}; do
    filename=${patient_str}_random_${material}_ROI.slurm

    mask_nrrd=$patient_dir\\/masks\\/${material}_00_through_15.nrrd

    cat ./random_ROI_template.txt | \
    sed -e "s/PATIENTSTR/${patient_str}/" \
        -e "s/PATIENTDIR/${patient_dir}/" \
        -e "s/MATERIALFILENAME/${mask_nrrd}/" \
        > $filename

done
