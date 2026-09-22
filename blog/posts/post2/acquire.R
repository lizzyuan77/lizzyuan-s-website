# Optional refresh only. Review current terms BEFORE supplying explicit IDs.
# Never invoked by analyze.R or Quarto; preserves the published snapshot.
library(rvest)
ids<-commandArgs(trailingOnly=TRUE)
if(!length(ids)) stop('Review current terms/robots, then pass explicit museum IDs. See README.')
src<-read.csv('sources.csv',stringsAsFactors=FALSE)
allowed<-read.csv('rules.csv',stringsAsFactors=FALSE,encoding='UTF-8')$id
if(any(!ids %in% allowed)) stop('Only reviewed, included institutions are eligible; excluded sources are not retried.')
src<-src[src$id %in% ids,]
dir.create('private-raw',showWarnings=FALSE)
ua<-httr::user_agent('StudentMuseumBlog/1.0 (AI-assisted educational research)')
for(i in seq_len(nrow(src))) {
 s<-src[i,]; dest<-file.path('private-raw',paste0(s$id,'.html'))
 if(file.exists(dest)) {message(s$id,': cached; not requested');next}
 base<-sub('(https?://[^/]+).*','\\1',s$url)
 r<-httr::GET(paste0(base,'/robots.txt'),ua,httr::timeout(20))
 if(httr::status_code(r)!=200) stop(paste('Robots unavailable; review before proceeding:',s$id))
 rt<-strsplit(httr::content(r,as='text',encoding='UTF-8'),'\n')[[1]]
 writeLines(rt,file.path('private-raw',paste0(s$id,'-robots.txt')))
 # Conservative review: every Disallow rule is considered, even if for another bot.
 # Refuse the request if any rule matches the target path.
 paths<-trimws(sub('^[^:]+:','',rt[grepl('^Disallow:',rt,ignore.case=TRUE)]))
 target<-sub('https?://[^/]+','',s$url)
 for(path in paths[nzchar(paths)]) {
  fixed_prefix<-strsplit(path,'*',fixed=TRUE)[[1]][1]
  if(is.na(fixed_prefix)||!nzchar(fixed_prefix)||startsWith(target,fixed_prefix)) stop(paste('Potential robots exclusion; manual review required:',s$id,path))
 }
 delays<-suppressWarnings(as.numeric(trimws(sub('^[^:]+:','',rt[grepl('^Crawl-delay:',rt,ignore.case=TRUE)]))))
 Sys.sleep(max(c(10,delays),na.rm=TRUE))
 r<-httr::GET(s$url,ua,httr::timeout(25));httr::stop_for_status(r)
 writeBin(httr::content(r,as='raw'),dest)
 tx<-html_text2(html_element(read_html(dest),'body'))
 if(nchar(tx)<500) stop('Unexpected short/challenge page; stop and inspect, do not bypass.')
 message(s$id,': saved for manual content review; not automatically accepted into results')
}
