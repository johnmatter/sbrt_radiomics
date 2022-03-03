#!/bin/bash

# Copy first big set of patients
# KW uploaded this on Feb 26 2022
source_dir=/nv/vol141/phys_nrf/Krishni/Cardiac_pre_Aorta
patients=(BB1 BM CT DA DJ FL GB HD HR2 KS LC LD LK LL MB MK NJ OW PJ1 PJ2 SB SW WT)

for patient in ${patients[@]}; do

    echo $patient

    timepoint=Pre
    mkdir -p $patient/$timepoint/clinical
    ln -s ${source_dir}/$patient/CT*.dcm $patient/$timepoint/clinical/
    ln -s ${source_dir}/$patient/struct*.dcm $patient/$timepoint/clinical/

done


# Copy second set of patients
# These were uploaded over a long period and some complications.
# I haven't come up with an easy general way to handle them.
# Might be worth COMPLETELY rearranging the way the storage of raw DICOMs on rivanna

# BE
# (1.25mm vs 5mm scan is original cause of problem here)
mkdir -p BE/Pre/clinical
BE_dir=/nv/vol141/phys_nrf/Krishni/Cardiac_Pre_Post/BE/Pre_JM/scan2_slice_thickness_1_25mm
ln -s ${BE_dir}/CT*.dcm BE/Pre/clinical/
ln -s ${BE_dir}/struct*.dcm BE/Pre/clinical/

# HI
# structure sets were weird because of contour name mismatch and ALSO permissions problems here on rivanna
mkdir -p HI/Pre/clinical
HI_dir=/nv/vol141/phys_nrf/JohnMatter/patients/post_and_pre/HI_Modified/Pre
ln -s ${HI_dir}/CT*.dcm HI/Pre/clinical/
ln -s ${HI_dir}/struct*.dcm HI/Pre/clinical/

# FJ
mkdir -p FJ/Pre/clinical

FJ_dir=/nv/vol141/phys_nrf/Krishni/Cardiac_Pre_Post/FJ-MB/Pre/
ln -s ${FJ_dir}/CT*.dcm FJ/Pre/clinical/

FJ_struct=/nv/vol141/phys_nrf/Krishni/Cardiac_Pre_Post/FJ-MB/JM_new_StructureSets_FJ/struct_set_Pre_JM.dcm
ln -s ${FJ_struct} FJ/Pre/clinical

# MJ1
mkdir -p MJ1/Pre/clinical

MJ1_dir=/nv/vol141/phys_nrf/Krishni/Cardiac_Pre_Post/MJ1-MB/Pre/
ln -s ${MJ1_dir}/CT*.dcm MJ1/Pre/clinical/

MJ1_struct=/nv/vol141/phys_nrf/Krishni/Cardiac_Pre_Post/MJ1-MB/MJ1_New_STructureSet_Pre/struct_set_2021-10-25_13-33-02.dcm
ln -s ${MJ1_struct} MJ1/Pre/clinical
