# Processed data dictionary

All processed files preserve the supplied derived data and summaries. Scores contain 100 rows, sampling contains 150 selected records, and summary contains five scopes.

## `cross_pudf_100_sentences_scores.csv`

| Column | Type | Description |
|---|---|---|
| `row_id` | int64 | Zero-based stable sentence identifier. |
| `tier` | object | Editorial sentence difficulty/genre tier. |
| `sentence` | object | Manually authored Azerbaijani sentence in Latin script. |
| `unicode_word_count` | int64 | Unicode-aware whitespace/word-token count used by study. |
| `source_model` | object | Source tokenizer model identifier (bert-base-uncased). |
| `source_token_count` | int64 | Number of source tokenizer tokens, excluding special tokens. |
| `source_tokens` | object | JSON-encoded list of source tokenizer token strings. |
| `target_model` | object | Target tokenizer model identifier (bert-base-multilingual-cased). |
| `target_token_count` | int64 | Number of target tokenizer tokens, excluding special tokens. |
| `target_tokens` | object | JSON-encoded list of target tokenizer token strings. |
| `target_token_to_word_fertility` | float64 | Target token count / Unicode word count. |
| `target_source_token_ratio` | float64 | Target token count / source token count. |
| `target_surface_nonoverlap_proxy` | float64 | Fraction target token surfaces whose lowercased forms are absent from source vocabulary strings after lowercase comparison; proxy only. |
| `b_tilde` | float64 | Configured score = target fertility + surface non-overlap proxy. |
| `b_tilde_zscore` | float64 | Population-standardized b_tilde across all sentences. |
| `b_tilde_minmax_minus3_to3` | float64 | Observed min-max scaling of b_tilde to [-3,3]. |
| `b_tilde_robust_p5_p95_minus3_to3` | float64 | b_tilde clipped at global 5th/95th percentiles then mapped to [-3,3]. |
| `robust_clip_p5` | float64 | Global 5th percentile clipping bound. |
| `robust_clip_p95` | float64 | Global 95th percentile clipping bound. |
| `overall_rank` | float64 | Ascending average rank across all sentences. |
| `level_rank` | float64 | Ascending average rank within tier. |

## `cross_pudf_sampling_batches.csv`

| Column | Type | Description |
|---|---|---|
| `theta` | float64 | Illustrative latent-ability level (-2, 0, 2). |
| `batch_number` | int64 | Batch index within theta level (1-5). |
| `position_in_batch` | int64 | Selection order (1-10) within batch. |
| `row_id` | int64 | Sentence identifier referencing score table/raw corpus. |
| `tier` | object | Sentence tier. |
| `sentence` | object | Selected Azerbaijani sentence. |
| `selection_probability` | float64 | Normalized probability/weight used at item-selection draw. |
| `fisher_information_weight` | float64 | Illustrative 2PL information weight a²P(1-P) at theta. |
| `2pl_discrimination_a` | float64 | Illustrative discrimination a, target fertility clipped to [0.3,3.0]. |
| `2pl_difficulty_b` | float64 | Illustrative difficulty b, equal to b_tilde z-score. |
| `probability_correct_at_theta` | float64 | Illustrative logistic 2PL response probability at theta. |
| `seed` | int64 | Random seed used in sampling (42). |

## `cross_pudf_summary.csv`

| Column | Type | Description |
|---|---|---|
| `scope` | object | Aggregation population: overall or one tier. |
| `n` | int64 | Number of sentences included. |
| `mean_unicode_word_count` | float64 | Mean Unicode word count. |
| `mean_source_token_count` | float64 | Mean source-token count. |
| `mean_target_token_count` | float64 | Mean target-token count. |
| `mean_target_token_to_word_fertility` | float64 | Mean target tokens per word. |
| `mean_target_source_token_ratio` | float64 | Mean target/source token ratio. |
| `mean_target_surface_nonoverlap_proxy` | float64 | Mean non-overlap proxy. |
| `mean_b_tilde` | float64 | Mean unstandardized b_tilde. |
| `mean_b_tilde_zscore` | float64 | Mean global z-scored b_tilde. |
| `spearman_word_count_vs_target_tokens_rho` | float64 | Spearman rho for word count vs target token count in scope. |
| `spearman_word_count_vs_target_tokens_pvalue` | float64 | Two-sided p-value for the within-scope Spearman correlation. |
