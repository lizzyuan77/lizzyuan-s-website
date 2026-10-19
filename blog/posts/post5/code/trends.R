# Repeated ACS 1-year cross sections, not a panel tracking the same people.
# Run from post5 after code/mechanisms.R. All inputs are cached for offline use.
library(ggplot2)
years <- c(2019, 2021, 2022, 2023, 2024)
read_year <- function(year) {
  tables <- lapply(c('B20017', 'B24010', 'B24022'), function(table) {
    read.csv(sprintf('data/trends/%s/%s.csv', year, table), check.names=FALSE)
  })
  d <- Reduce(function(x,y) merge(x,y,by='GEO_ID'), tables)
  stopifnot(nrow(d)==53, !anyDuplicated(d$GEO_ID))
  d$year <- year
  d$state <- ifelse(grepl('^0400000US',d$GEO_ID),sub('^0400000US','',d$GEO_ID),'US')
  positive <- function(x) ifelse(x>0,x,NA_real_)
  d$overall_ratio <- 100*positive(d$B20017_E006)/positive(d$B20017_E003)
  d$matched_ratio <- 100*positive(d$B24022_E038)/positive(d$B24022_E002)
  d$tech_ratio <- 100*positive(d$B24022_E044)/positive(d$B24022_E008)
  d$tech_share <- 100*(d$B24010_E020+d$B24010_E171)/d$B24010_E001
  d$women_tech <- 100*d$B24010_E171/(d$B24010_E020+d$B24010_E171)
  d$women_workforce <- 100*d$B24010_E153/d$B24010_E001
  d$representation_shortfall <- d$women_workforce-d$women_tech
  stopifnot(all(d$B24010_E020>0),all(d$B24010_E171>0))
  d
}
panel <- do.call(rbind,lapply(years,read_year))
panel <- subset(panel,!state %in% c('11','72'))
stopifnot(nrow(panel)==255, !anyDuplicated(paste(panel$state,panel$year)))
states <- subset(panel,state!='US')
latest <- read.csv('results/states-expanded.csv',colClasses=c(state='character'))
states$NAME <- latest$NAME[match(states$state,latest$state)]
states$abbr <- latest$abbr[match(states$state,latest$state)]
stopifnot(nrow(states)==250,!anyNA(states$NAME))
# Reconcile independent downloads with the original 2024 cross section.
check <- merge(subset(states,year==2024),latest,by='state')
stopifnot(max(abs(check$overall_ratio-check$ratio))<1e-8)
stopifnot(max(abs(check$tech_share.x-check$tech_share.y))<1e-8)
stopifnot(max(abs(check$women_tech.x-check$women_tech.y))<1e-8)
national <- subset(panel,state=='US')
national <- national[order(national$year),]
write.csv(states,'results/state-trends.csv',row.names=FALSE)
write.csv(national,'results/national-trends.csv',row.names=FALSE)

measures <- c('overall_ratio','tech_ratio','tech_share','women_tech')
start <- subset(states,year==2019,c('state','NAME','abbr',measures))
end <- subset(states,year==2024,c('state',measures))
changes <- merge(start,end,by='state',suffixes=c('_2019','_2024'))
for (name in measures) {
  changes[[paste0(name,'_change')]] <- changes[[paste0(name,'_2024')]]-changes[[paste0(name,'_2019')]]
}
write.csv(changes,'results/state-trend-changes.csv',row.names=FALSE)
correlation <- function(x,y) {
  good <- is.finite(x)&is.finite(y)
  c(n=sum(good),pearson=cor(x[good],y[good]),spearman=cor(x[good],y[good],method='spearman'))
}
checks <- rbind(
  tech_growth_gap_narrowing=correlation(changes$tech_share_change,changes$overall_ratio_change),
  women_tech_growth_gap_narrowing=correlation(changes$women_tech_change,changes$overall_ratio_change)
)
largest_change <- which.max(abs(changes$overall_ratio_change))
checks <- rbind(checks, tech_growth_excluding_largest_ratio_change=
  correlation(changes$tech_share_change[-largest_change],changes$overall_ratio_change[-largest_change]))
writeLines(paste('Largest absolute earnings-ratio change excluded in sensitivity:',
                 changes$NAME[largest_change]),'results/trend-sensitivity.txt')
