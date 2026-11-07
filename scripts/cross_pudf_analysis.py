#!/usr/bin/env python3
"""Reproduce Cross-PUDF descriptive, inferential and illustrative ZPD analyses.
Run from any directory: python scripts/cross_pudf_analysis.py [scores.csv] [sampling.csv]
Dependencies: pandas, numpy, scipy, statsmodels.
"""
from pathlib import Path
import sys
from itertools import combinations
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

ROOT=Path(__file__).resolve().parents[1]
SCORES=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'data/processed/cross_pudf_100_sentences_scores.csv'
SAMPLE=Path(sys.argv[2]).resolve() if len(sys.argv)>2 else ROOT/'data/processed/cross_pudf_sampling_batches.csv'
score=pd.read_csv(SCORES); samp=pd.read_csv(SAMPLE)
a=samp.groupby('row_id')['2pl_discrimination_a'].agg(['nunique','first'])
if (a['nunique']>1).any(): raise ValueError('discrimination differs within item')
score['2pl_discrimination_a']=score.row_id.map(a['first'])
tiers=list(score.tier.drop_duplicates()); thetas=sorted(samp.theta.unique())
metrics={'word_count':'unicode_word_count','target_token_count':'target_token_count','source_token_count':'source_token_count','target_fertility':'target_token_to_word_fertility','target_to_source_ratio':'target_source_token_ratio','nonoverlap_proxy':'target_surface_nonoverlap_proxy','b_tilde':'b_tilde','b_tilde_zscore':'b_tilde_zscore','discrimination_a':'2pl_discrimination_a'}
def pframe(title,x): print('\n'+title+'\n'+x.to_string(index=True,float_format=lambda v:f'{v:.10g}'))
print('DATA VALIDATION')
print(f'Scores: {len(score)}; sampling selections: {len(samp)}; unique sampled items: {samp.row_id.nunique()}; tiers: {tiers}; theta: {thetas}')
print('rows per tier:',score.groupby('tier').size().to_dict())
print('selections per theta/batch:',samp.groupby(['theta','batch_number']).size().to_dict())
if len(score)!=100 or score.row_id.nunique()!=100 or len(samp)!=150: raise ValueError('unexpected data dimensions')
print('\n1. TIER DESCRIPTIVE STATISTICS (sample SD; IQR Q3-Q1)')
for name,col in metrics.items():
 g=score.groupby('tier',sort=False)[col]; d=g.agg(n='count',mean='mean',sd='std',median='median',min='min',max='max'); d['IQR']=g.quantile(.75)-g.quantile(.25); pframe(name,d[['n','mean','sd','median','IQR','min','max']])
print('\n2. SHAPIRO-WILK NORMALITY TESTS BY TIER')
rows=[]
for name,col in metrics.items():
 for tier in tiers:
  x=score.loc[score.tier.eq(tier),col].dropna(); w,p=stats.shapiro(x); rows.append([name,tier,len(x),w,p])
pframe('W and p',pd.DataFrame(rows,columns=['metric','tier','n','W','p']).set_index(['metric','tier']))
print('\n3. BETWEEN-TIER TESTS (ANOVA + Kruskal-Wallis) AND POST-HOC')
for name in ['word_count','target_fertility','b_tilde','b_tilde_zscore']:
 col=metrics[name]; groups=[score.loc[score.tier.eq(t),col].dropna().to_numpy() for t in tiers]
 f,p=stats.f_oneway(*groups); h,pk=stats.kruskal(*groups)
 print(f'\n{name}: one-way ANOVA F={f:.10g}, df=({len(tiers)-1},{len(score)-len(tiers)}), p={p:.10g}; Kruskal-Wallis H={h:.10g}, df={len(tiers)-1}, p={pk:.10g}')
 tuk=pairwise_tukeyhsd(score[col],score.tier,alpha=.05)
 print('Tukey HSD (familywise adjusted):\n'+str(tuk))
 pair=[]
 for t1,t2 in combinations(tiers,2):
  x=score.loc[score.tier.eq(t1),col]; y=score.loc[score.tier.eq(t2),col]; u,pv=stats.mannwhitneyu(x,y,alternative='two-sided',method='auto'); pair.append([t1,t2,u,pv])
 adj=np.minimum(np.array([v[3] for v in pair])*len(pair),1)
 print('Pairwise Mann-Whitney U, Bonferroni corrected:')
 print(pd.DataFrame([v+[q] for v,q in zip(pair,adj)],columns=['tier_1','tier_2','U','p_raw','p_Bonferroni']).to_string(index=False,float_format=lambda v:f'{v:.9g}'))
