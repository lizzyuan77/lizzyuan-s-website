library(ggplot2)
dir.create('results',showWarnings=FALSE)
clean<-function(path){d<-read.csv(path);d$employed<-d$S2401_C01_001E;d$tech<-d$S2401_C01_007E;d$tech_share<-100*d$tech/d$employed;d$unemployment<-d$S2301_C04_001E;d$epr<-d$S2301_C03_001E;stopifnot(all(is.finite(d$tech_share)),all(d$tech>0),all(d$tech<d$employed),all(d$unemployment>=0),all(d$epr>0));d}
d<-clean('data/state-panel.csv');bay<-clean('data/bay-panel.csv');stopifnot(nrow(d)==306,!anyDuplicated(d[c('year','state')]),all(table(d$year)==51),nrow(bay)==12);s<-subset(d,state!=11)
changes<-function(x,a,b,id='state'){z<-merge(subset(x,year==a),subset(x,year==b),by=id,suffixes=c('_start','_end'));z$tech_change<-z$tech_share_end-z$tech_share_start;z$unemployment_change<-z$unemployment_end-z$unemployment_start;z$epr_change<-z$epr_end-z$epr_start;z$tech_growth<-100*(z$tech_end/z$tech_start-1);z$total_growth<-100*(z$employed_end/z$employed_start-1);z}
z<-changes(s,2018,2024)
periods<-list(c(2018,2019),c(2019,2021),c(2021,2024),c(2018,2024))
stats<-do.call(rbind,lapply(periods,function(p){v<-changes(s,p[1],p[2]);data.frame(period=paste(p,collapse='-'),n=nrow(v),unemployment_r=cor(v$tech_change,v$unemployment_change),epr_r=cor(v$tech_change,v$epr_change))}))
write.csv(z,'results/state-changes.csv',row.names=FALSE);write.csv(stats,'results/period-correlations.csv',row.names=FALSE);write.csv(changes(bay,2018,2024,'county'),'results/bay-changes.csv',row.names=FALSE)
# Each state has equal weight. Published ACS estimates already incorporate survey weights.
# Percentage-point changes apply to rates; percent growth applies to counts. No causal inference.
source('code/figures.R',encoding='UTF-8')
writeLines(capture.output(sessionInfo()),'results/session-info.txt')