write.csv(data.frame(check=rownames(checks),checks,row.names=NULL),'results/trend-correlations.csv',row.names=FALSE)
print(national[,c('year','overall_ratio','matched_ratio','tech_ratio','tech_share','women_tech','women_workforce')],row.names=FALSE)
print(checks)
cat('State point estimates with a higher overall ratio:',sum(changes$overall_ratio_change>0,na.rm=TRUE),'\n')
cat('State point estimates with a rising tech share:',sum(changes$tech_share_change>0,na.rm=TRUE),'\n')
cat('State point estimates with rising female tech representation:',sum(changes$women_tech_change>0,na.rm=TRUE),'\n')

bg <- '#fbf9f3'; ink <- '#173f3b'
theme_set(theme_minimal(base_size=12)+theme(
  plot.background=element_rect(fill=bg,color=NA),panel.grid.minor=element_blank(),
  plot.title=element_text(face='bold',color=ink,size=19),
  plot.subtitle=element_text(color='#52665f'),plot.caption=element_text(hjust=0,color='#52665f'),
  legend.position='bottom',legend.title=element_blank()
))
pay <- rbind(
  data.frame(year=national$year,value=national$matched_ratio,series='All occupations'),
  data.frame(year=national$year,value=national$tech_ratio,series='Technology occupations')
)
pay$segment <- ifelse(pay$year==2019, 'before missing year', 'after missing year')
p <- ggplot(pay,aes(year,value,color=series))+
  geom_line(aes(group=interaction(series,segment)),linewidth=1)+
  geom_point(size=3)+
  geom_text(aes(label=sprintf('%.1f',value)),nudge_y=.35,size=3.8,show.legend=FALSE)+
  scale_color_manual(values=c('All occupations'='#b66b3d','Technology occupations'='#17665d'))+
  scale_x_continuous(breaks=2019:2024)+
  scale_y_continuous(limits=c(80,89),breaks=seq(80,88,2))+
  labs(title='Progress in earnings parity was uneven',
       subtitle='Women’s median earnings per $1 earned by men (cents) | United States',
       x=NULL,y='Cents per male dollar',
       caption='ACS B24022; full-time, year-round civilian employed residents 16+. No standard 2020 ACS 1-year estimate; gap left blank.')
ggsave('results/earnings-trend.png',p,width=10,height=6,dpi=180,bg=bg)

rep <- data.frame(year=national$year,value=national$women_tech)
rep$segment <- ifelse(rep$year==2019,'before missing year','after missing year')
p <- ggplot(rep,aes(year,value))+
  geom_line(aes(group=segment),color='#653951',linewidth=1)+
  geom_point(color='#653951',size=3)+
  geom_text(aes(label=sprintf('%.1f%%',value)),nudge_y=.35,size=4)+
  scale_x_continuous(breaks=2019:2024)+scale_y_continuous(limits=c(20,32),breaks=seq(20,32,2))+
  labs(title='Women’s share of tech was almost unchanged',
       subtitle='Women’s share of computer & mathematical occupations | United States',
       x=NULL,y='Women’s share (%)',
       caption='ACS B24010; all civilian employed residents age 16+. Vertical axis begins at 20%. No estimate or interpolation for 2020.')
ggsave('results/representation-trend.png',p,width=10,height=5.5,dpi=180,bg=bg)

p <- ggplot(changes,aes(tech_share_change,overall_ratio_change))+
  geom_hline(yintercept=0,color='#b4c1ba')+
  geom_point(color='#21665c',size=2.6,alpha=.8)+
  geom_text(data=subset(changes,NAME%in%c('Washington','Maryland','Utah','New York','California','Wyoming')),
            aes(label=abbr),nudge_y=.5,size=3.5,check_overlap=TRUE)+
  labs(title='More tech did not consistently accompany a narrowing gap',
       subtitle='Each dot is a state | Changes from 2019 to 2024',
       x='Increase in technology occupation share (percentage points)',
       y='Increase in women’s / men’s earnings ratio (points)',
       caption='ACS B24010 and B20017. Above zero = a narrowing gap. States are equally weighted; descriptive, not causal.')
ggsave('results/change-comparison.png',p,width=10,height=6,dpi=180,bg=bg)
