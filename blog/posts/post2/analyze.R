# Run from this directory. Default: offline replay of short factual evidence.
# --raw PATH reads original cached pages and regenerates evidence; no network.
if(.Platform$OS.type=='windows') Sys.setlocale('LC_CTYPE','English_United States.utf8')
library(rvest)
library(ggplot2)
args <- commandArgs(trailingOnly=TRUE)
raw_dir <- if(length(args)==2 && args[1]=='--raw') args[2] else NULL
src <- read.csv('sources.csv',stringsAsFactors=FALSE)
rules <- read.csv('rules.csv',stringsAsFactors=FALSE,encoding='UTF-8')
stopifnot(nrow(rules)==18)
dir.create('data/evidence',recursive=TRUE,showWarnings=FALSE)
dir.create('data/derived',recursive=TRUE,showWarnings=FALSE)
dir.create('results',showWarnings=FALSE)
matched <- function(pattern,text,id) {
 m <- regexpr(pattern,text,perl=TRUE,ignore.case=TRUE)
 if(m[1]<0) stop(paste('Missing category:',id,pattern))
 regmatches(text,m)
}
money <- function(x,last=FALSE) {
 if(grepl('free',x,ignore.case=TRUE)) return(0)
 m <- regmatches(x,gregexpr('\\$[0-9]+(?:\\.[0-9]+)?',x,perl=TRUE))[[1]]
 if(!length(m)) stop('No price in matched category')
 as.numeric(sub('\\$','',if(last) tail(m,1) else m[1]))
}
escape <- function(x) {x<-gsub('&','&amp;',x,fixed=TRUE);x<-gsub('<','&lt;',x,fixed=TRUE);gsub('>','&gt;',x,fixed=TRUE)}
ans <- list()
for(i in seq_len(nrow(rules))) {
 r<-rules[i,]; s<-src[src$id==r$id,]
 path<-if(is.null(raw_dir)) paste0('data/evidence/',r$id,'.html') else file.path(raw_dir,paste0(r$id,'.html'))
 doc<-read_html(path)
 xml2::xml_remove(html_elements(doc,'script,style,noscript,svg'))
 tx<-gsub('[[:space:]\u00a0]+',' ',html_text2(html_element(doc,'body')))
 a<-matched(r$adult_pattern,tx,r$id); b<-matched(r$student_pattern,tx,r$id)
 adult<-money(a,r$id=='seaport'); student<-money(b,r$id %in% c('seaport','mca'))
 if(!is.null(raw_dir)) writeLines(paste0('<!doctype html><html><meta charset="utf-8"><body><p>',escape(a),'</p><p>',escape(b),'</p></body></html>'),paste0('data/evidence/',r$id,'.html'),useBytes=TRUE)
 ans[[i]]<-data.frame(s,adult=adult,student=student,saving=adult-student,adult22=if(r$id=='whitney') 0 else adult,student22=if(r$id=='whitney') 0 else student,price_type=r$price_type,hours_note=r$hours_note,conditions=r$conditions,observed_date='2026-09-21',adult_evidence=a,student_evidence=b)
}
d<-do.call(rbind,ans);d$saving22<-d$adult22-d$student22
stopifnot(!anyDuplicated(d$id),all(is.finite(d$adult)),all(d$student>=0),all(d$saving>=0),all(d$student<=d$adult))
write.csv(d,'data/derived/museum_prices.csv',row.names=FALSE,fileEncoding='UTF-8')
city<-do.call(rbind,lapply(split(d,d$city),function(z) data.frame(city=z$city[1],region=z$region[1],n=nrow(z),adult=mean(z$adult),student=mean(z$student),saving=mean(z$saving),saving22=mean(z$saving22),paid_only=if(any(z$adult>0)) mean(z$saving[z$adult>0]) else NA)))
city<-city[order(-city$saving),];rownames(city)<-NULL
region<-do.call(rbind,lapply(split(city,city$region),function(z) data.frame(region=z$region[1],cities=nrow(z),museums=sum(z$n),saving=mean(z$saving),student=mean(z$student))))
write.csv(city,'data/derived/city_summary.csv',row.names=FALSE)
write.csv(region,'data/derived/region_summary.csv',row.names=FALSE)
theme_set(theme_minimal(base_size=12)+theme(plot.background=element_rect(fill='#fbf9f3',color=NA),panel.grid.minor=element_blank(),panel.grid.major.y=element_blank(),plot.title=element_text(face='bold',color='#173f3b'),axis.title.y=element_blank()))
city$label<-paste0(city$city,' (n=',city$n,')')
g<-ggplot(city,aes(saving,reorder(label,saving)))+geom_col(fill='#21665c',width=.58)+geom_text(aes(label=sprintf('$%.2f',saving)),hjust=-.15,size=3.8)+scale_x_continuous(limits=c(0,max(city$saving)+3),labels=function(x) paste0('$',x))+labs(title='Where does student status save more?',subtitle='Average posted-price difference per museum | age 30, nonresident',x='Mean student discount (USD)',caption='Selected museums only. MCA uses suggested online prices; n = museums.\nSnapshot: September 21, 2026. Sources linked in the explorer.')
ggsave('results/city-savings.png',g,width=9,height=5.5,dpi=180)
g2<-ggplot(d,aes(student,reorder(museum,saving)))+geom_segment(aes(x=student,xend=adult,yend=reorder(museum,saving)),color='#cf9f45',linewidth=1.6)+geom_point(aes(color='Student'),size=2.6)+geom_point(aes(x=adult,color='Adult'),size=2.6)+scale_color_manual(values=c(Student='#21665c',Adult='#b36b38'))+labs(title='A discount is not the same as a cheap visit',subtitle='Posted admission: student vs. otherwise equivalent adult, age 30',x='USD',color=NULL,caption='Zero-price pairs overlap. General admission only; fees and special exhibitions excluded.')+theme(legend.position='top',axis.text.y=element_text(size=9))
ggsave('results/museum-prices.png',g2,width=10,height=7.4,dpi=180)
writeLines(capture.output(sessionInfo()),'results/session-info.txt')
print(city);print(region)
