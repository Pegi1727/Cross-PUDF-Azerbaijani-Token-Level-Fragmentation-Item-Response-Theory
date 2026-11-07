#!/usr/bin/env Rscript
# Reproducible Cross-PUDF analyses; run Rscript scripts/cross_pudf_analysis.R [scores.csv] [sampling.csv]
args <- commandArgs(trailingOnly=TRUE)
script_arg <- grep('^--file=', commandArgs(), value=TRUE)
script_path <- if(length(script_arg)) normalizePath(sub('^--file=','',script_arg[1])) else normalizePath('scripts/cross_pudf_analysis.R')
root <- dirname(dirname(script_path))
scores_file <- if(length(args)>=1) args[1] else file.path(root,'data/processed/cross_pudf_100_sentences_scores.csv')
sampling_file <- if(length(args)>=2) args[2] else file.path(root,'data/processed/cross_pudf_sampling_batches.csv')
score <- read.csv(scores_file,stringsAsFactors=FALSE,check.names=FALSE); samp <- read.csv(sampling_file,stringsAsFactors=FALSE,check.names=FALSE)
ac <- aggregate(samp[['2pl_discrimination_a']],list(row_id=samp$row_id),function(x) {if(length(unique(x))!=1) stop('discrimination differs within item'); x[1]}); names(ac)[2] <- '2pl_discrimination_a'
score <- merge(score,ac,by='row_id',all.x=TRUE,sort=FALSE); tiers <- unique(score$tier); theta <- sort(unique(samp$theta))
metrics <- c(word_count='unicode_word_count',target_token_count='target_token_count',source_token_count='source_token_count',target_fertility='target_token_to_word_fertility',target_source_ratio='target_source_token_ratio',nonoverlap_proxy='target_surface_nonoverlap_proxy',b_tilde='b_tilde',b_tilde_zscore='b_tilde_zscore',discrimination_a='2pl_discrimination_a')
cat('DATA VALIDATION\nScores:',nrow(score),'; selections:',nrow(samp),'; unique sampled items:',length(unique(samp$row_id)),'; tiers:',paste(tiers,collapse=', '),'; theta:',paste(theta,collapse=', '),'\n')
print(table(score$tier)); print(with(samp,table(theta,batch_number)))
if(nrow(score)!=100 || length(unique(score$row_id))!=100 || nrow(samp)!=150) stop('unexpected data dimensions')
cat('\n1. TIER DESCRIPTIVES (sample SD; IQR Q3-Q1)\n')
for(label in names(metrics)) { col <- metrics[[label]]; cat('\n',label,'\n',sep=''); out <- do.call(rbind,lapply(tiers,function(t) {x<-score[score$tier==t,col];data.frame(tier=t,n=length(x),mean=mean(x),sd=sd(x),median=median(x),IQR=IQR(x),min=min(x),max=max(x))})); print(out,row.names=FALSE,digits=10) }
cat('\n2. SHAPIRO-WILK NORMALITY BY TIER\n')
for(label in names(metrics)) for(t in tiers) {x<-score[score$tier==t,metrics[[label]]]; z<-shapiro.test(x);cat(label,' | ',t,' n=',length(x),' W=',unname(z$statistic),' p=',z$p.value,'\n',sep='')}
cat('\n3. BETWEEN-TIER ANOVA + KRUSKAL-WALLIS AND POST-HOC\n')
for(label in c('word_count','target_fertility','b_tilde','b_tilde_zscore')) {
 col<-metrics[[label]]; f<-as.formula(paste0('`',col,'` ~ factor(tier)')); an<-aov(f,data=score); cat('\n',label,'\n',sep=''); print(summary(an)); kw<-kruskal.test(score[[col]]~factor(score$tier));print(kw);cat('Tukey HSD: familywise-adjusted parametric post-hoc\n');print(TukeyHSD(an))
 pairs<-combn(tiers,2,simplify=FALSE); pw<-do.call(rbind,lapply(pairs,function(q){z<-wilcox.test(score[score$tier==q[1],col],score[score$tier==q[2],col],exact=FALSE,correct=FALSE);data.frame(tier_1=q[1],tier_2=q[2],W=unname(z$statistic),p_raw=z$p.value)}));pw$p_Bonferroni<-p.adjust(pw$p_raw,'bonferroni');cat('Wilcoxon rank-sum pairwise with Bonferroni correction\n');print(pw,row.names=FALSE,digits=10)
}
cat('\n4. OVERALL PEARSON/SPEARMAN CORRELATIONS\n')
pairs<-list(c('word_count','target_token_count','unicode_word_count','target_token_count'),c('word_count','target_fertility','unicode_word_count','target_token_to_word_fertility'),c('word_count','nonoverlap_proxy','unicode_word_count','target_surface_nonoverlap_proxy'),c('word_count','b_tilde','unicode_word_count','b_tilde'))
for(q in pairs){p<-cor.test(score[[q[3]]],score[[q[4]]],method='pearson');s<-cor.test(score[[q[3]]],score[[q[4]]],method='spearman',exact=FALSE);cat(q[1],' vs ',q[2],': Pearson r=',unname(p$estimate),' p=',p$p.value,'; Spearman rho=',unname(s$estimate),' p=',s$p.value,'\n',sep='')}
cat('Per-tier Spearman word count vs target tokens\n');for(t in tiers){d<-score[score$tier==t,];z<-cor.test(d$unicode_word_count,d$target_token_count,method='spearman',exact=FALSE);cat(t,' n=',nrow(d),' rho=',unname(z$estimate),' p=',z$p.value,'\n',sep='')}
cat('\n5. ZPD SAMPLING\n');ct<-table(factor(samp$theta,levels=theta),factor(samp$tier,levels=tiers));cat('Tier x theta pooled\n');print(ct)
for(b in sort(unique(samp$batch_number))){cat('Batch ',b,'\n',sep='');print(table(factor(samp$theta[samp$batch_number==b],levels=theta),factor(samp$tier[samp$batch_number==b],levels=tiers)))}
chi<-chisq.test(ct,correct=FALSE);cat('Chi-square pooled: X2=',unname(chi$statistic),' df=',unname(chi$parameter),' p=',chi$p.value,' min expected=',min(chi$expected),'\n',sep='')
for(col in c('fisher_information_weight','selection_probability','2pl_discrimination_a')){cat('\n',col,' by theta\n',sep='');print(do.call(rbind,lapply(theta,function(th){x<-samp[samp$theta==th,col];data.frame(theta=th,n=length(x),mean=mean(x),sd=sd(x),median=median(x),min=min(x),max=max(x))})),row.names=FALSE,digits=10)}
cat('\nDiscrimination ceiling a=3.0\n');for(th in theta){g<-samp[samp$theta==th,];u<-g[!duplicated(g$row_id),];cat('theta=',th,' selections=',nrow(g),' ceiling selections=',sum(g[['2pl_discrimination_a']]==3),' prop=',mean(g[['2pl_discrimination_a']]==3),' unique=',nrow(u),' ceiling unique=',sum(u[['2pl_discrimination_a']]==3),' unique_prop=',mean(u[['2pl_discrimination_a']]==3),'\n',sep='')}
sets<-lapply(theta,function(th)unique(samp$row_id[samp$theta==th]));names(sets)<-as.character(theta);cat('\nItem overlap/Jaccard by theta\n');for(q in combn(seq_along(sets),2,simplify=FALSE)){a<-sets[[q[1]]];b<-sets[[q[2]]];cat(names(sets)[q[1]],' vs ',names(sets)[q[2]],': intersection=',length(intersect(a,b)),' union=',length(union(a,b)),' Jaccard=',length(intersect(a,b))/length(union(a,b)),'\n',sep='')};cat('All theta intersection=',length(Reduce(intersect,sets)),' union=',length(Reduce(union,sets)),'\n')
cat('\nNOTE: 50 selections per theta; overlap uses unique item IDs; SDs are sample SD. Tukey follows ANOVA; Wilcoxon pairwise tests use Bonferroni correction.\n')
