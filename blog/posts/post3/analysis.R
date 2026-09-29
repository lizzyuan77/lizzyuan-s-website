# Run with Rscript analysis.R path/to/IPUMS_CPS.xml
# Raw microdata stay outside the publication folder. DDI imports preserve coding.
summarise_cps <- function(x, narrow=FALSE) {
 required<-c('YEAR','MONTH','SERIAL','PERNUM','AGE','LABFORCE','WTFINL')
 if(!all(required %in% names(x))) stop('Missing required variables: ',paste(setdiff(required,names(x)),collapse=', '))
 x<-as.data.frame(x[,required]); x[]<-lapply(x,as.numeric)
 if(!setequal(unique(x$YEAR),c(2019,2024))) stop('Extract must contain exactly 2019 and 2024.')
 if(anyNA(x[,c('YEAR','MONTH','SERIAL','PERNUM')])) stop('Missing identifiers.')
 if(anyDuplicated(x[,c('YEAR','MONTH','SERIAL','PERNUM')])) stop('Duplicate person-month identifiers; check overlapping extracts or ASEC.')
 months<-unique(x[,c('YEAR','MONTH')])
 if(nrow(months)!=24 || !all(months$MONTH %in% 1:12)) stop('Need all 12 Basic Monthly samples in both years.')
 if(any(!is.finite(x$WTFINL)) || any(x$WTFINL<0)) stop('Invalid weights.')
 if(anyNA(x$AGE) || any(!x$AGE %in% 0:99)) stop('Unexpected AGE codes; inspect DDI.')
 if(anyNA(x$LABFORCE) || any(!x$LABFORCE %in% c(0,1,2))) stop('Unexpected LABFORCE codes; inspect DDI.')
 audit<-data.frame(stage=c('All person-month records','Age 16+ with civilian labor-force status','Positive-weight analysis records'),n=c(nrow(x),sum(x$AGE>=16 & x$LABFORCE %in% 1:2),sum(x$AGE>=16 & x$LABFORCE %in% 1:2 & x$WTFINL>0)))
 x<-x[x$AGE>=16 & x$LABFORCE %in% 1:2 & x$WTFINL>0,]
 if(narrow) {
  breaks<-c(16,20,seq(25,80,5),Inf)
  labels<-c('16-19',paste0(seq(20,75,5),'-',seq(24,79,5)),'80+')
 } else {breaks<-c(16,25,35,45,55,65,75,Inf);labels<-c('16-24','25-34','35-44','45-54','55-64','65-74','75+')}
 x$age_group<-cut(x$AGE,breaks=breaks,right=FALSE,labels=labels)
 # Normalize within month so every month has equal weight in each annual rate.
 x$w<-x$WTFINL/ave(x$WTFINL,x$YEAR,x$MONTH,FUN=sum)/12
 x$in_lf<-as.numeric(x$LABFORCE==2)
 x$joint<-x$w*x$in_lf
 g<-aggregate(cbind(share=w,joint=joint)~YEAR+age_group,x,sum)
 counts<-aggregate(PERNUM~YEAR+age_group,x,length); names(counts)[3]<-'n_person_months'
 g<-merge(g,counts,by=c('YEAR','age_group'))
 if(nrow(g)!=2*length(labels)) stop('Empty age cells; cannot standardize without common support.')
 g$rate<-g$joint/g$share
 annual<-aggregate(joint~YEAR,g,sum);names(annual)[2]<-'rate'
 a<-g[g$YEAR==2019,];b<-g[g$YEAR==2024,];b<-b[match(a$age_group,b$age_group),]
 # Symmetric Kitagawa identity: no arbitrary ordering of the two changes.
 change<-data.frame(age_group=a$age_group,composition=(b$share-a$share)*(a$rate+b$rate)/2*100,within=(b$rate-a$rate)*(a$share+b$share)/2*100)
 delta<-100*(annual$rate[annual$YEAR==2024]-annual$rate[annual$YEAR==2019])
 if(abs(sum(change$composition+change$within)-delta)>1e-8) stop('Decomposition does not reconcile.')
 stopifnot(all(g$rate>=0 & g$rate<=1),all(abs(tapply(g$share,g$YEAR,sum)-1)<1e-9))
 list(groups=g,annual=annual,decomposition=change,audit=audit,delta=delta,
      standardized2024=sum(a$share*b$rate),composition=sum(change$composition),within=sum(change$within))
}

