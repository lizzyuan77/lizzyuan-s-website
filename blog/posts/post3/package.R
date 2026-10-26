# Run from this post folder after regenerating empirical results.
# Explicit allowlist: never archive raw CPS data or synthetic test outputs.
files <- c("index.qmd", "README.md", "DATA_REQUEST.md", "analysis.R",
 "test_analysis.R", "package.R", "draft.css",
 list.files("results", pattern="[.](csv|png|rds|txt)$", full.names=TRUE))
stopifnot(all(file.exists(files)), !any(grepl("test-output", files, fixed=TRUE)))
archive <- tempfile(fileext=".zip")
status <- zip(archive, files=files, flags="-q")
if(status != 0L || !file.exists(archive)) stop("Could not build research.zip; check zip on PATH.")
if(!file.copy(archive, "research.zip", overwrite=TRUE)) stop("Could not save research.zip.")
unlink(archive)
