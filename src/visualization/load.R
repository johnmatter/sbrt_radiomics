# Load csvs
print("Loading")
d <- data.frame()
for(patient in patients) {
    for(timepoint in c("Pre", "Post1")) {
        csvs <- Sys.glob(paste(patient_dir,patient,timepoint,"radiomics","*.csv",sep="/"))
        for(csv in csvs) {
            dTemp <- read.csv(csv)

            # Timepoint isn't in the csv, so we append it for calculating changes
            dTemp$timepoint <- timepoint

            # This might seem trivial, but I needed to do it to compare 2 CT
            # scans for the SAME timepoint for the SAME patient with DIFFERENT
            # slice thicknesses.
            # I did this by giving the patient two different IDs (MB_thick,
            # MB_thin); the csv still had the duplicate ID
            dTemp$patient <- patient

            d <- rbind(d, dTemp)
        }
    }
}

# remove diagnostic columns; we're not interested in them
d <- d %>% select(-contains("diagnostics_"))

# tolower() all mask names; some patients have e.g. Heart.nrrd and others, heart.nrrd
# alsoo remove ".nrrd"
d$mask <- as.factor(tolower(sub(".nrrd","",d$mask)))

# limit to pulmonary structures of interest
masks_filter <- c("aorta", "aorta_-_shrink__1.00mm", "aorta_blood", "aorta_wall_jm")
d <- d %>% filter(mask %in% masks_filter)

# rename
d <- transform(d, mask=revalue(mask,c("aorta_-_shrink__1.00mm"="aorta_shrink_1mm")))

# get names of radiomic features
radiomic_features <- names(d)
radiomic_features <- radiomic_features[!radiomic_features %in% c("success", "patient", "mask", "timepoint", "dose_bin")]

# remove shape features from the list; we're not interested in them in terms of change
radiomic_features <- radiomic_features[-contains("shape",vars=radiomic_features)]

# Calculate absolute changes in radiomic features between the two time points.
# This is bit of a hack but it works.
print("Calculating deltas")
d_delta <- data.frame(patient=character(), mask=character(), dose_bin=character())
for(feature in radiomic_features) {
    print(paste("-- ",feature))
    eval_str <- "d_feature_delta <- d %>% group_by(patient, mask, dose_bin)"
    eval_str <- sprintf("%s %%>%% summarize(delta=%s[timepoint=='Post1']-%s[timepoint=='Pre'], .groups='keep')", eval_str, feature, feature)
    eval_str <- sprintf("%s %%>%% rename(%s=delta)", eval_str, feature)
    eval(parse(text=eval_str))

    d_delta <- d_delta %>% right_join(d_feature_delta, by=c("patient", "mask", "dose_bin"))
}

d_delta$dose_bin <- str_replace(d_delta$dose_bin, " to ", "–")

# Summarize volume of each mask in each dose bin
print("Summarizing volumes")
d_volume <- d %>% select(patient, mask, dose_bin, timepoint, success, original_shape_VoxelVolume)

d_volume_pre <- d_volume %>%
                filter(timepoint=="Pre") %>%
                select(-c(success, timepoint)) %>%
                rename(original_shape_VoxelVolume_Pre=original_shape_VoxelVolume)

d_volume_post <- d_volume %>%
                 filter(timepoint=="Post1") %>%
                 select(-c(success, timepoint)) %>%
                 rename(original_shape_VoxelVolume_Post1=original_shape_VoxelVolume)

d_volume <- d_volume_pre %>% right_join(d_volume_post,by=c("patient","mask","dose_bin"))

# now to figure out voxel sizes
d_voxel_size <- read.csv(paste0(patient_dir, "/slice_thickness.csv"))
d_voxel_size <- d_voxel_size %>% mutate(voxel_size=slice_thickness*pixel_spacing**2)

d_volume <- left_join(d_volume,
                      d_voxel_size %>% filter(timepoint=="Pre") %>% select(patient, voxel_size) %>% rename(voxel_size_Pre=voxel_size))
d_volume <- left_join(d_volume,
                      d_voxel_size %>% filter(timepoint=="Post1") %>% select(patient, voxel_size) %>% rename(voxel_size_Post1=voxel_size))

# calculate volume in cc
d_volume <- d_volume %>% rename(volume_in_voxels_Pre=original_shape_VoxelVolume_Pre)
d_volume <- d_volume %>% rename(volume_in_voxels_Post1=original_shape_VoxelVolume_Post1)

d_volume <- d_volume %>% mutate(volume_in_cc_Pre=volume_in_voxels_Pre * voxel_size_Pre / 1e3)
d_volume <- d_volume %>% mutate(volume_in_cc_Post1=volume_in_voxels_Post1 * voxel_size_Post1 / 1e3)

# calculate difference in volumes
d_volume <- d_volume %>% mutate(delta_cc = (volume_in_cc_Pre - volume_in_cc_Post1) / (volume_in_cc_Pre))
d_volume <- d_volume %>% mutate(delta_voxels = (volume_in_voxels_Pre - volume_in_voxels_Post1) / (volume_in_voxels_Pre))

write.csv(d_volume, paste0(output_dir, "/volume.csv"))
