#!/bin/bash

# This script rearranges the phantom data into a format that should work with
# the sbrt_radiomics repo.
# The original data are available at https://wiki.cancerimagingarchive.net/display/Public/Credence+Cartridge+Radiomics+Phantom+CT+Scans?preview=/24284300/25427982/labeled_ccr.jpg#242843000d1c0b53772a4fba8580e8b19f65069b

src_dir=/nv/vol141/phys_nrf/JohnMatter/ccr_phantom/CC-Radiomics-Phantom
dest_dir=/nv/vol141/phys_nrf/JohnMatter/ccr_phantom/data

scans=(CCR1_GE1 CCR1_GE2 CCR1_GE3 CCR1_GE4 CCR1_GE5 CCR1_GE6 CCR1_GE7 CCR1_P1 CCR1_P2 CCR1_P3 CCR1_P4 CCR1_P5 CCR1_S1 CCR1_S2 CCR1_T1 CCR1_T2 CCR1_T3)

# create directories
echo mkdiring
for scan in ${scans[@]}; do
    mkdir -p $dest_dir/$scan/clinical/ct
done

# link CT scans
echo linking CTs
ln -s $src_dir/'CCR1_GE1/07-11-2017-NA-NA-82396/2.000000-STD NI 21 A40-00349'/*dcm                                  $dest_dir/CCR1_GE1/clinical/ct
ln -s $src_dir/'CCR1_GE2/07-11-2017-NA-NA-66252/302.000000-FIRSTSCAN-72210'/*dcm                                    $dest_dir/CCR1_GE2/clinical/ct
ln -s $src_dir/'CCR1_GE3/07-11-2017-NA-NA-78045/2.000000-STD NI 23 A40-54190'/*dcm                                  $dest_dir/CCR1_GE3/clinical/ct
ln -s $src_dir/'CCR1_GE4/07-11-2017-NA-NA-97652/2.000000-FB-76897'/*dcm                                             $dest_dir/CCR1_GE4/clinical/ct
ln -s $src_dir/'CCR1_GE5/07-11-2017-NA-NA-57771/3.000000-NA-52025'/*dcm                                             $dest_dir/CCR1_GE5/clinical/ct
ln -s $src_dir/'CCR1_GE6/07-11-2017-NA-NA-55378/3.000000-PTC chest300ma-85714'/*dcm                                 $dest_dir/CCR1_GE6/clinical/ct
ln -s $src_dir/'CCR1_GE7/07-11-2017-NA-e1 ZZZ1969 CT5-46024/2.000000-STD NI 18 A40-46828'/*dcm                      $dest_dir/CCR1_GE7/clinical/ct
ln -s $src_dir/'CCR1_P1/07-11-2017-NA-NA-67468/6.000000-standard-88421'/*dcm                                        $dest_dir/CCR1_P1/clinical/ct
ln -s $src_dir/'CCR1_P2/07-11-2017-NA-NA-58168/3.000000-NA-63386'/*dcm                                              $dest_dir/CCR1_P2/clinical/ct
ln -s $src_dir/'CCR1_P3/07-11-2017-NA-NA-44787/6.000000-HELIX 16X0.75-16932'/*dcm                                   $dest_dir/CCR1_P3/clinical/ct
ln -s $src_dir/'CCR1_P4/07-11-2017-NA-NA-97757/7.000000-Helix 16x1.5-11900'/*dcm                                    $dest_dir/CCR1_P4/clinical/ct
ln -s $src_dir/'CCR1_P5/07-11-2017-NA-NA-93203/4.000000-HighResDRR-56473'/*dcm                                      $dest_dir/CCR1_P5/clinical/ct
ln -s $src_dir/'CCR1_S1/07-11-2017-NA-RTRTThorax Adult-61245/2.000000-Thorax  3.0  B31s-51256'/*dcm                 $dest_dir/CCR1_S1/clinical/ct
ln -s $src_dir/'CCR1_S2/07-11-2017-NA-ThoraxCHESTWOROUTINE Adult-67881/4.000000-LUNG WITH  2.0  I70f  2-67136'/*dcm $dest_dir/CCR1_S2/clinical/ct
ln -s $src_dir/'CCR1_T1/07-11-2017-NA-NA-88872/2.000000-Body 3.0-92976'/*dcm                                        $dest_dir/CCR1_T1/clinical/ct
ln -s $src_dir/'CCR1_T2/07-11-2017-NA-NA-91346/7.000000-Lung 3.0-39251'/*dcm                                        $dest_dir/CCR1_T2/clinical/ct
ln -s $src_dir/'CCR1_T3/07-11-2017-NA-NA-52454/3.000000-Chest 3.0   Axial-47952'/*dcm                               $dest_dir/CCR1_T3/clinical/ct

# rename CT scan files to have 'CT' prefix to satisfy sbrt_radiomics code
echo renaming CTs
for scan in ${scans[@]}; do
    scan_dir=$dest_dir/$scan/clinical
    for slice in $(ls $scan_dir/ct); do
        mv $scan_dir/ct/$slice $scan_dir/CT-$slice
    done
    rmdir $scan_dir/ct
done

# link RTSTRUCTs
echo linking RTSTRUCTs
ln -s $src_dir/CCR1_GE1/07-11-2017-NA-PROSTATEEMPTYAKL-82396/1.000000-NA-69900/1-1.dcm $dest_dir/CCR1_GE1/clinical/rtstruct.dcm
ln -s $src_dir/CCR1_GE2/07-11-2017-NA-PROSTATEEMPTYAKL-66252/1.000000-NA-55367/1-1.dcm $dest_dir/CCR1_GE2/clinical/rtstruct.dcm
ln -s $src_dir/CCR1_GE3/07-11-2017-NA-PROSTATEEMPTYAKL-78045/1.000000-NA-38928/1-1.dcm $dest_dir/CCR1_GE3/clinical/rtstruct.dcm
ln -s $src_dir/CCR1_GE4/07-11-2017-NA-PROSTATEEMPTYAKL-97652/1.000000-NA-18765/1-1.dcm $dest_dir/CCR1_GE4/clinical/rtstruct.dcm
ln -s $src_dir/CCR1_GE5/07-11-2017-NA-PROSTATEEMPTYAKL-57771/1.000000-NA-28012/1-1.dcm $dest_dir/CCR1_GE5/clinical/rtstruct.dcm
ln -s $src_dir/CCR1_GE6/07-11-2017-NA-PROSTATEEMPTYAKL-55378/1.000000-NA-79406/1-1.dcm $dest_dir/CCR1_GE6/clinical/rtstruct.dcm
ln -s $src_dir/CCR1_GE7/07-11-2017-NA-PROSTATEEMPTYAKL-46024/1.000000-NA-72920/1-1.dcm $dest_dir/CCR1_GE7/clinical/rtstruct.dcm
ln -s $src_dir/CCR1_P1/07-11-2017-NA-PROSTATEEMPTYAKL-67468/1.000000-NA-22945/1-1.dcm  $dest_dir/CCR1_P1/clinical/rtstruct.dcm
ln -s $src_dir/CCR1_P2/07-11-2017-NA-PROSTATEEMPTYAKL-58168/1.000000-NA-79338/1-1.dcm  $dest_dir/CCR1_P2/clinical/rtstruct.dcm
ln -s $src_dir/CCR1_P3/07-11-2017-NA-PROSTATEEMPTYAKL-44787/1.000000-NA-42770/1-1.dcm  $dest_dir/CCR1_P3/clinical/rtstruct.dcm
ln -s $src_dir/CCR1_P4/07-11-2017-NA-PROSTATEEMPTYAKL-97757/1.000000-NA-91258/1-1.dcm  $dest_dir/CCR1_P4/clinical/rtstruct.dcm
ln -s $src_dir/CCR1_P5/07-11-2017-NA-PROSTATEEMPTYAKL-93203/1.000000-NA-12537/1-1.dcm  $dest_dir/CCR1_P5/clinical/rtstruct.dcm
ln -s $src_dir/CCR1_S1/07-11-2017-NA-PROSTATEEMPTYAKL-61245/1.000000-NA-88237/1-1.dcm  $dest_dir/CCR1_S1/clinical/rtstruct.dcm
ln -s $src_dir/CCR1_S2/07-11-2017-NA-PROSTATEEMPTYAKL-67881/1.000000-NA-61866/1-1.dcm  $dest_dir/CCR1_S2/clinical/rtstruct.dcm
ln -s $src_dir/CCR1_T1/07-11-2017-NA-PROSTATEEMPTYAKL-88872/1.000000-NA-85473/1-1.dcm  $dest_dir/CCR1_T1/clinical/rtstruct.dcm
ln -s $src_dir/CCR1_T2/07-11-2017-NA-PROSTATEEMPTYAKL-91346/1.000000-NA-96506/1-1.dcm  $dest_dir/CCR1_T2/clinical/rtstruct.dcm
ln -s $src_dir/CCR1_T3/07-11-2017-NA-PROSTATEEMPTYAKL-52454/1.000000-NA-88812/1-1.dcm  $dest_dir/CCR1_T3/clinical/rtstruct.dcm
