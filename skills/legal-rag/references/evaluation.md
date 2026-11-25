# Facit, panel labelling, metrics, paired tests, guard sets, answer check, determinism

Evidence behind the `legal-rag` skill. Extracted 2026-11-25 from the AI Regelkompas / Saga project notes.
Path shorthands: `N/` = `/home/lars/source/ai-compliance-dk-wt-notesweep/notes/` (also in the ai-ops-dk/ai-compliance-dk repo under
`notes/`), `C/` or `CQ` = `~/.cache/saga-chunk-quality/` (local artefacts, may disappear), `S/`, `saga:` or `RO` =
a Saga worktree at origin/main (`docs/eval/`, `docs/operations/ROLLOUT-4B-2048.md`, `deploy/k8s/config/`).
Status tags: measured + adopted / measured / negative result / hypothesis. Numbers are from the cited runs;
re-measure before relying on them for a different corpus or model.

# Learnings: how to evaluate legal RAG retrieval reliably

All of this comes from reading notes and artefact reports; I ran nothing. Paths: `N/` = `/home/lars/source/ai-compliance-dk-wt-notesweep/notes/`, `C/` = `~/.cache/saga-chunk-quality/`. Saga eval docs were read from the worktree `/home/lars/source/saga-wt-drop-1024-hnsw/docs/eval/`, because the main Saga checkout has no `docs/eval/` (it is on an old branch). Whether that worktree matches `origin/main` is [INFERENCE].

Main points:
- The pooled, panel-graded facit plus paired tests, a guard set and an answer-level veto is the method that was measured and adopted.
- A catalogue facit on its own was measured to be invalid.
- LLM judges are diagnostics only, never the target metric.
- Determinism comes from frozen hashes, memo/replay, corpus fingerprints and an offline socket guard.

## A. Gold / facit construction

1. **Don't score against a catalogue (locator) facit alone; most of its "misses" are relevant chunks.**
   - Why: a judge check of keyed misses found relevant-but-not-in-the-key at 0.75–0.91 on sets a/d and 0.475–0.55 on set c. Adjusted hit@5 rose from 0.39–0.51 to 0.74–0.95 (`C/20261119/staging-eval-v1/keycheck/judge-report.md`; summarised in `N/2026-11-23-104639-retrieval-naeste-fase.md`).
   - The catalogue facit also has 0 of 1,356 targets outside the index, so it can never reveal corpus holes. 50 seed sources were missing from `ai-regler-4b` (`N/experiments/retrieval-r1.md`, "Diagnose E").
   - Status: measured + adopted (catalogue facit demoted to a secondary metric).
   - Caveat: the set b facit was never checked.
2. **Build the facit by pooling: the union of the chunks each cell selects, before unit expansion, over every planned arm plus production. Grade each (question, chunk) pair 0/1/2.**
   - Grades: 0 = irrelevant; 1 = relevant (context, partial answer, a neighbouring provision an answer might plausibly cite); 2 = governing/best source that directly answers a central part.
   - Why: round 1 pooled 427 questions into 5,972 pairs (mean 14, max 24 per question) and got 1,383 grade-2 pairs after freezing (`retrieval-r1.md`).
   - Status: measured + adopted (G1).
3. **Calibrate each panel tier on controls before labelling, and keep only tiers that score ≥ 95 %.**
   - Controls: positives = catalogue hits on set c (expected grade ≥ 1); negatives = chunks from unrelated acts (expected 0).
   - Why: 106 positive + 120 negative controls. Positive/negative accuracy was default 0.962/0.975, smol 0.962/0.967, slow 0.953/0.967, so all three passed. Full agreement on controls 96.5 %.
   - The "control failures" were mostly the control being wrong (e.g. an Administration Act § 27 hit for a private company), not the panel.
   - Status: measured + adopted.
   - Caveat: the deviations were inspected by hand; positive controls inherit catalogue errors.
