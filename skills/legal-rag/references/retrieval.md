# Embedder, query construction, hybrid/lookup arms, reranker, floors, top_k, topic path

Evidence behind the `legal-rag` skill. Extracted 2026-11-25 from the AI Regelkompas / Saga project notes.
Path shorthands: `N/` = `/home/lars/source/ai-compliance-dk-wt-notesweep/notes/` (also in the ai-ops-dk/ai-compliance-dk repo under
`notes/`), `C/` or `CQ` = `~/.cache/saga-chunk-quality/` (local artefacts, may disappear), `S/`, `saga:` or `RO` =
a Saga worktree at origin/main (`docs/eval/`, `docs/operations/ROLLOUT-4B-2048.md`, `deploy/k8s/config/`).
Status tags: measured + adopted / measured / negative result / hypothesis. Numbers are from the cited runs;
re-measure before relying on them for a different corpus or model.

I pulled about 45 learnings out of the assigned notes, the Saga config files on disk and the docs they cite. Every number below comes from a note or a config comment; I did not re-run anything.

What is in production now is the 4B embedder at 2560 dims with a Danish query instruction and the whole question embedded. The 4B reranker runs on the main question but not on the topic path, `top_k` is 10, there is no rewrite or multi-query, provision lookup merges via RRF, and a raw dense floor of 0.50 is set.

Two things to know about the sources:
- **Config files.** The Saga checkout at `/home/lars/source/saga` has an old working tree whose `deploy/k8s/config` predates the 4B switch. I read the current config from the worktree `saga-wt-s3measure`, which sits on the deployed commit (`ea8c845`, code `e09d212`).
- **Path shorthand.** `N/` = `/home/lars/source/ai-compliance-dk-wt-notesweep/notes/`, `S/` = `saga-wt-s3measure/`, `C/` = `~/.cache/saga-chunk-quality/`.

## A. How to measure
1. **Measure the route the product actually calls.** Evidence: a benchmark of four topic queries on the `regelkompas` collection got chunk-recall@6 = 0/1671. It matched no real route: the sidecar only calls `/v1/answer` on `ai-regler`. Source: `N/experiments/saga-retrieval-metric-validation.md`. Status: negative result, lesson adopted (it became the basis of E0). Caveat: the gold set was derived from model verdicts, not a lawyer.
2. **Don't trust a citation-derived gold set without checking it.** Evidence: an external judge found 75–90 % of sets a and d "misses" were relevant but not in the gold set; for set c it was 48–55 %. Source: `N/2026-11-17-144417-e5-inputdiagnose.md` (keycheck). Adopted: "facit v2", a pooled panel grading (0 irrelevant / 1 relevant / 2 governing source), frozen by hash before scoring. A model panel was only used if it scored ≥ 95 % on positive and negative controls; all three scored 0.953–0.975. A blind adjudicator agreed with the panel 0.81 of the time. Source: `N/experiments/retrieval-r1.md`. Caveat: the panel and the adjudicator are possibly the same model family.
3. **Use nDCG@6, any-grade-2 delivered and grade-2 recall, paired per question.** Tests: sign permutation with 10,000 resamples, exact McNemar. Adoption needs a gain in at least one set, no significant regression in any set, a guard set t that does not regress, and then an answer-level check (blind pairwise judgement plus "claims without coverage"). Status: measured and adopted; it is the protocol for rounds 1, 2 and 2b. The guard set caught a regression that overall numbers hid (R4, see 6.25).
4. **Measure at provision level as well as document level.** Evidence: on the deployed setup R@10 from rule card to provision is 51.4 %, but at document level it is 88.8 %. In 12 of the 52 misses only guidance or a draft came back. Source: `N/experiments/s3-maaling-4b.md`. Status: measured; the S3 gate (≥ 95 %) is not passed.
5. **Align probe depth with serving depth.** Evidence: adding 48 sources pushed gold spans out of `max_hits` 6 (probes 0.417); setting it to 10, the served depth, gave 0.517. Source: `N/2026-11-23-104639-retrieval-naeste-fase.md`. Status: adopted.

