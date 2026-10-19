# Run from blog/posts/post5: Rscript code/analyze.R
library(jsonlite)
library(ggplot2)
dir.create('results', showWarnings=FALSE)
earn <- read.delim('data/acsdt1y2024-b20017.dat',sep='|',check.names=FALSE)
income <- read.delim('data/acsdt1y2024-b19013.dat',sep='|',check.names=FALSE)
j <- fromJSON('data/acs-state-2024.json')
tech <- as.data.frame(j[-1,,drop=FALSE],stringsAsFactors=FALSE)
names(tech) <- j[1,]
tech <- subset(tech,!state %in% c('11','72'))
tech$GEO_ID <- paste0('0400000US',tech$state)
z <- merge(merge(tech,earn,by='GEO_ID'),income,by='GEO_ID')
stopifnot(nrow(z)==50,!anyDuplicated(z$state))
z$male <- z$B20017_E003; z$female <- z$B20017_E006
z$ratio <- 100*z$female/z$male
z$gap <- 100-z$ratio
z$income <- z$B19013_E001
z$tech_share <- 100*as.numeric(z$S2401_C01_007E)/as.numeric(z$S2401_C01_001E)
stopifnot(all(z$male>0),all(z$female>0),all(z$income>0),all(z$tech_share>0),all(z$ratio>0 & z$ratio<150))
z$abbr <- state.abb[match(z$NAME,state.name)]
stopifnot(!anyNA(z$abbr))
write.csv(z,'results/states.csv',row.names=FALSE)
cors <- data.frame(measure=c('Technology share','Household income'),pearson=c(cor(z$tech_share,z$ratio),cor(z$income,z$ratio)),spearman=c(cor(z$tech_share,z$ratio,method='spearman'),cor(z$income,z$ratio,method='spearman')))
write.csv(cors,'results/correlations.csv',row.names=FALSE)
print(cors)
print(z[order(z$ratio),c('NAME','male','female','ratio','tech_share','income')],row.names=FALSE)
bg <- '#fbf9f3'; ink <- '#173f3b'
theme_set(theme_minimal(base_size=12)+theme(plot.background=element_rect(fill=bg,color=NA),panel.grid.minor=element_blank(),plot.title=element_text(face='bold',color=ink,size=19),plot.subtitle=element_text(color='#52665f'),plot.caption=element_text(hjust=0,color='#52665f'),axis.title=element_text(color=ink)))
labels <- subset(z,NAME %in% c('Washington','California','Maryland','Utah','Louisiana','Vermont','New York','Massachusetts'))
for(v in c('tech_share','income')) {
  xx <- if(v=='income') z[[v]]/1000 else z[[v]]
  ll <- labels; ll$x <- if(v=='income') ll[[v]]/1000 else ll[[v]]
  dd <- z; dd$x <- xx
  p <- ggplot(dd,aes(x,ratio))+geom_point(color='#21665c',size=2.8,alpha=.8)+geom_text(data=ll,aes(label=abbr),nudge_y=1.1,size=3.5,check_overlap=TRUE)+
    labs(title=if(v=='income') 'Higher income does not guarantee a narrower gap' else 'Technology concentration is not earnings parity',subtitle='Each dot is one state | 2024 ACS 1-year estimates',x=if(v=='income') 'Median household income (thousands of dollars)' else 'Computer & mathematical occupations (% of employed residents)',y="Women’s median earnings / men’s median earnings (%)",caption='Full-time, year-round workers age 16+ with earnings. Descriptive state comparisons; no causal interpretation.')+
    scale_y_continuous(limits=c(min(z$ratio)-2,max(z$ratio)+3))
  ggsave(paste0('results/',v,'.png'),p,width=10,height=6.5,dpi=180,bg=bg)
}
writeLines(capture.output(sessionInfo()),'results/session-info.txt')
