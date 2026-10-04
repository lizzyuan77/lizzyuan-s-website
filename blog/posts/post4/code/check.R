z<-read.csv('results/state-changes.csv')
samples<-list('50 states'=z,'Exclude California'=subset(z,state!=6))
a<-do.call(rbind,lapply(names(samples),function(n){v<-samples[[n]];data.frame(sample=n,n=nrow(v),unemployment_pearson=cor(v$tech_change,v$unemployment_change),unemployment_spearman=cor(v$tech_change,v$unemployment_change,method='spearman'),epr_pearson=cor(v$tech_change,v$epr_change),epr_spearman=cor(v$tech_change,v$epr_change,method='spearman'))}))
write.csv(a,'results/robustness.csv',row.names=FALSE);print(a)
