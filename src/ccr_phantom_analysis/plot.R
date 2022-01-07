date_str <- format(Sys.Date(), "%Y%m%d")
output_dir <- paste0("/Users/matter/Desktop/radiomics_", date_str)
if (!dir.exists(output_dir)) {
    print(paste0(output_dir, " does not exist."))
    user_response <- askYesNo("mkdir?")
    if (user_response) {
        dir.create(output_dir)
    } else {
        print("Proceed with caution.")
    }
}


# generate plots
plots <- hash()

feature_sets <- c("glcm", "gldm", "glrlm", "glszm", "ngtdm")
for(feature_set in feature_sets) {

    plots[[feature_set]] <- hash()

    feature_names <- radiomic_features[grepl(feature_set, radiomic_features)]
    for(feature in feature_names) {

        # this list contains 10 plots, one for each material
        plots[[feature_set]][[feature]] <- vector('list', length(unique(d$material)))

        j <- 1
        for (m in unique(d$material)) {
            p <- ggplot(d %>% filter(material==m),
                        aes_string(x="original_shape_VoxelVolume", y=feature)) +
                        geom_point(alpha=0.7) +
                        geom_line(alpha=0.7) +
                        theme_bw() +
                        theme(legend.position = "none",
                              axis.title.y = element_text(size = 8),
                              axis.text.x  = element_text(size = 8, angle = 60),
                              axis.title.x = element_text(size = 8)) +
                        ylab(feature) +
                        ggtitle(m)

            plots[[feature_set]][[feature]][[j]] <- p
            j <- j+1
        }

        # collect plots for this feature
        p <- annotate_figure(
             ggarrange(plotlist=plots[[feature_set]][[feature]],
                       nrow=3, ncol=4,
                       common.legend=TRUE, legend="bottom"),
             top = text_grob(paste(feature, "vs ROI volume [#voxels]"), face = "bold", size = 14)
             )

        # save PDF
        this_filename <- paste0(output_dir, "/", toupper(feature_set), "_", feature, ".pdf")
        ggsave(plot=p, filename=this_filename, width=14, height=10)
    }
}