run_analysis<-function(ddi_path) {
 for(pkg in c('ipumsr','ggplot2')) if(!requireNamespace(pkg,quietly=TRUE)) stop('Install package: ',pkg)
 if(!file.exists(ddi_path)) stop('IPUMS DDI file not found. See DATA_REQUEST.md; no substitute data will be generated.')
 ddi<-ipumsr::read_ipums_ddi(ddi_path)
 x<-ipumsr::read_ipums_micro(ddi,verbose=FALSE)
 if(!'ASECFLAG' %in% names(x) || any(x$ASECFLAG==1,na.rm=TRUE)) stop('Use Basic Monthly data only; ASEC records are not allowed.')
 res<-summarise_cps(x); sensitivity<-summarise_cps(x,TRUE)
 dir.create('results',showWarnings=FALSE)
 for(nm in c('groups','annual','decomposition','audit')) write.csv(res[[nm]],paste0('results/',nm,'.csv'),row.names=FALSE)
 write.csv(data.frame(grouping=c('Broad age groups','Five-year groups (16-19 and 80+ endpoints)'),composition=c(res$composition,sensitivity$composition),within=c(res$within,sensitivity$within),net=c(res$delta,sensitivity$delta)),'results/sensitivity.csv',row.names=FALSE)
 saveRDS(res,'results/analysis.rds')
 make_figures(res,'results')
 writeLines(trimws(capture.output(sessionInfo()),which='right'),'results/session-info.txt')
 writeLines(c(paste('DDI basename:',basename(ddi_path)),paste('DDI MD5:',unname(tools::md5sum(ddi_path))),paste('Analysis run:',Sys.Date()),'Read corresponding IPUMS citation/version from the supplied DDI.'),'results/provenance.txt')
 invisible(res)
}

make_figures<-function(res,out_dir,test_only=FALSE) {
 library(ggplot2)
 dir.create(out_dir,recursive=TRUE,showWarnings=FALSE)
 theme_set(theme_minimal(base_size=13)+theme(panel.grid.minor=element_blank(),plot.title=element_text(face='bold',colour='#173f3b'),plot.background=element_rect(fill='#fbf9f3',colour=NA),legend.position='top'))
 colours<-c('2019'='#bd793d','2024'='#21665c')
 g<-res$groups;g$year<-factor(g$YEAR)
 p1<-ggplot(g,aes(age_group,100*rate,colour=year,group=year))+geom_line(linewidth=1)+geom_point(size=3)+scale_colour_manual(values=colours)+scale_y_continuous(limits=c(0,100))+labs(title='1. Did participation change within age groups?',x='Age',y='Labor-force participation (%)',colour=NULL,caption='IPUMS CPS Basic Monthly, all months of 2019 and 2024. WTFINL weighted.\nCivilians age 16+; employed plus unemployed, not employment alone.')
 p2<-ggplot(g,aes(age_group,100*share,fill=year))+geom_col(position='dodge',width=.72)+scale_fill_manual(values=colours)+labs(title='2. Did the population shift toward older ages?',x='Age',y='Share of civilian population age 16+ (%)',fill=NULL,caption='Shares average the twelve monthly weighted population compositions.\nPopulation shares, not shares of the downloaded sample.')
 parts<-rbind(data.frame(component='Age composition',value=res$composition),data.frame(component='Within-age participation',value=res$within),data.frame(component='Observed total',value=res$delta))
 parts$component<-factor(parts$component,levels=parts$component)
 p3<-ggplot(parts,aes(component,value,fill=component))+geom_hline(yintercept=0,colour='#89938c')+geom_col(width=.55)+geom_text(aes(label=sprintf('%+.2f pp',value)),vjust=ifelse(parts$value>=0,-.6,1.5),size=4)+scale_fill_manual(values=c('#bd793d','#21665c','#586878'),guide='none')+labs(title='3. Separate composition from participation changes',subtitle='2019 to 2024 | symmetric Kitagawa decomposition',x=NULL,y='Contribution to change (percentage points)',caption='Composition + within-age change = observed total. Descriptive accounting, not causation.')+scale_y_continuous(expand=expansion(mult=.22))
 plots<-list(p1,p2,p3)
 for(i in 1:3) {
  if(test_only) plots[[i]]<-plots[[i]]+labs(title=paste('SYNTHETIC TEST ONLY - Figure',i),caption='Artificial fixtures for code validation. NOT CPS data or empirical findings.')
  ggsave(file.path(out_dir,paste0('figure',i,'.png')),plots[[i]],width=9,height=5.4,dpi=180)
 }
 invisible(plots)
}
if(sys.nframe()==0) {
 args<-commandArgs(trailingOnly=TRUE)
 if(length(args)!=1) stop('Usage: Rscript analysis.R path/to/IPUMS_CPS.xml')
 run_analysis(args[1])
}