## B. Embedder
6. **Use Qwen3-Embedding-4B, not 0.6B.** Evidence, raw single query without reranker on sets a+c+d (n=160): hit@5 rose from 0.306 to 0.575–0.581 and hit@20 from 0.594 to 0.744–0.762. On set b (long questions) hit@5 went from 0.098 to 0.642–0.770. Source: `N/2026-11-17…md` (arms-4b, `C/…/staging-eval-v1/arms-4b/results/report.md`). Status: measured and adopted (`ai-regler-4b`). Caveat: at first, answer-level tests showed no difference, because rewriting and decomposition hid the gain (see 13).
7. **Store the native 2560 dims and search them by exact float32 scan.** Evidence on a+c+d: 1024, 2048 and 2560 dims cannot be told apart. On long questions through the answer path, whole question: any-gold 0.72 / 0.78 / 0.80 at 1024 / 2048 / 2560 (2560 vs 1024 +0.083, p=0.0002). Exact float32 took 26–33 ms against 98 ms for halfvec. Sources: `S/deploy/k8s/config/embeddings.yaml` comment, `N/2026-11-17…md`. Status: adopted. Caveat: the model ignores the `dimensions` parameter, so narrower widths are a Matryoshka prefix renormalised client-side.
8. **Q8_0 is enough; Q6_K is no worse.** Evidence: no measurable difference (a+c+d hit@5 0.575 for Q6_K vs 0.562 for Q8_0). Status: Q8_0 adopted, since the owner wanted at most Q8 and maximum precision.
9. **Probe the real token limit.** Evidence: the servers announce a 4096 context but reject 4096 and 4097 tokens and accept 4095, for both embedder and reranker. Source: `N/2026-11-17…md` (`serving-boundary-results.json`). Status: adopted in the contracts (4095).
10. **An HNSW index with a collection filter applied after the scan silently starves the pool.** Evidence: with ef_search 40 over 27k chunks, expert collections got a median of 17–19 of 30 candidates, minimum 3. Exact scan gave 30 of 30. Source: `N/2026-11-13-231800-e1-opfolgning.md`, finding 7. Status: fixed (the dense arm always uses exact scan, saga#169).

## C. Query construction
11. **For 4B, embed queries with the Danish legal instruction; give documents no prefix.** The prefix is the Qwen3 `Instruct:…\nQuery:` format asking for provisions in Danish laws, EU acts and authority guidance.
    - Evidence on 4B (round 1): removing it (C0) gave nDCG@6 −0.074 and any_g2 −0.063.
    - Evidence on 0.6B staging without reranker: R@5 0.093 with no instruction, 0.098 with the English default, 0.127 with Danish legal.
    - Sources: `N/experiments/retrieval-r1.md`, `N/2026-11-17…md`.
    - Status: measured and adopted on the 4B descriptors only.
    - Caveat: on 0.6B **with** the reranker, the production CI gate fell from 0.538 to 0.477 recall@10, so 0.6B has no prefix (`embeddings.yaml` comment). Adding a prefix needs no re-embedding, but the contract must be re-frozen.
12. **Don't add a separate instruction for case descriptions.** Evidence: C2 gave nDCG −0.049, and −0.097 on set b. Source: `N/experiments/retrieval-r1.md`. Negative result.
13. **Don't use auxiliary-model rewrite or decomposition with a strong embedder.** Evidence:
    - Raw single query 0.606 against 0.525 through the rewritten path on a+c+d.
    - Round 1 A3 (no rewrite, no decomposition): nDCG@6 0.717 → 0.756 (p<0.001); a +0.11, d +0.19, t +0.11.
    - A1 (rewrite only) damaged the guard set t (nDCG −0.19).
    - Rewriting helps 0.6B (set b 0.12 → 0.27) but hurts 4B (set b 0.68 → 0.50).
    - Sources: `N/experiments/retrieval-r1.md`, `N/2026-11-17…md` (pathret-v1).
    - Status: adopted (`query_rewrite`/`multi_query: false`).
14. **Embed long questions whole; compact only when they exceed the embedding context.** Evidence: set b uncompressed 0.72–0.80 against compressed 0.51 (+0.20 to +0.30, p<0.001). Answer test on 60 long questions: "expected passage cited" 0.25 in production vs 0.65 with the recommended setup. Source: `N/2026-11-17…md`. Status: adopted (`RETRIEVAL_QUERY_COMPACTION=when_required`, search limit 1,024 cl100k tokens).
15. **Compaction is fragile.**
    - A 256-token output budget caused deterministic 503s on 26 of 192 long questions; the budget was raised to 1,536.
    - Even at temperature 0 the aux model is not repeatable: 152 of 166 compactions came back with different text between runs.
    - 17 of 192 were still refused as `too_long`.
    - Source: `N/2026-11-17…md`; `config.py` comment.
    - Status: fixed and adopted. Lesson: record aux outputs once and replay them in every eval cell.
16. **Short reference queries ("title + act + article") do not find the provision.** Evidence: span hit@6 1/25 against 6/25 for the baseline, although document hit rose to 41–47 % from 31 %. Source: `N/experiments/saga-explain-query-construction.md`. Negative result (on 0.6B). Hypothesis: the aux model's decomposition of queries of 12+ words dilutes them.
17. **Broad topic texts retrieve guidance, not provisions.** Evidence: only 7–15 % of top-6 came from the target acts; compressed review text gave M1 1.3 % (K7), 26.9 % on 4B (S3). Locator-first retrieval (looking provisions up by heading) gave explain M1 100 % against 14.6 % (K9). Sources: `N/experiments/k7-review-soegetekst.md`, `N/experiments/k5-k9-explain.md`. Status: locators adopted for known provisions; per-rule queries (E4) still open.

## D. Hybrid search: keyword arm, BM25, lookup, RRF
18. **A `plainto_tsquery` keyword arm is dead for natural questions.** It requires every word in the same chunk; 82 % of questions got an empty arm, and 100 % in sets a, b and d. "Hybrid" was in practice dense-only. Source: `N/2026-11-13…md`, `N/2026-11-17…md`. Measured.
19. **An "any word" keyword arm is not a fix at pool 30.**
    - On 0.6B: R@5 0.049 vs 0.093.
    - It helps at pool 100–300 (pool-hit 0.697 vs 0.563) and for short lookups (set c, binding pool 30: 10 → 31 %).
    - `ts_rank` beats `ts_rank_cd`. It costs 0.2–0.5 s per search and seconds for 85-word questions, so bound the query.
    - Sources: `N/2026-11-14…md`, `config.py` (`retrieval_sparse_mode`, default `all_terms`).
    - Status: measured, not adopted.
20. **Removing the dead keyword arm gives nothing once rewriting is off.** Evidence: D0 alone gave nDCG +0.007, but X10 = Y10 + D0 gave Δ −0.0003 (p 0.91). Not adopted (it would need a code change for no gain).
21. **BM25 does not replace the keyword arm.** Evidence: hit@5 0.450 against 0.556 (p=0.009). Source: `N/2026-11-23…md` (`retrieval-lexical-v1`). Negative result.
22. **Add a provision-lookup arm when the user's question names an act and article; merge it as an extra RRF list.**
    - Evidence: hit@5 0.556 → 0.887, hit@6 0.606 → 0.906, hit@20 0.975, never a loss; set c 0.418 → 1.00.
    - Sets a and d are unchanged, because "art. 30" without an act cannot be resolved. There was one wrong resolution (an amending regulation's article number).
    - Only the original question is parsed; `rrf` is preferred over `pin`.
    - Sources: `N/2026-11-17…md`, `S/docs/operations/ROLLOUT-4B-2048.md`.
    - Status: adopted (`RETRIEVAL_PROVISION_LOOKUP=rrf`). Caveat: not measured together with the reranker, and the CI gate does not exercise it.
23. **RRF parameters in use:** dense_top_n and sparse_top_n 30, `rrf_k` 60, rerank_top_n 30, multi-query fuse_top 20, union_cap 40 (`config.py`). Not ablated. Note that RRF scores are rounded to 6 decimals and there is no secondary ID sort; that is a likely source of non-reproducibility (see 10.40).

## E. Pool depth and candidate pools
24. **Dense recall saturates slowly.** Evidence: gold chunk within 30 / 100 / 300 / 1000 candidates was 32.5 / 57.1 / 74.0 / 90.9 % (`regelkompas`, 0.6B). Long recorded questions stayed under 3 % even at 300. Source: `N/2026-11-13…md`. Measured on 0.6B; superseded by 4B (pool-hit@30 0.79).
25. **A wider mixed pool does not help the 0.6B reranker.** Evidence: provision in served top-6 at pool 30 / 100 / 300 was 9.1 / 11.7 / 9.1 %, while pool coverage rose from 33 % to 74 %. 100 pairs per call took 11–15 s. Source: `N/2026-11-14…md` (Saga `docs/eval/pool-depth.md`). Negative result.
26. **Two pools (binding text vs the rest, 3 slots held for binding): not adopted.**
    - The 15+15 arm raised rule-card recall@6 from 9.1 to 23.4 % and from 6.5 to 13.0 %, but tripped the guidance stop rule, and held-out showed no gain.
    - 30+30 was deployed (owner's deviation) and rolled back after false answers on abstention probes rose from 10/48 to 13/48.
    - A second run of the unchanged baseline config also gave 13/48 (an equal shift between runs), so the stop rule could not separate the effect from noise.
    - "Binding on top" (E1d) gave 15/48.
    - Final config: `candidate_pools: mixed`. Source: `N/2026-11-14…md`.
    - Negative result. Lesson: the 16 abstention questions ×3 repetitions are not independent samples; measure run-to-run variance before setting stop rules.

## F. Reranker
27. **0.6B reranker after the 4B embedder hurts.** Evidence: R06 vs Y10 nDCG@6 0.728 → 0.702 (p=0.0005); a −0.14, t −0.15. Source: `N/experiments/retrieval-r2.md`. Negative result.
28. **4B reranker beats 0.6B clearly and Y10 overall, except on the topic path.** Evidence: R4 vs Y10 +0.030 nDCG@6 (p=0.0001); c +0.101, g +0.072, b +0.017; but t −0.106 (p=0.0014). R4 vs R06 +0.055. Source: `N/experiments/retrieval-r2.md`. Status: measured; adopted only as R4s (see 6.32).
29. **Never rerank with a compressed question while the embedder saw the whole one.** Evidence on 4B, long questions: expected passage cited 0.65 without the reranker vs 0.42 with it on compressed text; any-gold through the path 0.51 → 0.38. Questions over the search limit now skip the reranker. Source: `ROLLOUT-4B-2048.md`. Adopted.
30. **A plain task instruction to the reranker gives no gain.** Evidence (E5 step 1, 0.6B on CPU): 0 / −1 and −1 / −3 hits against the required +4. Source: `N/2026-11-14…md`. Negative result.
31. **The 0.6B reranker is saturated.** Gold chunk median score 0.95, but a median of 89 chunks per query score ≥ 0.9. On P15's guidance pairs, scores 0.997–0.9998 separated nothing. Measured.
32. **E5 pilot, 4B vs 0.6B reranker on the same 0.6B candidates (mixed pool 30, dev):**
    - Rule-card hits 5 → 14 of 77 (`ai-regler`) and 7 → 17 of 77 (`regelkompas`).
    - Held-out: 3 → 4 and 5 → 4 of 30, i.e. no consistent gain.
    - Median GPU time per 60 candidates: 10.5 s (0.6B) against 16.6 s (4B).
    - The full-suite rerun was inconclusive: 286 of 816 inputs differed between arms (230 only in order, 56 in membership).
    - Source: `N/2026-11-14…md`, `N/2026-11-16-182718-e5-fuld-suite-frys.md`, `N/2026-11-17…md`.
    - Lesson: freeze candidate inputs and vectors, and feed both rerankers identical ordered input.
33. **Self-convert the 4B reranker GGUF and validate it against transformers.**
    - No official GGUF exists; early third-party conversions score wrongly.
    - Own Q8_0 conversion: Spearman 0.993 (CPU) and 0.995 (GPU) against the transformers reference.
    - It only fits with q8_0 KV cache, ubatch 256 and flash attention on (4,576 MiB; f16 KV ran out of memory). q8_0 KV moves scores by up to 0.033.
    - Latency per call: p50 6.3 s and p95 11.5 s, against 2.6 s for 0.6B (client timeout 60 s).
    - Pairs over 4,095 tokens get HTTP 400 and fall back to RRF order; score that fallback honestly.
    - Source: `N/experiments/retrieval-r2.md`. Measured and adopted.
34. **Reranker scores barely track graded relevance.** Evidence: the transformers reference against the facit gain on 30 pairs gave Spearman 0.23 for 0.6B and 0.41 for 4B. Open: whether the reranker can be trusted as a gate.

## G. Gates and floors
35. **D1 dual floor (0.6B reranker era): rerank 0.20 OR dense 0.50; retrieval counts as empty only when both are missed.**
    - 0.20 sits in an empty band between 0.136 (highest caught hard negative) and 0.318 (weakest real question) across 42 golden queries; it refused 4 of 5 hard negatives with 0 false refusals.
    - The 0.50 dense fallback exists because the earlier bge-reranker compressed cross-lingual scores.
    - Source: `S/src/saga/gateway/config.py` comments. Adopted.
    - Caveats: only 5 hard negatives. Without a reranker D1 never runs. On 4B, 0.50 would be calibrated for applicability, but changed no outcome (0/126), so it was left at 0.20 (`N/2026-11-24-170539…md`).
36. **Without a reranker, use a dense floor on the raw question vector.** Evidence (4B d2560): floor 0.50 on the raw vector refused 0/432 positives and 41/45 negatives, including 5/5 hard. On the vector after rewriting it refused only 25/40. Margin to the lowest positive is only 0.02. Sources: `ROLLOUT-4B-2048.md`, `collections.yaml` (`dense_floor: {floor: 0.50, basis: raw}`). Adopted. Caveat: small negative set; recalibrate whenever the corpus, model or rewrite prompt changes.
37. **The topic gate (best of the first N candidates vs the topic's own text ≥ 0.70) is model-specific and becomes irrelevant under 4B.**
    - It was calibrated on 0.6B over 14 topics, of which only 6 were off-topic; dagpenge 0.997 and moms 0.929 are not caught.
    - Under 4B, all four t topics score 0.973–0.990.
    - A 4B-recalibrated θ = 0.542 left the result unchanged (t still −0.106).
    - Sources: `config.py` comment, `N/experiments/retrieval-r2b.md`.
    - Negative result for recalibration (variant (a) rejected).

## H. Topic path, slots, top_k
38. **On the multi-topic path (`retrievalQueries`), skip the reranker; keep it on the main question.**
    - Diagnosis: the 4B reranker reordered inside each topic (top-8 overlap with Y10 only 2–5).
    - One 334-character tail chunk of AI Act art. 2 (grade 1, rerank 0.990) outranked art. 6 (grade 2, 0.987) in all 8 ai-scope questions and alone explains about 37 % of the loss.
    - R4s: t unchanged, overall +0.034 (p=0.0001). Answer check: citation precision 0.894 → 0.930 (p=0.006), no veto.
    - Source: `N/experiments/retrieval-r2b.md`.
    - Adopted (saga#196, `topic_reranker: false`). Caveat: the blind judge leaned towards Y10 (113 vs 90, p=0.12, not significant). Lesson: short chunk tails get inflated reranker scores.
39. **Serve 10 sources, not 6.** Evidence: B10 any_g2 0.909 → 0.953 and g2_recall 0.719 → 0.877 for +4.4k prompt tokens (median 14.2k, p95 20.6k, cap 32,768). Answer check: cites a grade-2 source 0.877 → 0.945 (p=0.004); blind judgement 124 vs 84 (p=0.007). Top 8 gave g2_recall 0.812. Adopted (`top_k: 10`).
40. **Topic slots:** each topic gets `max(top_k, topics×3)` slots, capped at 8 total (the consumer's validation limit), round-robin by rank (`config.py`). Not re-measured on 4B.
41. **Allocating evidence inside a fixed 6,000-character / 12-item answer budget did not work.** Target-blind, protection-bundle and role-complementarity allocators all kept losing protective conditions or exceptions (SF6) and never improved the missing items (SF2). Sources: `N/experiments/saga-target-blind-allocation.md`, `saga-protection-bundle-allocation.md`, `saga-role-*.md`. Negative results; that track is closed.

## I. Reproducibility and infrastructure
42. **Memoise everything per exact input:** aux outputs, embeddings and reranker answers per model. Fingerprint the corpus including the stored vector values. Use one REPEATABLE READ snapshot. Replays then reproduced 427/427 selections. Source: `N/experiments/retrieval-r2b.md`.
43. **Long DB sessions through `kubectl port-forward` stall silently** (the server waits for the client; idle timeout 4 h). Use an SSH route to the internal service, and close the pool before the tunnel. Source: `N/2026-11-17…md`.
44. **Lock the ingest images to the lockfile.** An unpinned `pypdf` 7.0.1 → 7.1.0 re-extracted 46 PDFs and contaminated a control arm. Source: `N/2026-11-13…md`.

## J. Open questions
45. These are not settled by the evidence:
    - The reranker together with provision lookup is unmeasured.
    - Re-calibrate the topic gate and slot allocation for 4B on a wider off-topic set (6 off-topic topics is narrow).
    - The dense floor rests on 40–45 negatives.
    - Rule-card → provision R@10 is 51.4 % and K7-M1 is 26.9 %, against targets of 95 % and 90 %. The plan's answer is structure-aware units (E2), exact identifiers (E3) and per-rule queries (E4).
    - Reranker passages near the 4,095-token pair limit (2048-token chunks of up to 3,772 tokens).
    - A fine-tuned reranker or embedder (E5 step 3 / E6) has not been tried.
    - Why short reference queries hit the right act but miss the provision is unexplained.
