# Intuitive figures; called after analyze.R creates the validated data and changes.
ink <- '#173f3b'; green <- '#21665c'; orange <- '#bf783b'; paper <- '#fbf9f3'
theme_set(theme_minimal(base_size=14) + theme(panel.grid.minor=element_blank(), plot.background=element_rect(fill=paper,colour=NA), plot.title=element_text(face='bold',colour=ink,size=19), plot.subtitle=element_text(colour='#52665f'), plot.caption=element_text(size=10,hjust=0), legend.position='top'))

# 1. Rank by measured increase, not by hand-picked examples.
top <- head(z[order(-z$tech_change,z$state),],10)
top$place <- factor(top$NAME_start, levels=rev(top$NAME_start))
p1 <- ggplot(top,aes(tech_change,place)) +
 geom_col(fill=green,width=.62) +
 geom_text(aes(label=sprintf('+%.2f pp',tech_change)),hjust=-.12,size=4) +
 scale_x_continuous(limits=c(0,max(top$tech_change)+.3),expand=expansion(mult=c(0,.02))) +
 labs(title='1. Where did tech employment share grow most?',subtitle='Top 10 states by increase, 2018-2024 | 48 of 50 states recorded an increase',x='Increase in computer & mathematical occupation share (percentage points)',y=NULL,caption='Source: Census ACS 1-year, S2401. Share of employed residents, not local office jobs.\nA rise from 3% to 4% is +1 percentage point (pp).') +
 theme(panel.grid.major.y=element_blank())

# 2. Both panels use the same favorable direction: up = improvement.
l <- rbind(data.frame(z,metric='Lower unemployment',improvement=-z$unemployment_change),data.frame(z,metric='More adults employed',improvement=z$epr_change))
l$metric<-factor(l$metric,levels=c('Lower unemployment','More adults employed'))
l$status<-ifelse(l$improvement>0,'Improved',ifelse(l$improvement<0,'Worsened','Unchanged'))
labelrows<-subset(l,NAME_start %in% c('California','Washington','Texas'))
p2<-ggplot(l,aes(tech_change,improvement)) +
 annotate('rect',xmin=-Inf,xmax=Inf,ymin=0,ymax=Inf,fill='#e9f1e9',alpha=.65) +
 annotate('rect',xmin=-Inf,xmax=Inf,ymin=-Inf,ymax=0,fill='#f6e8de',alpha=.55) +
 geom_hline(yintercept=0,colour=ink,linewidth=.5) +
 geom_point(aes(colour=status),size=2.6,alpha=.85) +
 geom_smooth(method='lm',se=FALSE,colour='#66706b',linetype=2,linewidth=.6) +
 geom_text(data=labelrows,aes(label=NAME_start),hjust=1.04,vjust=-.7,size=3.2,colour=ink) +
 scale_colour_manual(values=c('Improved'=green,'Worsened'=orange,'Unchanged'='#7a8188'),guide='none') +
 facet_wrap(~metric,ncol=1,scales='free_y') +
 labs(title='2. Did more tech come with a better job market?',subtitle='Each dot is one state, 2018-2024. Higher on either panel = a better outcome.',x='Increase in tech employment share (percentage points)',y='Improvement (percentage points)',caption='Green background: improvement. Peach: deterioration. Dashed lines summarize the association.\nUnemployment improvement = 2018 rate minus 2024 rate; employment improvement = 2024 ratio minus 2018 ratio.')

# 3. Compare interpretable outcome changes, rather than correlation coefficients.
group_rows<-list(); memberships<-list()
for(i in 1:3){
 pp<-periods[[i]];v<-changes(s,pp[1],pp[2]);v<-v[order(v$tech_change,v$state),]
 v$group<-NA_character_;v$group[1:13]<-'Slowest tech-share growth';v$group[38:50]<-'Fastest tech-share growth'
 v<-v[!is.na(v$group),];v$period<-paste(pp,collapse='-');memberships[[i]]<-v
 for(g in unique(v$group)){
  a<-subset(v,group==g)
  group_rows[[length(group_rows)+1]]<-data.frame(period=v$period[1],group=g,metric='Lower unemployment',improvement=mean(-a$unemployment_change))
  group_rows[[length(group_rows)+1]]<-data.frame(period=v$period[1],group=g,metric='More adults employed',improvement=mean(a$epr_change))
 }
}
groups<-do.call(rbind,group_rows);write.csv(groups,'results/period-groups.csv',row.names=FALSE)
write.csv(do.call(rbind,memberships),'results/period-group-membership.csv',row.names=FALSE)
groups$group<-factor(groups$group,levels=c('Fastest tech-share growth','Slowest tech-share growth'))
groups$metric<-factor(groups$metric,levels=c('Lower unemployment','More adults employed'))
p3<-ggplot(groups,aes(period,improvement,fill=group)) +
 geom_hline(yintercept=0,colour=ink) +geom_col(position=position_dodge(.75),width=.65) +
 geom_text(aes(label=sprintf('%+.2f',improvement),vjust=ifelse(improvement>=0,-.4,1.3)),position=position_dodge(.75),size=3.8) +
 facet_wrap(~metric,ncol=1,scales='free_y') +scale_fill_manual(values=c(green,'#aab2b0')) +
 scale_y_continuous(expand=expansion(mult=.17)) +
 labs(title='3. Faster tech growth did not consistently mean bigger gains',subtitle='Compare the 13 fastest- and 13 slowest-growing states in each period',x=NULL,y='Average improvement (percentage points)',fill=NULL,caption='Higher = better in both panels. Equal-weight state means; groups are reselected each period.\nChanges cover unequal-length periods, not annualized rates. 2019-2021 spans the pandemic.')

# 4. Fixed county boundaries; endpoints and values are explicit.
bc<-changes(bay,2018,2024,'county')
ba<-rbind(data.frame(place=sub(', California','',bc$NAME_start),metric='Tech employment share (%)',start=bc$tech_share_start,end=bc$tech_share_end),data.frame(place=sub(', California','',bc$NAME_start),metric='Unemployment rate (%)',start=bc$unemployment_start,end=bc$unemployment_end))
ba$place<-factor(ba$place,levels=c('San Francisco County','Santa Clara County'))
p4<-ggplot(ba,aes(y=place)) +geom_segment(aes(x=start,xend=end,yend=place),colour='#b6bfba',linewidth=2) +
 geom_point(aes(x=start,colour='2018'),size=4) +geom_point(aes(x=end,colour='2024'),size=4) +
 geom_text(aes(x=start,label=sprintf('%.2f',start)),vjust=1.9,size=4) +
 geom_text(aes(x=end,label=sprintf('%.2f',end)),vjust=-1.1,size=4) +
 scale_colour_manual(values=c('2018'='#84918b','2024'=green)) +
 scale_y_discrete(expand=expansion(add=.7)) +scale_x_continuous(expand=expansion(mult=.15)) +
 facet_wrap(~metric,ncol=1,scales='free_x') +
 labs(title='4. In two Bay Area counties, both measures rose',subtitle='2018 to 2024 | More tech workers did not coincide with lower unemployment',x='Percent',y=NULL,colour=NULL,caption='Census ACS 1-year point estimates; these two counties are not the full Bay Area.\nTech share describes employed residents. Unemployment describes the broader civilian labor force.') +theme(panel.grid.major.y=element_blank())
for(i in 1:4)ggsave(paste0('results/figure',i,'.png'),get(paste0('p',i)),width=10,height=if(i==1)7 else 9,dpi=180)
print(groups)