4. **Consensus rules:**
   - nDCG gain = mean panel grade.
   - "Grade 2" needs a majority.
   - Pairs with spread 2 (0 vs 2) go to a blind adjudicator.
   - Fewer than 2 valid grades = unrated, never 0.
   - Why: inter-tier agreement was default–slow 0.917, default–smol 0.783, smol–slow 0.796; full agreement 0.75 (smol gives more 2s); 8 spread-2 pairs. Sample check panel vs adjudicator: 34/42 (0.81), no two-step errors; spread-2 pairs 4/8 (`retrieval-r1.md`).
   - Status: measured + adopted.
   - Caveat: the 50-pair review was delegated to a frontier model (declared Opus) instead of Lars, possibly the same model family as the panel, so independence is limited.
5. **Freeze the labelling protocol and the facit with sha256 before any cell is scored.**
   - Frozen protocol: prompt, panel, consensus rule (`freeze-v1.json` `d274cca5…`, `facit-v2.json` `66365896…`).
   - Status: adopted (also the K18 precedent, `N/experiments/k18-modelpanel.md`).
6. **Label new chunks (outside the pool) after the run and before scoring, with the same frozen panel/prompt/freeze file, as a frozen addendum. Require 0 unrated selected chunks before a cell is scored.**
   - Why: addendum-1 had 782 pairs (90 grade-2); addendum-2 had 1,398 pairs (132 grade-2; 5 spread-2 pairs, all adjudicated to 1); addendum-3 was empty and frozen anyway (`retrieval-r2.md`, `retrieval-r2b.md`). The labeller script checks the hashes.
   - Status: adopted.
   - Caveat: when the pool grows, IDCG grows, and a cell's own numbers fall. Y10 went 0.739 → 0.725 nDCG@6 with an unchanged selection. Only compare cells scored under the same facit version.
7. **Make the panel reference reproducible: hash the content, not only the metadata, and check the model identity per reviewer.**
   - Why: in K18, draft points hashed only metadata, so 10 fixes could not change any score; fixed in k18-3 by hashing the body text.
   - The first round-3 spawn got shifted models (fable ran astra, …); caught from the session logs and rerun one model at a time with a log-verified model.
   - K18 consensus rule: same verdict from ≥ 3 of 4 models; 2–2 = unresolved, never approve or reject. Scores 85.5 → 94.6 → 98.7 → 99.7 % (`N/2026-11-12-163600-genoptag-k10-k17.md`).
   - Status: adopted.
8. **Hold out whole acts/documents with a result-blind hash split; report held-out, never tune on it.**
   - Why: E0 split on sha256(`e0-split-v1:<act>`) until ≥ 30 % of targets were held out (30 of 92). E1c's dev gain for rule-card text did not show on held-out (`saga-wt-drop-1024-hnsw/docs/eval/e0-retrieval-baseline.md`, `e1c-two-pools.md`).
   - Status: adopted in the E-series; the R-series used sets instead of a split.

## B. Metrics

9. **Primary metrics, computed on the list before unit expansion, per set and overall:**
   - nDCG@6 with linear gain = consensus grade, IDCG from all rated pairs of the question;
   - g2_recall = share of the question's pooled grade-2 pairs that are selected;
   - any_g2 = at least one grade-2 among the selected.
   - Secondary: catalogue any_gold/target_recall, prompt tokens, refusals, `rerank_degraded`.
   - Status: adopted (G3).
   - Caveat: scoring before expansion counts a chunk as lost even when unit expansion still serves it (AI Act art. 2 body, chunk 53622, in `retrieval-r2b.md`).
10. **Use span/document-level hits, not only heading-chunk hits, when the gold is a provision.**
    - Why: span-hit barely changed a near-zero result (blind2 span-recall@6 0.35 %). Document-hit @6 was 13–16 % (an upper bound) (`N/experiments/saga-retrieval-metric-validation.md`).
    - E0 counts every overlap copy of a heading chunk (K2 lesson).
    - Status: adopted in E0.
11. **Measure the route the product actually calls, with its real query construction and the in-force version as target.**
    - Why: a benchmark with 99.7 % locator coverage and recall@6 = 0 (`N/experiments/saga-censor-retrieval-recall.md`) turned out to measure no product route: the sidecar only calls `/v1/answer` on `ai-regler`.
    - Status: negative result → rule adopted (E0 basis).

