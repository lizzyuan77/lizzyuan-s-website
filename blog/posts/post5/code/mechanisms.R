# Additional descriptive checks. Run after analyze.R from post5.
library(ggplot2)
load_table <- function(t) read.delim(paste0('data/acsdt1y2024-',tolower(t),'-states.dat'),sep='|',check.names=FALSE)
a <- load_table('B24010'); f <- load_table('B24020'); pay <- load_table('B24022')
z <- read.csv('results/states.csv',colClasses=c(state='character'))
merge_keep <- function(x,y) merge(x,y,by='GEO_ID',all.x=TRUE,sort=FALSE)
z <- merge_keep(merge_keep(merge_keep(z,a),f),pay)
stopifnot(nrow(z)==50,!anyDuplicated(z$state))
derive <- function(x) {
 x$tech_female <- x$B24010_E171
 x$tech_male <- x$B24010_E020
 x$women_workforce <- 100*x$B24010_E153/x$B24010_E001
 x$women_tech <- 100*x$tech_female/(x$tech_female+x$tech_male)
 x$representation_shortfall <- x$women_workforce-x$women_tech
 x$female_tech_rate <- 100*x$tech_female/x$B24010_E153
 x$male_tech_rate <- 100*x$tech_male/x$B24010_E002
 x$women_tech_ft <- 100*x$B24020_E171/(x$B24020_E171+x$B24020_E020)
 x$women_workforce_ft <- 100*x$B24020_E153/x$B24020_E001
 x$tech_male_pay <- ifelse(x$B24022_E008>0,x$B24022_E008,NA)
 x$tech_female_pay <- ifelse(x$B24022_E044>0,x$B24022_E044,NA)
 x$tech_pay_ratio <- 100*x$tech_female_pay/x$tech_male_pay
 x
}
z <- derive(z)
stopifnot(all(z$tech_female+z$tech_male==as.numeric(z$S2401_C01_007E)))
stopifnot(all(z$B24010_E001==as.numeric(z$S2401_C01_001E)))
stopifnot(all(z$tech_female>0),all(z$tech_male>0),all(z$women_tech>=0 & z$women_tech<=100))
write.csv(z,'results/states-expanded.csv',row.names=FALSE)
us <- derive(merge_keep(merge_keep(subset(a,GEO_ID=='0100000US'),f),pay))
e <- read.delim('data/acsdt1y2024-b20017.dat',sep='|');e<-subset(e,GEO_ID=='0100000US')
us$male<-e$B20017_E003;us$female<-e$B20017_E006;us$ratio<-100*us$female/us$male
us$matched_male<-us$B24022_E002;us$matched_female<-us$B24022_E038
us$matched_ratio<-100*us$matched_female/us$matched_male
write.csv(us,'results/national.csv',row.names=FALSE)
partial <- function(x,y,control) cor(resid(lm(x~control)),resid(lm(y~control)))
stats<-data.frame(check=c('tech_ratio','income_ratio','women_tech_ratio','tech_ratio_holding_income','women_tech_ratio_holding_income','tech_income'),value=c(cor(z$tech_share,z$ratio),cor(z$income,z$ratio),cor(z$women_tech,z$ratio),partial(z$tech_share,z$ratio,z$income),partial(z$women_tech,z$ratio,z$income),cor(z$tech_share,z$income)))
write.csv(stats,'results/mechanism-correlations.csv',row.names=FALSE)
print(stats)
print(z[z$NAME%in%c('New York','Maryland','Washington','Utah'),c('NAME','women_workforce','women_tech','women_tech_ft','female_tech_rate','male_tech_rate','tech_pay_ratio','tech_male_pay','tech_female_pay')],row.names=FALSE)
print(us[,c('women_workforce','women_tech','female_tech_rate','male_tech_rate','women_tech_ft','women_workforce_ft','tech_pay_ratio','tech_male_pay','tech_female_pay','ratio')])
cat('States underrepresented:',sum(z$women_tech<z$women_workforce),'\n')
cat('FT states underrepresented:',sum(z$women_tech_ft<z$women_workforce_ft),'\n')
bg <- '#fbf9f3'; ink <- '#173f3b'
theme_set(theme_minimal(base_size=13)+theme(plot.background=element_rect(fill=bg,color=NA),panel.grid.minor=element_blank(),plot.title=element_text(face='bold',color=ink,size=19),plot.subtitle=element_text(color='#52665f'),plot.caption=element_text(hjust=0,color='#52665f'),axis.title=element_text(color=ink)))
# Every state is retained; selected comparisons get labels.
labels<-subset(z,NAME%in%c('Utah','New York','Washington','Maryland','Louisiana','California'))
p<-ggplot(z,aes(women_tech,ratio))+geom_point(color='#21665c',size=2.5,alpha=.8)+geom_text(data=labels,aes(label=abbr),nudge_y=1.1,size=3.5,check_overlap=TRUE)+labs(title='Who holds the tech jobs matters, too',subtitle='Each dot is one state | 2024 ACS 1-year estimates',x='Women as a share of computer & mathematical workers (%)',y='Women’s / men’s median annual earnings (%)',caption='Representation: all employed residents 16+. Earnings: full-time, year-round workers 16+. Descriptive associations.')
ggsave('results/representation-scatter.png',p,width=10,height=6.5,dpi=180,bg=bg)
# Compare the female share with a state-specific workforce benchmark.
case <- subset(z,NAME%in%c('Utah','Washington','Maryland','New York'))
case$NAME<-factor(case$NAME,levels=c('Utah','Washington','Maryland','New York'))
p<-ggplot(case,aes(y=NAME))+geom_segment(aes(x=women_tech,xend=women_workforce,yend=NAME),color='#b4c1ba',linewidth=1.5)+geom_point(aes(x=women_tech,color='Technology occupations'),size=4)+geom_point(aes(x=women_workforce,color='All employed workers'),size=4)+geom_text(aes(x=women_tech,label=sprintf('%.1f%%',women_tech)),nudge_y=.23,size=4)+geom_text(aes(x=women_workforce,label=sprintf('%.1f%%',women_workforce)),nudge_y=.23,size=4)+scale_color_manual(values=c('Technology occupations'='#17665d','All employed workers'='#b66b3d'))+scale_x_continuous(limits=c(15,55),breaks=seq(15,55,10))+labs(title='A technology hub can still leave women underrepresented',subtitle='Women’s share of technology occupations versus women’s share of all employment',x='Women’s share (%)',y=NULL,color=NULL,caption='2024 ACS B24010. All civilian employed residents age 16+. Four illustrative states, not a representative sample.')+theme(legend.position='bottom',panel.grid.major.y=element_blank())
ggsave('results/representation-cases.png',p,width=10,height=5.5,dpi=180,bg=bg)
# Compare national medians, not a decomposition of state medians.
national_pay<-data.frame(group=rep(c('All occupations','Computer & mathematical occupations'),each=2),sex=rep(c('Women','Men'),2),earnings=c(us$matched_female,us$matched_male,us$tech_female_pay,us$tech_male_pay))
national_pay$group<-factor(national_pay$group,levels=unique(national_pay$group))
p<-ggplot(national_pay,aes(group,earnings/1000,fill=sex))+geom_col(position=position_dodge(.75),width=.63)+geom_text(aes(label=paste0('$',format(round(earnings),big.mark=',',trim=TRUE))),position=position_dodge(.75),vjust=-.5,size=4)+scale_fill_manual(values=c('Women'='#17665d','Men'='#b66b3d'))+scale_y_continuous(expand=expansion(mult=c(0,.15)))+labs(title='Tech pays more for both groups. A gap remains.',subtitle='United States | Full-time, year-round civilian employed residents age 16+',x=NULL,y='Median annual earnings (thousands of dollars)',fill=NULL,caption='2024 ACS B24022. Same population definition for both groups; job, seniority and hours are not held constant.')+theme(legend.position='bottom')
ggsave('results/national-earnings.png',p,width=10,height=6,dpi=180,bg=bg)
writeLines(capture.output(sessionInfo()),'results/session-info.txt')
