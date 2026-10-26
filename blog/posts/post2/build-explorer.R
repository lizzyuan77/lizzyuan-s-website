# Build the complete interactive table from the analysis data, never copied prices.
# analyze.R supplies d in the same evaluation environment.
stopifnot(exists("d"), nrow(d) == 18)
html_escape <- function(x) {
 x <- gsub("&", "&amp;", as.character(x), fixed=TRUE)
 x <- gsub("<", "&lt;", x, fixed=TRUE)
 x <- gsub(">", "&gt;", x, fixed=TRUE)
 gsub('"', "&quot;", x, fixed=TRUE)
}
rows <- vapply(seq_len(nrow(d)), function(i) {
 z <- d[i,]
 sprintf(paste0('<tr data-city="%s" data-adult="%s" data-student="%s" ',
  'data-adult22="%s" data-student22="%s"><td><a href="%s">%s</a>',
  '<small>%s · %s</small></td><td class="price adult">$%.2f</td>',
  '<td class="price student">$%.2f</td><td class="price saving">$%.2f</td>',
  '<td>%s<small>%s</small></td></tr>'),
  html_escape(z$city), z$adult, z$student, z$adult22, z$student22,
  html_escape(z$url), html_escape(z$museum), html_escape(z$city),
  html_escape(z$price_type), z$adult, z$student, z$saving,
  html_escape(z$conditions), html_escape(z$hours_note))
}, character(1))
template <- paste(readLines("explorer-template.html", warn=FALSE, encoding="UTF-8"), collapse="\n")
stopifnot(length(gregexpr("__ROWS__", template, fixed=TRUE)[[1]]) == 1L,
          grepl("__ROWS__", template, fixed=TRUE))
writeLines(sub("__ROWS__", paste(rows, collapse=""), template, fixed=TRUE), "explorer.html", useBytes=TRUE)
