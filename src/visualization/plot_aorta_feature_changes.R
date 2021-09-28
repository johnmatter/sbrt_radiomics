feature_sets <- c("glcm", "gldm", "glrlm", "glszm", "ngtdm")

# limit to aorta
masks_filter <- c("aorta", "aorta_shrink_1mm", "aorta_blood", "aorta_wall_jm")
d <- d %>% filter(mask %in% masks_filter)

# shapes to use
shape_values <- c("aorta"=16,
                  "aorta_shrink_1mm"=10,
                  "aorta_blood"=8,
                  "aorta_wall_jm"=1)

# Print legend
p <- ggplot(d_delta %>% filter(mask!="aorta"),
            aes_string(x="dose_bin", y="original_firstorder_Mean", color="patient", shape="mask")) +
            geom_point(alpha=0.7) +
            theme_bw() +
            scale_shape_manual(values=shape_values)
l <- cowplot::get_legend(p)
pdf(file=paste0(output_dir,"/legend.pdf"))
grid.newpage()
grid.draw(l)
dev.off()

# generate plots
plots <- hash()

for (m in masks_filter) {

    # Create a hash table
    plots[[m]] <- hash()

    for(feature_set in feature_sets) {
        feature_names <- radiomic_features[grepl(feature_set, radiomic_features)]

        print(paste(m, feature_set))

        plots[[m]][[feature_set]] <- vector('list', length(feature_names)+1)

        for(i in seq_along(feature_names)) {

            this_mean <- mean((d %>% filter(timepoint=="Pre", mask==m) %>%
                                     select(feature_names[i]))[,feature_names[i]],
                              na.rm=T)

            p <- ggplot(d_delta %>% filter(mask==m),
                        aes_string(x="dose_bin", y=feature_names[[i]], color="patient", shape="m", group="patient")) +
                        geom_point(alpha=0.7) + #, position=position_jitter(width=0.1)) +
                        geom_line(alpha=0.7) +
                        theme_bw() +
                        scale_shape_manual(values=shape_values) +
                        theme(legend.position = "none",
                              axis.title.y = element_text(size = 6),
                              axis.text.x  = element_text(angle=60,size=6),
                              axis.title.x = element_blank()) +
                        ylab(sub(paste("original",feature_set,"",sep="_"), "", feature_names[[i]])) +
                        ggtitle(paste0("Pre mean = ", signif(this_mean,3)))

            plots[[m]][[feature_set]][[i]] <- p
        }
        plots[[m]][[feature_set]][[i+1]] <- l
    }
}


#Print each matrix's features together as one PDF
for (mask in masks_filter) {
    for(feature_set in feature_sets) {
        this_title    <- paste("Changes (Post1-Pre) for", toupper(feature_set), "features")
        this_filename <- paste0(output_dir, "/", mask, "_", toupper(feature_set), ".pdf")
        p <- annotate_figure(
             ggarrange(plotlist=plots[[mask]][[feature_set]],
                       nrow=5, ncol=5,
                       common.legend=TRUE, legend="bottom"),
             top = text_grob(this_title, face = "bold", size = 14)
             )
        ggsave(plot=p, filename=this_filename, width=14, height=10)
    }
}
