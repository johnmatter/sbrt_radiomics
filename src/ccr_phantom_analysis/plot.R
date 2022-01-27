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
        # For titles
        feature_name_pretty <- sub(paste0("original_",feature_set,"_"), "", feature)
        feature_set_pretty <- toupper(feature_set)

        # this list contains 10 plots, one for each material
        plots[[feature_set]][[feature]] <- vector('list', length(unique(d$material)))

        j <- 1
        for (m in unique(d$material)) {
            p <- ggplot(d %>% filter(material==m),
                        aes_string(x="original_shape_VoxelVolume",
                                   y=feature,
                                   color="scan")) +
                        # geom_point(alpha=0.7) +
                        geom_line(alpha=1.0, size=0.75) +
                        theme_dark() +
                        scale_color_carto_d(name = "Scan:", palette = "Pastel") +
                        theme(legend.position = "none",
                              axis.title.x = element_text(size = 8, color="white"),
                              axis.title.y = element_text(size = 8, color="white"),
                              axis.text.x  = element_text(size = 8, angle = 0, color="white"),
                              axis.text.y = element_text(size = 8, color="white"),
                              plot.title = element_text(color="white"),
                              legend.title = element_text(color="white"),
                              legend.text = element_text(color="white"),
                              legend.background = element_rect(fill = "#151515", color="#151515"),
                              plot.background = element_rect(fill = "#151515", color="#151515")) +

                        ylab(feature_name_pretty) +
                        xlab("Volume [voxels]") +
                        ggtitle(m)

            plots[[feature_set]][[feature]][[j]] <- p
            j <- j+1
        }

        # collect plots for this feature
        this_title <- paste(feature_set_pretty, feature_name_pretty, "vs ROI volume")
        p <- annotate_figure(
             ggarrange(plotlist=plots[[feature_set]][[feature]],
                       nrow=3, ncol=4,
                       common.legend=TRUE, legend="right"),
             top = text_grob(this_title, face = "bold", size = 14, color="white")
             )

        p2 <- cowplot::ggdraw(p) +
              theme(plot.background = element_rect(fill = "#151515"))

        # save PDF
        this_filename <- paste0(output_dir, "/", toupper(feature_set), "_", feature, ".pdf")
        ggsave(plot=p2, filename=this_filename, width=14, height=10)
    }
}
