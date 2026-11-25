# Editions, consolidated text, drafts, metadata, corpus management, verbatim citations

Evidence behind the `legal-rag` skill. Extracted 2026-11-25 from the AI Regelkompas / Saga project notes.
Path shorthands: `N/` = `/home/lars/source/ai-compliance-dk-wt-notesweep/notes/` (also in the ai-ops-dk/ai-compliance-dk repo under
`notes/`), `C/` or `CQ` = `~/.cache/saga-chunk-quality/` (local artefacts, may disappear), `S/`, `saga:` or `RO` =
a Saga worktree at origin/main (`docs/eval/`, `docs/operations/ROLLOUT-4B-2048.md`, `deploy/k8s/config/`).
Status tags: measured + adopted / measured / negative result / hypothesis. Numbers are from the cited runs;
re-measure before relying on them for a different corpus or model.

I've extracted the learnings below from your assigned notes, the Saga docs at `saga-wt-s3measure` and the cited cache artefacts. The `/home/lars/source/saga` checkout is about a month old and has none of these docs, so I read `origin/main` (`ea8c845`) from the `saga-wt-s3measure` worktree. Paths are relative to `notes/` unless they start with `saga:` (meaning that worktree) or `~`.

**Short answers to your key questions:**
- **Superseded editions:** mark the old text with `replacedBy` (which edition to read), not `inForceTo` (whether the act is valid). Drop annex copies at ingest and apply a hard per-collection filter. Superseded editions cited: 117 → 0, then 179 → 0 for annex copies, and 0 in S3.
- **Drafts:** `current` still lets drafts through. S3 counted 14 draft-guideline and 16 proposal citations in 111 answers, and the high-risk rule card retrieved only a draft. Only `current_adopted` removes them.
- **Seed list vs freeze:** compare the built index against the seed list after every rebuild. A gold set built on the index found 0 gaps while 48 sources were missing.
- **Verbatim citations:** apply the normalisation list in section F, then require exact wording. Verified citations went 35 % → 84.7 %.