print('\n4. OVERALL PEARSON AND SPEARMAN CORRELATIONS')
for n1,n2,c1,c2 in [('word_count','target_token_count','unicode_word_count','target_token_count'),('word_count','target_fertility','unicode_word_count','target_token_to_word_fertility'),('word_count','nonoverlap_proxy','unicode_word_count','target_surface_nonoverlap_proxy'),('word_count','b_tilde','unicode_word_count','b_tilde')]:
 r,pr=stats.pearsonr(score[c1],score[c2]); rho,ps=stats.spearmanr(score[c1],score[c2]); print(f'{n1} vs {n2}: Pearson r={r:.10g}, p={pr:.10g}; Spearman rho={rho:.10g}, p={ps:.10g}')
print('\nPer-tier Spearman word count vs target token count')
for t in tiers:
 d=score[score.tier.eq(t)]; rho,p=stats.spearmanr(d.unicode_word_count,d.target_token_count); print(f'{t}: n={len(d)}, rho={rho:.12g}, p={p:.12g}')
print('\n5. ZPD SAMPLING')
ct=pd.crosstab(samp.theta,samp.tier).reindex(index=thetas,columns=tiers,fill_value=0); pframe('Tier counts by theta pooled over batches',ct)
for b in sorted(samp.batch_number.unique()): pframe(f'Batch {b}: tier counts by theta',pd.crosstab(samp.loc[samp.batch_number.eq(b),'theta'],samp.loc[samp.batch_number.eq(b),'tier']).reindex(index=thetas,columns=tiers,fill_value=0))
chi,p,dof,exp=stats.chi2_contingency(ct.to_numpy()); print(f'Chi-square tier x theta, pooled: chi2={chi:.10g}, df={dof}, p={p:.10g}; min expected={exp.min():.10g}')
print('\nFisher information, selection probability, and discrimination summaries by theta')
for col in ['fisher_information_weight','selection_probability','2pl_discrimination_a']:
 pframe(col,samp.groupby('theta')[col].agg(n='count',mean='mean',sd='std',median='median',min='min',max='max'))
print('\nDiscrimination ceiling a=3: selected records and unique-item proportions')
rows=[]
for th,g in samp.groupby('theta'):
 u=g.drop_duplicates('row_id'); rows.append([th,len(g),int(g['2pl_discrimination_a'].eq(3).sum()),g['2pl_discrimination_a'].eq(3).mean(),len(u),int(u['2pl_discrimination_a'].eq(3).sum()),u['2pl_discrimination_a'].eq(3).mean()])
pframe('Ceiling proportions',pd.DataFrame(rows,columns=['theta','selections_n','ceiling_selections','selection_prop','unique_items_n','ceiling_unique_items','unique_prop']).set_index('theta'))
print('\nItem overlap across theta (unique row_id sets; Jaccard=intersection/union)')
sets={th:set(g.row_id) for th,g in samp.groupby('theta')}
for x,y in combinations(thetas,2):
 inter=sets[x]&sets[y]; union=sets[x]|sets[y]; print(f'{x:g} vs {y:g}: intersection={len(inter)}, union={len(union)}, Jaccard={len(inter)/len(union):.10g}')
print(f'All theta: intersection={len(set.intersection(*(sets[t] for t in thetas)))}, union={len(set.union(*(sets[t] for t in thetas)))}')
print('\nNOTE: batch-level draws are without replacement within theta; each theta has 50 selections. Overlap uses unique row IDs. SDs are sample SD. Tukey follows one-way ANOVA; Mann-Whitney post-hoc p-values use Bonferroni adjustment.')
