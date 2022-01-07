top_dir <- "/Volumes/ssd750/radiomics/CCR_phantom/radiomics/data"

scans <- c("CCR1_GE1")

# Load csvs
print("Loading")
d <- data.frame()
for(scan in scans) {
    csvs <- Sys.glob(paste(top_dir,scan,"radiomics","*.csv",sep="/"))
    for(csv in csvs) {
        d <- rbind(d, read.csv(csv))
    }
}

# get names of radiomic features
radiomic_features <- names(d)[grepl("^original_.*", names(d))]

# get mask names
d$mask <- str_replace(basename(d$Mask), ".nrrd", "")

# get material
d$material <- gsub("_.*", "", d$mask)
