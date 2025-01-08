# REF: https://towardsdatascience.com/doing-and-reporting-a-serial-mediation-model-with-two-mediators-in-r-with-lavaan-739ed3155814

set.seed(1234) #enter this command to get the same "random" results as I do here.
iv=rnorm(n=1000,mean=50, sd=10)
m1=.6*rnorm(n=1000,mean=50, sd=10)+.4*iv
m2=.6*rnorm(n=1000,mean=50, sd=10)+.4*m1
dv=.6*rnorm(n=1000,mean=50, sd=10)+.4*m2
cv1=rnorm(n=1000,mean=50, sd=10)
cv2=rnorm(n=1000,mean=50, sd=10)

fit=lm(dv~iv)
summary(fit)
library(lavaan)
df=as.data.frame(cbind(iv,dv,m1,m2,cv1,cv2))

model="
  #Regressions
  m1 ~ a*iv
  m2 ~ b*m1 + iv
  dv ~ c*m2 + m1 + d*iv + cv1 + cv2
  
  #Defined Parameters: id, indirect effect; de, direct effect
  ind_eff := a*b*c
  dir_eff := d
"
fit=sem(model,df)
summary(fit)

fit <- lavaan::sem(model = model, data = df, se = "boot", bootstrap = 5000, ncpus=8)
lavaan::parameterEstimates(fit, boot.ci.type = "bca.simple")

fit <- lavaan::sem(model = model, data = df)
lavaan::parameterEstimates(fit, boot.ci.type = "bca.simple")

fit.boot = bootstrapLavaan(fit, R = 1e6, parallel = 'multicore', ncpus=8)
lavaan::parameterEstimates(fit, boot.ci.type = "bca.simple")
