#!/bin/bash
# patients=(BE CT DA FJ HD HI LJ MB MJ1 MK PJ2 PP SB WJ LK TC KS LL DJ)
patients=(MB HI WT BB1 GB)

for patient in ${patients[@]}; do
    patient_dir=${patient}
    patient_str=${patient}
    filename=radiomics_${patient_str}.slurm

    cat ./radiomics_template_slurm.txt | \
    sed -e "s/PATIENTSTR/${patient_str}/" \
    sed -e "s/PATIENTDIR/${patient_dir}/" \
        > $filename
done
