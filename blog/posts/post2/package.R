# Explicit publishable file list: no private raw pages or recursive folder zipping.
files <- c("index.qmd", "README.md", "post.css", "sources.csv", "rules.csv",
 "analyze.R", "acquire.R", "run.R", "build-explorer.R", "package.R",
 "explorer-template.html", "explorer.html",
 list.files("data/evidence", pattern="[.]html$", full.names=TRUE),
 list.files("data/derived", pattern="[.]csv$", full.names=TRUE),
 list.files("results", pattern="[.](csv|png|txt)$", full.names=TRUE))
stopifnot(all(file.exists(files)), !any(grepl("private-raw", files, fixed=TRUE)))
archive <- tempfile(fileext=".zip")
status <- zip(archive, files=files, flags="-q")
if(status != 0L || !file.exists(archive)) stop("Could not build research.zip; check that zip is on PATH.")
if(!file.copy(archive, "research.zip", overwrite=TRUE)) stop("Could not save research.zip.")
unlink(archive)
