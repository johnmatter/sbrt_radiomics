top_dir <- "/Volumes/ssd750/radiomics/CCR_phantom/radiomics/data"

scans <- c("CCR1_GE1",
           "CCR1_GE2",
           "CCR1_GE3",
           "CCR1_GE4",
           "CCR1_GE5",
           "CCR1_GE6",
           "CCR1_GE7",
           "CCR1_P1",
           "CCR1_P2",
           "CCR1_P3",
           "CCR1_P4",
           "CCR1_P5",
           "CCR1_S1")
           # "CCR1_S2", # failed radiomics calculation 20200113
           # "CCR1_T1", # failed radiomics calculation 20200113
           # "CCR1_T2", # failed radiomics calculation 20200113
           # "CCR1_T3) # failed radiomics calculation 20200113

# Load csvs
print("Loading")
d <- data.frame()
for(scan in scans) {
    print(paste(scan,'------'))
    csvs <- Sys.glob(paste(top_dir,scan,"radiomics","*.csv",sep="/"))
    for(csv in csvs) {
        cat('.')
        d <- rbind(d, read.csv(csv, header=TRUE))
    }
    print('')
}

# get names of radiomic features
radiomic_features <- names(d)[grepl("^original_.*", names(d))]

# get mask names
d$mask <- str_replace(basename(d$Mask), ".nrrd", "")

# get scan names
d$scan <- sub("CCR1_", "", basename(dirname(dirname(d$Mask))))

# get material
d$material <- gsub("_.*", "", d$mask)
