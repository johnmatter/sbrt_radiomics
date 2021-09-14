# sbrt_radiomics
This is a set of scripts used to process DICOM CT scans, RTSTRUCT, and RTDOSE
files for a project aimed at using
[radiomics](https://pubmed.ncbi.nlm.nih.gov/33431509/) to improve
[SBRT](https://www.mayoclinic.org/tests-procedures/sbrt/pyc-20446794) treatment
protocols for lung cancer.

## How to set things up on rivanna
1. [Connect](https://www.rc.virginia.edu/userinfo/rivanna/login/) to [rivanna](https://www.rc.virginia.edu/userinfo/rivanna/overview/)
2. Clone this repo somewhere (e.g. /nv/vol141/phys_nrf/JohnMatter/sbrt_radiomics)
3. Create a python virtual environment by running the following commands in the directory above your cloned repo
  1. python -m venv sbrt_radiomics_env
  2. source sbrt_radiomics_env/src/activate
  3. pip install numpy matplotlib pandas pydicom pynrrd pyradiomics scipy SimpleITK

You will have to source the activate script every time you (or a SLURM job) want to run these scripts.

## Basic overview
The `src` directory contains two subdirectories: `preprocess` and `radiomics`.
For each patient in the dataset, their DICOM files must be preprocessed to
prepare them for input to pyradiomics.
The `preprocess.sh` script preprocesses the data and the `radiomics.sh` script
calculates radiomic features for the output of `preprocess.sh`.
Both scripts run python scripts for the desired patient, but the user should
only have to peep into the inner workings of the python scripts if things go
really awry—I believe all the kinks have been worked out.

## Input and output
Your data should live in a directory somewhere that *isn't* your home directory
and ideally is not in your cloned version of this repo.
You should create a symbolic link to your data directory in the top directory
of this repo (e.g. `ln -s /nv/vol141/phys_nrf/JohnMatter/patients/dataset1 data`).
**The scripts all assume this link exists!**

The data should be organized as shown in the mock directory tree below this paragraph.
These patients have data from two time points, Pre and Post1.
MB is an example of a new unprocessed patient, and only has DICOM files.
LJ is an example of a fully processed patient, and has additional directories,
NRRD files, and CSVs—these are all generated by the python scripts.

```
/nv/vol141/phys_nrf/JohnMatter/patients/post_and_pre/
├── WJ/
│   ├── Pre/
│   │   ├── clinical/
│   │   │   ├── struct_set.dcm
│   │   │   ├── RTDOSE1.2.276.0.7230010.3.1.4.1602247082.16596.1613672697.92.dcm
│   │   │   ├── CT1.2.840.113704.7.1.0.106249620020632.1607274627.1060.dcm
│   │   │   ├── CT1.2.840.113704.7.1.0.106249620020632.1607274627.1061.dcm
│   │   │   ├── CT1.2.840.113704.7.1.0.106249620020632.1607274627.1062.dcm
│   │   │   ├── ...
│   ├── Post1/
│   │   ├── clinical/
│   │   │   ├── struct_set.dcm
│   │   │   ├── RTDOSE1.2.276.0.7230010.3.1.4.1602247082.16596.1613672697.92.dcm
│   │   │   ├── CT1.2.840.113704.7.1.0.106249620020632.1607274627.1060.dcm
│   │   │   ├── CT1.2.840.113704.7.1.0.106249620020632.1607274627.1061.dcm
│   │   │   ├── CT1.2.840.113704.7.1.0.106249620020632.1607274627.1062.dcm
│   │   │   ├── ...
├── MB/
│   ├── Pre/
│   ├── Post1/
├── HI/
│   ├── Pre/
│   ├── Post1/
├── LJ/
│   ├── Pre/
│   │   ├── ct_img.nrrd
│   │   ├── dose_in_CT_dimensions.nrrd
│   │   ├── contours.pickle
│   │   ├── clinical/
│   │   │   ├── struct_set.dcm
│   │   │   ├── RTDOSE1.2.276.0.7230010.3.1.4.1602247082.16596.1613672697.92.dcm
│   │   │   ├── CT1.2.840.113704.7.1.0.106249620020632.1607274627.1060.dcm
│   │   │   ├── CT1.2.840.113704.7.1.0.106249620020632.1607274627.1061.dcm
│   │   │   ├── CT1.2.840.113704.7.1.0.106249620020632.1607274627.1062.dcm
│   │   │   ├── ...
│   │   ├── masks/
│   │   │   ├── Aorta.nrrd
│   │   │   ├── Heart.nrrd
│   │   │   ├── ...
│   │   ├── radiomics/
│   │   │   ├── LJ_Aorta_radiomics.csv
│   │   │   ├── LJ_Heart_radiomics.csv
│   │   │   ├── ...
│   ├── Post1/
│   │   ├── ct_img.nrrd
│   │   ├── dose_in_CT_dimensions.nrrd
│   │   ├── contours.pickle
│   │   ├── clinical/
│   │   │   ├── struct_set.dcm
│   │   │   ├── RTDOSE1.2.276.0.7230010.3.1.4.1602247082.16596.1613671945.83.dcm
│   │   │   ├── CT1.2.840.113704.7.1.0.106249620020632.1607274491.766.dcm
│   │   │   ├── CT1.2.840.113704.7.1.0.106249620020632.1607274491.767.dcm
│   │   │   ├── CT1.2.840.113704.7.1.0.106249620020632.1607274491.768.dcm
│   │   │   ├── ...
│   │   ├── masks/
│   │   │   ├── Aorta.nrrd
│   │   │   ├── Heart.nrrd
│   │   │   ├── ...
│   │   ├── radiomics/
│   │   │   ├── LJ_Aorta_radiomics.csv
│   │   │   ├── LJ_Heart_radiomics.csv
│   │   │   ├── ...
```

## Todo
* I've been using [SLURM](https://www.rc.virginia.edu/userinfo/rivanna/slurm/)
  to efficiently process multiple patients and timepoints.
  I have a bash script that generates SLURM job files for all patients.
  It will be committed soon.
* I've been using R to plot/analze the processed data.
  I'll either commit that code or rewrite it in python.
* I wrote a rudimentary image viewing script using matplotlib.
  I use it after preprocessing and before calculating radiomic features as a
  safety check to make sure everything is still running smoothly.
