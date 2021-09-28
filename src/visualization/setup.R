# Set up relevant variables, mkdirs if necessary, etc

date_str <- format(Sys.Date(), "%Y%m%d")
output_dir <- paste0("/Users/matter/Desktop/radiomics_", date_str)
if (!dir.exists(output_dir)) {
    print(paste0(output_dir, " does not exist."))
    user_response <- askYesNo("mkdir?")
    if (user_response) {
        dir.create(output_dir)
    } else {
        print("Proceed with caution. Subsequent scripts assume this dir exists.")
    }
}

# Where do the radiomics data live?
patient_dir <- "/Volumes/ssd750/radiomics/patients/contrast"
patients <- c(
"BB1",
"BE",
# "CT",
"DA",
"DJ",
"FJ",
"GB",
"HD",
"HI",
"KS",
"LJ",
"LK",
"LL",
"MB",
"MJ1",
# "MK",
"PJ2",
# "PP",
"SB",
# "TC",
"WJ",
"WT"
)
