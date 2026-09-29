# Synthetic fixtures test arithmetic ONLY. They are never article data.
source('analysis.R')
x<-expand.grid(YEAR=c(2019,2024),MONTH=1:12,AGE=c(20,30,40,50,60,70,80),LABFORCE=1:2)
x$SAMPLE<-x$YEAR*100+x$MONTH;x$SERIAL<-seq_len(nrow(x));x$PERNUM<-1
x$WTFINL<-ifelse(x$LABFORCE==2,3,1)
r<-summarise_cps(x)
stopifnot(all(abs(r$annual$rate-.75)<1e-10),abs(r$delta)<1e-10)
# Weight scaling and repeated monthly records must not alter point estimates.
y<-x;y$WTFINL[y$MONTH==6]<-y$WTFINL[y$MONTH==6]*100
stopifnot(max(abs(summarise_cps(y)$annual$rate-r$annual$rate))<1e-10)
# Only participation changes: composition component must be zero.
y<-x;y$WTFINL[y$YEAR==2024 & y$LABFORCE==2]<-4;y$WTFINL[y$YEAR==2024 & y$LABFORCE==1]<-0
rr<-summarise_cps(y)
stopifnot(abs(rr$delta-25)<1e-10,abs(rr$composition)<1e-10)
fails<-function(z) inherits(try(summarise_cps(z),silent=TRUE),'try-error')
stopifnot(fails(rbind(x,x[1,])),fails(x[x$MONTH!=3,]))
y<-x;y$LABFORCE[1]<-9;stopifnot(fails(y))
y<-x;y$WTFINL[1]<- -1;stopifnot(fails(y))
cat('PASS: weighted rates, month normalization, decomposition identity, duplicates, missing months, coding and weights.\n')
# Older group's participation remains lower, but its population share increases.
y<-x;y$WTFINL[y$AGE==80 & y$LABFORCE==2]<-1
y$WTFINL[y$AGE==80 & y$LABFORCE==1]<-3
y$WTFINL[y$YEAR==2024 & y$AGE==80]<-y$WTFINL[y$YEAR==2024 & y$AGE==80]*3
rr<-summarise_cps(y)
stopifnot(rr$delta<0,abs(rr$within)<1e-10,abs(rr$composition-rr$delta)<1e-10)
# Check the narrower-bin sensitivity with every age cell populated.
z<-expand.grid(YEAR=c(2019,2024),MONTH=1:12,AGE=c(17,22,seq(27,77,5),82),LABFORCE=1:2)
z$SAMPLE<-z$YEAR*100+z$MONTH;z$SERIAL<-seq_len(nrow(z));z$PERNUM<-1;z$WTFINL<-1
stopifnot(abs(summarise_cps(z,TRUE)$delta)<1e-10)
make_figures(rr,'test-output',test_only=TRUE)
cat('PASS: pure composition change, narrower groups, and all three figure-generation paths.\n')
