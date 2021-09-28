#!/bin/bash
# patients=(BE CT DA FJ HD HI LJ MB MJ1 MK PJ2 PP SB WJ LK TC KS LL DJ)
# patients=(MB HI WT BB1 GB)
patients=(LJ)
timepoints=(Pre Post1)

for patient in ${patients[@]}; do
    for timepoint in ${timepoints[@]}; do
        patient_dir=${patient}\\/${timepoint}
        patient_str=${patient}_${timepoint}
        filename=preprocess_${patient_str}.slurm

        cat ./preprocess_template_slurm.txt | \
        sed -e "s/PATIENTSTR/${patient_str}/" \
            -e "s/PATIENTDIR/${patient_dir}/" \
            > $filename

    done
done