### A. How to represent editions so superseded text is never cited
1. **Mark the superseded edition with `replacedBy` (the `source_uri` of the edition to read instead), not with `inForceTo`.** Why: the adopted act is not repealed, so `inForceTo` would be false. Before this, old and consolidated editions shared `actId`, `status: inForce` and `inForceTo: null` (0/97), so no filter could tell them apart. `supersedes` lists older acts (e.g. 95/46/EF), not editions. Result: texts with `replacedBy` cited 117 → 0. Sources: `experiments/e1-gyldighedsfilter.md`; `saga:docs/eval/e1-validity-filter.md`. Status: measured + adopted (saga#164). Caveat: the markers are a best reading of the K1 version map and are not legally approved.
2. **Validate `replacedBy` when the source list is loaded.** The target must be another entry in the same file, not the entry itself, and not itself replaced. For Retsinformation, the checker also requires that the old text is historic, that its "Konsolideret ved" lists the target, and that the target is `Valid`. A swapped pair gave MISMATCH on all three checks. Sources: `saga:docs/eval/corpus-metadata-proposal.md`; `saga:src/saga/ingest/sources/metadata.py`. Status: adopted.
3. **Keep superseded editions in the corpus and filter them; don't delete them.** Lookups that name a document (`locate`, `only`) bypass the filter by design. The applicability families pinned the adopted GDPR and would have returned nothing otherwise. Keeping them also makes rollback a config change and keeps version probes measurable. Source: `e1-gyldighedsfilter.md`. Status: adopted (also used for LBK 1183/2025 → 953/2026).
4. **A gap in the corpus beats any filter.** E1 gate 1 still failed: 48 other-edition citations (GDPR 24, CRA 21, MDR 3), because `ai-regler` held only the original texts and had no marker on them. Fix: add the consolidations and put `replacedBy` on the originals. Source: `saga:docs/eval/e1-validity-filter.md`. Status: measured, fixed later (B12, six consolidations).
5. **Missing metadata must exclude nothing ("unknown" is not "expired"). Leave unverifiable fields absent: not `null`, not guessed.** Retsinformation's `EndDate` follows the latest amendment and must not be used as `inForceTo`. The checker verified 435 fields; 235 could not be verified; 0 mismatched. Source: `saga:docs/eval/corpus-metadata-proposal.md`, `saga:docs/applicability-experts-corpus.md`. Status: adopted.
6. **Metadata schema (closed; unknown keys or values are rejected at ingest):**
   - `sourceType`: binding | guidance | standard | recommendation | proposal
   - `status`: inForce | adopted | proposal | draft
   - `territory`: EU | DK | FO | GL
   - `inForceFrom` / `inForceTo`: ISO date; `inForceTo` is the last valid day
   - `supersedes`, `replacedBy`, `omitAnnexes`, `regime`, `actId`, `actKey`, `framework` (core | screening), `edition` (e.g. "1. udgave oktober 2019"), `note`
   - Date rules: `inForceFrom` is when the main provisions apply. Use `status: adopted` while they don't yet apply (CRA until 11.12.2027). A Danish LBK uses the original act's commencement date.
   - Source: `saga:docs/applicability-experts-corpus.md`. Status: adopted.
7. **Version map, per act (K1):** current identifier, consolidation date, amending acts, pending proposals, application dates per provision, and evidence (URL, fetch time, SHA256). Catalogue statuses: current / original-act-only / outdated / ambiguous. Unversioned landing pages are always ambiguous. Result: 26 of 94 catalogue references pointed at a superseded or original edition (21 of them the AI Act). Source: `k1-versionskort.md` + `.json`. Status: measured; feeds E1 and hard negatives. Not approved by a lawyer.

### B. Consolidated text, annex copies, recitals
8. **For EU acts, ingest the consolidated Cellar text (`celex/0…-YYYYMMDD`) where one exists and is in force; otherwise the adopted text.** K3: 0 of 461 package links pointed to a consolidated version. K6: consolidated AI Act cited in 0/30 version answers. Sources: `k3-pakke-forpas.md`, `k6-prober.md`. Status: adopted.
9. **Check that the consolidation was ingested in full.** The old `ai-regler` doc 120 held only headings for the amended sections (lossy ingest). Source: K1 finding S2. Status: found, re-ingested.
10. **Drop annex copies of EU acts inside Danish laws at ingest (`omitAnnexes: true`, Retsinformation `<Bilag>`).**
    - LOV 2025/467 had 455 chunks: 7 were the law, 448 the adopted AI Act with its original dates. LBK 2024/289 had GDPR as an annex in 255 of 289 chunks. Both were tagged `binding`/`inForce` with no marker.
    - After E1 removed the adopted text, its freed slots went to the annex copy (42 → 69, 57 of them recitals), not to the consolidation (0 → 3/30).
    - E1b: annex copies cited 179 → 0 (served 283 → 0). Consolidated AI Act served 7/30, so gate 2 still failed; the slots went to guidance.
    - Sources: `2026-11-13-231800-e1-opfolgning.md`, `saga:docs/eval/e1b-annex-omission.md`. Status: measured + adopted (B11).
11. **Recitals: the consolidated text has none (0/313 chunks); the adopted text has 222/505.** 59 % of served adopted-AI-Act chunks were recitals. Decision: keep them out of search and bring them back as a labelled non-binding pool. Recitals help interpretation but create no obligations. Sources: e1-opfolgning; `search-diagnosis-source-review.md`. Status: decided; second half not implemented.

### C. Drafts, proposals, binding vs guidance
12. **Don't trust titles or model labels for legal status. Curate `status: draft` on draft guidelines and classify draft → `proposal`.**
    - Before K16, `classify_source` labelled the draft high-risk guidelines `guidance` (docs 70/71); after K16 all 8 drafts/proposals were `proposal`.
    - With no metadata, the fallback is title prefix ("FORSLAG"/"UDKAST"/"draft") → proposal. Then CELEX sector 0/3 + R/L/D → binding, sector 6 → case law (binding), sector 5 (e.g. COM proposals) → guidance in the fallback, unknown → guidance (conservative).
    - Sources: `k6-2-prober.md`; `saga:src/saga/gateway/applicability/evidence.py`. Status: adopted.
13. **Labelling alone doesn't fix answers.** Proposal marking was 72.2 % (K6) → 77.8 % (K6-2); the target is 100 %. Every answer that cited a draft was marked. The unmarked ones answered questions about drafts from binding text without saying the guidance exists only as a draft. Source: `k6-prober.md`, `k6-2-prober.md`. Status: negative result; open question.
14. **Use filter mode `current_adopted` for anything that feeds an assessment.** `current` (excludes replaced and expired texts) suits a chat bot that may answer about proposals, with a label. Drafts in `regelkompas` top 30 fell 15 → 0.
    - **S3 says drafts still get cited:** on `ai-regler-4b` with `current`, the draft high-risk guidelines were cited 14 times and `proposal` documents 16 times in 111 answers.
    - For the high-risk rule card, only the draft was retrieved. E1's aim "drafts never a basis" is not met on the answer bots.
    - Sources: `e1-gyldighedsfilter.md`, `experiments/s3-maaling-4b.md`. Status: `current_adopted` adopted for applicability; answer bots stay on `current`.
15. **Proposals (e.g. L 99):** set `sourceType`/`status: proposal`, `inForceFrom: null` (a proposed date isn't a date), and a title prefix "FORSLAG (ikke vedtaget)". They must never produce "does not apply", and are at most a signal or screening item. Record a SHA256 of each reading and re-check at every reading (1st, 2nd, 3rd) and at royal assent. After royal assent: `binding`/`adopted` until the commencement date, then `inForce`. Source: `l99-ai-hjemmelslov-import.md`. Status: hypothesis; not imported.
16. **Rank binding sources ahead of guidance only with an abstention guard.** E1c reserved 3 of 6 places for binding chunks. Governing document cited 34 → 63 %, but false answers on abstention probes rose 10 → 13 of 48 → rolled back. E1d (binding chunks added on top): 15 false answers vs 10 → not adopted. Source: `saga:docs/eval/e1c-two-pools.md`, `e1d-binding-on-top.md`. Status: negative result.
17. **Outdated guidance is a version leak `replacedBy` can't catch.** In K6, 14 of 20 date errors came from AI Act guidance written before amending act 2026/1744, which still says 2 Aug 2026. Six remain in K6-2. Source: `k6-prober.md`, `k6-2-prober.md`. Status: open, unsolved.

### D. Filter and scope mechanics
18. **Apply the filter inside every arm of the search (dense, keyword, provision lookup, both pools), and let `retrieve` read the collection's own setting, so no route can skip it.** With the filter on, use an exact dense scan. With HNSW `ef_search=40` and post-filtering, 809 of 2,262 lists had under 30 candidates; with an exact scan, 0. Latency: median 0.074 → 0.132 s. Source: `saga:docs/eval/e1-validity-filter.md`, b8 notesweep. Status: adopted.
19. **Build source scopes (`scopes.yaml`) as an exact `source_uri = ANY(list)` filter over one collection, with their own `validity_filter`. No silent fallback when a source is missing.** Applicability `scope: regelkompas` = `ai-regler-4b` + 97 sources + `current_adopted`, replacing a separate collection. Parity: 331/331 identical outcomes, 0 citations outside scope. Locate: 92/92 targets found. Unit tests keep the scope equal to the seed list. If the file isn't mounted, scoped calls return 503 (this happened). Source: `saga:docs/regelkompas-collection.md`, `locate-4b.md`. Status: adopted (saga#192, #197).

### E. Corpus management
20. **After every rebuild, compare the built index against the seed list, not against the gold set.** The gold set found 0 of 1,356 targets missing, because it was built on the index. Against the 188-URL seed list, 50 sources were missing from `ai-regler-4b`, including MDR, NIS 2 implementing regulation 2024/2690 and the key AI/GDPR guidance. 48 of them had been lost from the old `ai-regler` at step D. Cause (`[INFERENCE]`): the corpus freeze (v6–v8f) was built from a source list that predated the corpus merge. The 48 were excluded as `unverified_dimension`/`fail`/`unverified`/`withheld`. Sources: `retrieval-r1.md` §Diagnose E; `~/.cache/saga-chunk-quality/20261123/unverified-sources-48.json`. Status: measured + fixed.
21. **Include sources without an audit, labelled `unverified`; missing evidence is never `pass`.** Contract settings: `unverified_sources` + `on_unverified_source: include_labelled` + `on_unlabelled: unverified`. Result: 188 documents / 10,474 chunks; labels pass 6,182 / fail 503 / unverified 3,789. Production then cited the reinstated MDR, 2024/2690 and Digitaliseringsstyrelsen guidance. Source: `2026-11-23-104639-retrieval-naeste-fase.md`. Status: adopted (saga#190).
22. **When the corpus grows, re-align probe depth with serving depth.** Adding the 48 sources pushed required spans out of `max_hits: 6`: probe score 0.417 < the 0.45 floor. With `max_hits: 10` (= `top_k`): 0.517. Source: same note. Status: adopted.
23. **Nightly refresh with `on_source_revision: unverified`:** if an upstream text changes, its chunks are written `unverified`/`unjudged` (`source_extraction_changed`) instead of being held. Probes that need that document are skipped, and forbidden evidence in it is reported `forbidden_unchecked`. The quality bundle is a digest-pinned OCI image, sha256-checked in an init container. The first cluster run failed because prompts were missing from the ingest image. Promotion is fail-closed when a source returns 502/429. Source: same note; `saga:docs/operations/ROLLOUT-4B-2048.md`. Status: adopted.
24. **Build ingest images from the lockfile.** An unpinned pypdf (7.0.1 → 7.1.0) silently re-extracted 46 PDFs (14–15 % of lines changed) and destroyed E1's clean control. Source: e1-opfolgning. Status: adopted.
25. **When the filter changes, move gold labels to the current edition.** The eval gate went red (recall@10 0.505 → 0.448) because 10 gold labels sat on the now-filtered adopted AI Act. After moving them: 0.512. Source: e1-opfolgning. Status: adopted.
26. **Keep the seed chain identical and test it:** `sources.yaml` (source of truth) → `urls-*.txt` → deploy copy, plus scope and seed tests. When comparing collections, compare text: `content_hash` differs per pipeline even for the same edition (all 11 differed). Never ingest test profiles or answer keys into the corpus. Source: l99 note, `locate-4b.md`, `search-diagnosis-source-review.md`. Status: adopted.
27. **Fetching from primary sources:**
    - EUR-Lex web pages return HTTP 202 with no content to bots; use Cellar SPARQL plus content negotiation with `Accept-Language: dan`. ft.dk returns 403; folketingstidende.dk PDFs work.
    - Retsinformation `.rdfa` gives in-force and "consolidated by" (`consolidated_by`) relations.
    - MDCG and justitsministeriet.dk fail intermittently, so retry.
    - Sources: `k1-versionskort.md`, `l99-ai-hjemmelslov-import.md`.

### F. Verbatim citation check (applicability)
28. **Normalise before comparing a quote with its chunk, then require exact wording.** In order: NFKC → remove invisibles (U+00AD, zero-widths, BOM) → amendment markers (▼M1/▼B/▲) to a space → the table separator "|" (from EUR-Lex list tables, "a) | tekst") to a space → remove quote marks → unify dashes → join line-break hyphens (letter-"- "-letter) → casefold and collapse whitespace.
    - Split on "…"/"..."; every segment must appear, in order. Minimum quote length is 20 characters. Placeholder "quotes" are rejected.
    - An added full stop is **not** accepted, and paraphrase is always rejected.
    - Verified-rule citations: 35 % (2048-token chunks spanning several provisions) → 57 % (provision located by the quote's position, 4B heading forms) → 66 % (limited to the provision's span) → 74.8 % ("|") → 84.7 % (hyphen; production 84.2 %). The merge bar was ≥ 80 %.
    - Source: 2026-11-23 note; `saga:src/saga/gateway/applicability/evidence.py`. Status: measured + adopted (saga#192).
29. **A quote counts only for the provision that contains it.** Rules with no provision number accept a verbatim quote only from the rule's own located document. Danish § locators must match the 4B form ("§ 7." alone on a line). Before this fix, no § locator matched in 4B. Source: `saga:docs/regelkompas-collection.md`. Status: adopted.
30. **Downgrade-only guard:** a "does not apply" that rests on a quote containing a scope reservation ("i det omfang", "for så vidt", "to the extent", …) becomes "must be clarified". Trigger: NIS 2 loven § 1, stk. 2. Status: adopted.
31. **At ingest, decide a line-end hyphen from the document's own vocabulary** (the word appears unbroken: drop the hyphen; appears with a hyphen: keep; otherwise keep and count as unresolved). No dictionary. Source: `experiments/rag-chunk-design.md`. Status: adopted.

### G. Results that held up, and failures
- **The superseded gate holds now:** S3 found 0 superseded served or cited in 426 turns; consolidated AI Act served 10/10 on version probes. But R@10 for rule card → provision is 51.4 % (target ≥ 95 %). Document level is 88.8 %: the problem is finding the provision inside the right edition, not version selection. Source: `s3-maaling-4b.md`.
- **Prompt fixes didn't work; deterministic labels did** (K6, K6-2: all three criteria failed twice). K8 sidecar labels: shown as source-backed without the governing provision 26/83 → 0 on explain; 74 "not current edition" (68 AI Act, 6 CRA) and 6 draft/proposal labels. Source: `k8-etiketter.md`.
- **SF2 is a negative result.** "Proposal" here means extraction suggestions, not draft laws. A prompt addendum to recover an omitted enumerated rule structure (lead-in + three points) gave 14/22 vs a required 18, within run-to-run noise at temperature 0. Lesson: keep enumerations whole structurally, not by prompting. Source: `saga-sf2-proposal-completeness.md`.

### Open questions
- Who confirms the editions? K1, `source-status.json` and the `replacedBy` markers are drafts with no legal review (e.g. is the adopted CRA a "superseded edition"?).
- How to version-stamp guidance written before an amending act (e.g. 2026/1744), so it can't leak old dates (item 17)?
- Should the answer bots move to `current_adopted`, or keep `current` and label drafts (S3: 30 draft/proposal citations)?
- Under the filter, a question about a draft gets "not found" instead of a labelled draft. Is that acceptable?
- Labelled non-binding recital pool, and placement of `proposal` sources such as L 99: not built.
- Two seed URLs (02009L0048-20260829, 02014L0053-20260530) exist in no collection.
