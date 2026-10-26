# From the website root: Rscript blog/posts/post2/run.R
# Also works from another directory or from an extracted research bundle.
file_arg <- grep("^--file=", commandArgs(), value=TRUE)
if(length(file_arg) != 1L) stop("Run this script with Rscript.")
post_dir <- dirname(normalizePath(sub("^--file=", "", file_arg)))
setwd(post_dir)
if(length(commandArgs(trailingOnly=TRUE))) stop("Offline replay takes no arguments. For original cached HTML, see README.")
source("analyze.R", local=TRUE)
source("package.R", local=TRUE)
message("Offline replay complete: CSVs, figures, explorer, session information, and research.zip regenerated.")