## C. Statistics and decision rule

12. **Pair by question:**
    - sign-flip permutation, 10,000 resamples, seed 20261123, for nDCG/g2_recall;
    - exact McNemar for binary metrics (any_g2, grade-2 cited);
    - two-sided binomial for judge preference; α = 0.05.
    - Status: adopted.
    - Caveat: the 15 t items are combinations of 4 topics, strongly correlated, but treated as independent.
13. **Preregister the cells, the adoption rule and the veto in the note before each run.**
    - Adoption rule: a gain in ≥ 1 set (or overall) AND no significant regression (p < 0.05) in nDCG@6, g2_recall or any_g2 in any set; the guard set t must not regress.
    - Logged as "registered before start" entries in the notes (r2b frozen as `freeze-r2b.json` `d0a7bf64…`).
    - Status: adopted.
14. **Keep a guard set for secondary routes (t = 15 combinations of the sidecar's 4 fixed topics sent as `retrievalQueries`).**
    - Why: it caught real regressions. A1 (rewrite only) gave t nDCG −0.19 and g2_recall −0.24.
    - The 4B reranker (R4) won overall (+0.030, p 0.0001; c +0.101) but t fell 0.962 → 0.855 (p 0.0014), which vetoed it.
    - Diagnosis: the loss came from reordering within topics, not from the topic gate. A single 334-character tail chunk explained about 37 % of the loss.
    - The topic path without a reranker (R4s) then passed: +0.034 overall, t unchanged.
    - Status: measured + adopted.
15. **Run a combination cell of the winners; don't assume effects add up.**
    - Why: D0 (keyword arm off) +0.007 alone, but Δ −0.0003 (p 0.91) on top of A3, so it was dropped (it needs code for no gain).
    - Status: adopted.
16. **Include a same-budget control when an arm adds places or tokens.**
    - Why: in E1d, part of the "binding on top" gain was simply 3 more places (B1-9 control) (`e1d-binding-on-top.md`).
    - B10 bought g2_recall 0.719 → 0.877 for +4.4k prompt tokens; report the cost alongside.
    - Status: measured.

## D. Answer-level check (G5)

17. **Check the retrieval winner end to end against the baseline before rollout, with the production generator, and veto on any significant regression.**
    - Setup: 160 public + 60 seeded b questions (`answer-sample-v5.json`), generator qwen3.6.
    - Mechanical metrics: answered; cites ≥ 1 grade-2 source; citation precision (cited sources with grade ≥ 1 / gain ≥ 0.5).
    - Blind pairwise judge as a secondary signal.
    - Veto: significant regression in "claims without coverage" or "grade-2 cited".
    - Why (Y10 vs P0): grade-2 cited 0.877 → 0.945 (p 0.004), precision 0.896 → 0.929 (p 0.03), judge 124/84 (p 0.007).
    - Why (R4s vs Y10): precision 0.894 → 0.930 (p 0.006); grade-2 cited 0.950 = 0.950; the judge leaned towards Y10 (113/90, p 0.12, not significant).
    - Status: adopted (saga#191, #196).
    - Caveat: the judge is one session model scored against a panel-built reference; claim coverage moved 0.763 → 0.786 (n.s.).

## E. LLM judges

18. **Never use an LLM judge (or Ragas) as the target metric; use mechanical metrics against a frozen facit, plus a jurist where needed.**
    - Why: in the Opus re-review there was 0/72 disagreement between contexts on the same text, yet SF2's byte-identical answers were judged opposite ways under two presentations (0·0·18 vs 18·0·0, driven by one core point). Sonnet differed again (`N/experiments/saga-opus-rereview.md`).
    - Rule outcome: `LLM_REVIEW_NOT_STABLE_MECHANICAL_AND_JURIST_ONLY`.
    - Status: negative result → rule adopted (B8).
    - A frozen panel verdict (K18, facit v2) is allowed; a live judge is not.
19. **Qualify any judge on unseen sealed controls before use.**
    - Why: GLM was 28/28 on dev but 41/45 on sealed controls, so not qualified. Gemma v2 was 27/28 and passed on missing neighbour context (`N/2026-11-17-144417-e5-inputdiagnose.md`).
    - Status: negative result.

## F. Noise floor and determinism

20. **Measure the instrument before you measure candidates: k replicates per distinct request, and report the replicate spread as the threshold a candidate must beat.**
    - Why: at temperature 0 there were 2 distinct outputs per request. Main status was saturated (floor/ceiling); only core-point counts (spread 0–2) and extraction recall (spread 0–1) had resolution (`N/experiments/saga-noise-floor.md`).
    - Status: measured + adopted (k = 5 in E0/E9).
21. **Size repeats per level.**
    - Retrieval: E0 had a 3-repeat spread of 0.0; under exact scan the spread was ≤ 0.16 point against 2-point decision margins, so suite v2 runs one retrieval pass and treats < 0.2 point as noise.
    - Answers: keep 3 repeats; the false-answer rate spread 6–13 points per repeat (`e0-retrieval-baseline.md`, `e1b-annex-omission.md`).
    - Status: adopted.
22. **Record non-deterministic helper outputs once and replay them in every cell.**
    - Memoise: helper-model rewrites (Gemma was not repeatable at temperature 0), embeddings per exact input, reranker answers per model (never across models).
    - Hard-fail on a memo miss and block non-loopback sockets for offline runs.
    - Why: replay reproduced 427/427 identical selections (including rerank scores) and Y10 reproduced round 1 exactly (nDCG 0.739).
    - Status: adopted.
23. **Fingerprint the corpus (md5 over text + metadata + vector and over document rows) at start and end; scratch copy, production read-only.**
    - Why: E0's `ai-regler` was re-chunked mid-run by the 03:00 refresh cron, which made its numbers uncertain.
    - Status: adopted.
24. **Never score silent fallbacks.**
    - Why: the reranker rejected pairs over 2048 tokens and Saga served RRF order, so 450/2,262 E0 records were `degraded`.
    - Rule: flag `rerank_degraded`, retry transient errors, verify reranker identity via `/v1/models` before and after each phase (reject a phase on the wrong n_params).
    - Status: adopted.
25. **Check that the ANN filter doesn't truncate candidate lists.**
    - Why: one HNSW index over all collections, filtered after the scan, gave 810/2,262 lists with < 30 candidates and reordered up to 9 % of lists. Fixed by exact scan (`e1-validity-filter.md`).
    - E5's model comparison was inconclusive because 286 lists had unmatched inputs (`N/2026-11-16-182718-e5-fuld-suite-frys.md`).
    - Status: negative result → fix adopted.

## G. Local engine validation

26. **Before replacing production scores with local ones, validate local against production on fixed pairs with a frozen rule: max |Δ| ≤ 0.10 and the same top-1 in every question.**
    - Why (30 pairs from the facit, 6 questions):
      - local CPU 4B reranker vs GPU: max |Δ| 0.057, Pearson 0.998, top-1 6/6;
      - embedder: cosine ≥ 0.9994;
      - self-converted 4B GGUF vs transformers: Spearman 0.993;
      - q8_0-KV shifted scores by up to 0.033;
      - mid-range scores drift most (≈ 0.06); scores near 0 or 1 match within 0.001.
    - Status: measured + adopted (`retrieval-r2.md`, `retrieval-r2b.md`).
    - Caveat: the transformers reference itself correlates only 0.23 (0.6B) / 0.41 (4B) with facit gain. Engine fidelity is not relevance.

## Open questions and failures

- Set b's catalogue facit was never checked.
- The judge leaned (n.s.) against the adopted R4s.
- Adjudicator independence is unclear (same model family as the panel).
- The guard set is correlated and has n = 15.
- The 4B topic gate was calibrated on only 6 negatives (θ = 0.542 changed nothing).
- Round 2 ran with a deviation (q8_0-KV instead of the preregistered f16-KV).
- No jurist has validated the M2 flags (the "kill line") or the K1 version map.
- The Ragas gate in Saga CI still uses an LLM judge (smoke run on 5 questions on PRs; floor-gated full run nightly), which conflicts with item 18.

**Checks to run:** none — this was read-only extraction.
