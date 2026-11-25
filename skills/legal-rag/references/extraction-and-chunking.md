# Extraction, units, heading paths, chunk size, locators, chunk-quality judge

Evidence behind the `legal-rag` skill. Extracted 2026-11-25 from the AI Regelkompas / Saga project notes.
Path shorthands: `N/` = `/home/lars/source/ai-compliance-dk-wt-notesweep/notes/` (also in the ai-ops-dk/ai-compliance-dk repo under
`notes/`), `C/` or `CQ` = `~/.cache/saga-chunk-quality/` (local artefacts, may disappear), `S/`, `saga:` or `RO` =
a Saga worktree at origin/main (`docs/eval/`, `docs/operations/ROLLOUT-4B-2048.md`, `deploy/k8s/config/`).
Status tags: measured + adopted / measured / negative result / hypothesis. Numbers are from the cited runs;
re-measure before relying on them for a different corpus or model.

Below are 48 learnings, all taken from the notes listed, Saga docs and artefact paths. The local `/home/lars/source/saga` checkout is stale (it has no `docs/operations/` or `docs/eval/`). For Saga "origin/main" facts I therefore read `saga-wt-s3measure`, which is checked out at `origin/main` = `ea8c845` (code `e09d212`).

**Path abbreviations:**
- `N/` = `ai-compliance-dk-wt-notesweep/notes/`
- `E5` = `N/2026-11-17-144417-e5-inputdiagnose.md`
- `CQ` = `~/.cache/saga-chunk-quality/`
- `RO` = `saga-wt-s3measure/docs/operations/ROLLOUT-4B-2048.md`

## A. Source extraction (XML, HTML, PDF)

1. **Treat the raw source as the reference: audit extraction independently against markup or page renders, never against your own earlier output.**
   - Why: the repair agents' own counts were wrong several times. One invariant check missed two label forms, and one "changed documents" list did not match the hashes. Only the independent auditor's count was trusted.
   - Evidence: `N/experiments/rag-chunk-design.md` §8.3.
   - Status: measured + adopted. Caveat: an auditor is costly (two other PDF readers plus renders).

2. **Prefer structured XML/HTML over PDF.**
   - Why: XML reached 41/47 proven, with no confirmed text errors (`E5`, XmlUnverifiedProof). PDF climbed over about 12 audit rounds: 6 → 22 → 27 → 29 → 30 → 35 → 37 → 41 pass of 56. The final state is 41 pass / 3 unverified / 12 fail (`E5`, audit v28).
   - Status: measured. Caveat: most remaining PDF failures are slide decks with merged columns and scrambled tables. 15 PDFs were never indexed.

3. **For PDF, use the tag tree when it can be proven; otherwise fall back to geometry. Never mix the two routes within one document.**
   - Why: the tagged route grew from 14 to 25 of 56 PDFs. It is rejected when clipped text, missing tags or backwards lines appear (`E5` PdfTaggedCoverage).
   - Status: adopted.

4. **Decide paragraph breaks from evidence, not from pdfminer's `line_margin`.** Use baseline pitch per font size (±2 %, at least 10 lines).
   - Why: pdfminer measured line height as 8.04 pt where MuPDF measured 9.77 pt, which split every line into its own paragraph. After the fix (`E5` PdfGeometricParagraphs):
     - splits within a page: 1,676 → 153
     - running headers/footers or furniture inside sentences: 303 → 6
     - page-break splits: 324 → 49
   - Status: measured + adopted.

5. **Remove running headers and footers only when repetition is proven** (same height ±2 pt on ≥ 3 pages and ≥ 25 % of pages), and count what you remove.
   - Status: adopted (`E5`, design §3).

6. **Join text across a page break only with linguistic plus layout evidence.** The previous page must not end a sentence, and the next must start lower-case.
   - Why: all 22 joins made this way were real continuations, and no rejected candidate was one (`E5` tagged round 2).
   - Status: adopted.

7. **Place each footnote after the paragraph holding its own marker.** Invariant: no note is read before its marker; never place a note inside a sentence or between a colon lead-in and its list.
   - Why: the first rule ("all notes after the first marker") regressed 123 notes in 11 documents. Audit v12 fell from 13 to 9 pass (`E5`).
   - Status: negative result, then fixed and adopted. Notes before their marker: 178 → 0.

8. **Resolve end-of-line hyphens from the document's own vocabulary.** If the word occurs unhyphenated elsewhere, remove the hyphen; if it occurs hyphenated, keep it; otherwise keep it and count it as unresolved. Use no dictionary.
   - Why: "always keep the hyphen" left broken words in table cells ("canadi-ske"). With the vocabulary rule, p26 had 61 removed / 16 unresolved, and p36 64 / 7 (`E5` round 4).
   - Status: adopted.

9. **Reject extractions containing control characters, and strip NUL from `/Alt` and `/ActualText`.**
   - Why: U+0000 in a logo's alt text failed p33 and p34 (the text cannot be stored).
   - Status: adopted (`E5` round 10).

10. **Drop hidden or over-painted text only when invisibility is provable.**
    - Why: the first over-paint detector deleted visible text behind a transparent Form group (`E5`, 19/11 13:06).
    - Status: adopted, after a regression was found.

11. **Make tie-breaking deterministic** (stable source-order ordinals).
    - Why: pdfminer 20260107 breaks distance ties by `id(box)`. The same PDF gave two different extractions under different allocation orders (`E5`).
    - Status: adopted.

12. **Pin parser dependencies with a lock file.**
    - Why: pypdf drifted from 7.0.1 to 7.1.0 between images and re-extracted every PDF. 46 documents in `ai-regler` and 38 in `regelkompas` changed, with 14–15 % of lines different. That invalidated an experiment control (`saga-wt-s3measure/docs/eval/e1b-annex-omission.md`).
    - Status: negative result, which led to lock-file images.

13. **For HTML, cut site chrome by markup role and count what you cut, but keep heading-marked buttons and accordions.**
    - Why: one HTML repair (v3) removed 10 accordion headings that sat inside buttons, which was a regression. HTML-v4 then matched all 41 frozen reference texts. Later status: 58 pass / 27 unverified / 0 fail of 85 (`E5`).
    - Status: measured + adopted. Caveat: one pass had relied on a site-specific class name.

14. **Pair quotation marks only within the same article/annex container and list item, and never across footnotes.**
    - Why: an opening » in an amending article paired with a « closing a footnote at the end of the document. The resulting "quoted" span swallowed AI Act articles 103–113 and annexes I–XIV (80 real headings) and 34 CRA headings. That made locators and probes invalid (`E5` GoldSpansV1 / EurlexQuotedSpans).
    - Status: found and fixed. AI Act contract: 109 → 159 units.

15. **Tables: one row per line, cells separated by ` | `; a list item stays a frozen block.**
    - Status: adopted (design §3).
    - Caveat: the 4B corpus renders list items as `a) | tekst` and footnotes as `^{1}`. Content is identical, but string matching must tolerate this (`N/experiments/locate-4b.md`, 6/92 differences).

## B. Non-text content and image markers

16. **Replace each content image with a visible generated marker:** `[billede: <author alt>]`, `[billede uden tekstbeskrivelse]`, `[formel: …]` or `[formel uden tekstgengivelse]`.
    - Omit and count decorative images (empty alt, `role=presentation`, hidden, 1×1, artifact).
    - Reject source text that itself looks like a marker (`MarkerCollision`).
    - Why: before this, alt text appeared unmarked inside body text in 34 HTML documents, and XML `<Image>` produced nothing. Result: 69 markers, 14 decorative skipped (`E5` NonTextMarkersV1). On PDF the markers moved p08, p20, p22, p43 and p48 to pass.
    - Status: user decision + adopted. Caveats: vector figures without a caption get no marker; an alt that is only a label still counts as a description.

17. **Never let a marker land on the wrong side of a heading,** or it attaches to the previous section.
    - Why: this happened on p26 p.35 and p06 p.3.
    - Status: rule added in audit (`E5` v26 r2).

18. **On the PDF layout route, take alt text from the structure tree's Figure.**
    - Why: without it the route wrote "no description" for figures that had authored `/Alt`. p01, p02, p04 and p05 fell from pass to fail (`E5` audit v20).
    - Status: negative result, then fixed.

## C. Structure, units and heading paths

19. **Derive units only from the source's literal headings** (`Artikel N`, `§ N.`, `KAPITEL`, `AFDELING`, `AFSNIT`, `BILAG`, "ud fra følgende betragtninger:") and only for act-type sources.
    - Guidance gets structure only from heading spans frozen in the source contract. Never guess numbered list items as headings.
    - Treat non-increasing labels (tables of contents, quoted text) as anomalies, so the document stays unverified.
    - Evidence: `saga-wt-s3measure/src/saga/ingest/source_structure.py` docstring; design §4.
    - Status: adopted.

20. **Put the heading path in the chunk text itself, not only in metadata.**
    - Rendered input is: document title (declared as generated), then ancestor/unit headings copied verbatim one per line, then required dependencies, a blank line, and the verbatim body (`source_segments.py`).
    - Why, three pieces of evidence:
      - Hierarchy as a native index (951 of 2,326 chunks carrying hierarchy) gave 9/16 correct answers, the same as the legacy index, with no net gain (`N/experiments/saga-source-first.md`; this is the "PR #139 9/16 vs 9/16" cited in `e2-strukturbevidst-opdeling.md`).
      - The old chunker had no metadata and no headings: only 18 of 313 AI Act chunks started with their article heading (`e2-…md`).
      - In the reranker analysis, adding the header lifted the same stk. from a score of 0.02 to 1.00 (`E5` 22/11).
    - Status: adopted. Caveats: the 9/16 result is confounded (planner and config also changed). Whether the header should also feed the sparse `ts` arm was left open.

21. **Emit one chunk per unit when it fits; otherwise pack whole segments** (paragraphs, `Stk. N.`, `1)`, `a)`). Never span two units, never merge separate provisions, and overlap only inside a split unit.
    - Why: the old 512/64 blind chunker produced 2,266 of 7,445 chunks that were overlap copies. In K2, 21 of 23 locator misses were the same heading appearing in chunk h and h+1 (`N/experiments/k2-lokatordaekning.md`).
    - Status: adopted (E2 itself was never run as a pre-registered A/B).

22. **Keep annex reproductions out of the index.** Danish implementing acts reproduce EU regulations "for practical reasons"; use `omitAnnexes: true` on the source entry.
    - Why: LOV 2025/467 went from 455 to 7 chunks and LBK 2024/289 from 289 to 34. Annex-copy citations fell from 179 to 0. Before, the copies took 8.5–11.4 % of top-6 slots (`e1b-annex-omission.md`).
    - Status: measured + adopted. Caveat: the consolidated AI Act was still served in only 7 of 30 version probes, because guidance filled the freed slots.

23. **Treat recitals as their own fine-grained judge units** (the consecutive run of numbered recitals a chunk touches).
    - Why: the whole recital block was one unit, up to 235,750 characters in the AI Act. 759 of 910 cases that could never pass sat in recital units. With per-recital judge units this fell to 207 at 1024 and from 409 to 127 at 2048 (`E5` 20/11).
    - Status: adopted for the judge only; chunking and identity are unchanged.
    - Open: whether recitals should be excluded from free search or become their own chunk type.

24. **Copy contract-declared dependencies verbatim into the chunk** (list lead-in, table header, quote → lead), transitively and de-duplicated. Reject the document if they cannot fit or if they cross units.
    - Why: 2 of 35 preflight rejections were dependencies crossing units; both traced to wrongly split multi-part headings (`E5`).
    - Status: adopted. Copied context must not introduce a new primary article/§ marker.

## D. Chunk size and token budgets

25. **Use a 2048-token target, with an atomic exception: an indivisible block may exceed the target if both consumer budgets hold.** Never truncate.
    - Why, same 86 documents (`E5` 19/11 13:06):

      | Target | Documents pass/fail | Units split on the 50-document subset |
      |---|---|---|
      | 512 | 50/36 | 189 |
      | 1024 | 72/14 | 28 |
      | 2048 | 83/3 | 2 |

    - Corpus freeze v8b (128 documents): 1024 gives 7,988 chunks, 66 over target; 2048 gives 6,384 chunks, 3 over target (design §5).
    - Reference judge: 1,810 fail at 1024 vs 523 at 2048 (`E5` 21/11).
    - Status: measured + adopted (`RO`).

26. **Do not expect a target change to move hit rates much; it mainly delivers complete provisions.**
    - Why: paired comparison of 1024 vs 2048, n=160: no difference on hit@1, hit@5, R@5 or MRR. Complete gold chunk in top-5 was 0.312 vs 0.419 (p=0.0005). That advantage disappears once unit expansion is counted: 0.456 vs 0.463 (`E5` 21/11 21:30).
    - In answers, a non-passed source was cited in 55–58 % of answers at 1024 vs 25–33 % at 2048.
    - Status: measured.

27. **Count budgets with each real consumer's tokenizer and template** (embedding, and reranker on query + chunk). Probe the server's real limit.
    - Why: `/props` advertised 4,096 tokens, but 4,095 was accepted and 4,096/4,097 rejected. HF tokenizers apply NFC normalisation and GGUF does not (`E5` 18/11).
    - Final measured ceilings: 3,772 embedding / 4,052 reranker tokens. At 2048 the token distribution is p50 416, p99 2,093, max 3,772 (`RO`).
    - Status: adopted.

28. **Reject any input that is still over budget; never cut silently.**
    - The single remaining blocker: lta/2026/397 needed 4,207/4,486 tokens until a source-proven quote overlay fixed it. One recital in 32026R1744 is a single 2,310-token paragraph and was kept whole (`E5`).
    - Status: adopted.

29. **Treat chunk size and vector width as separate choices.**
    - Qwen3-Embedding-4B Q8_0 at 2560 dimensions was chosen. a+c+d is flat across 1024/2048/2560. Long queries (b): 0.72 / 0.78 / 0.80 any-gold.
    - The 0.6B endpoint silently ignored `dimensions:512`, so reduce widths client-side by prefix cut plus L2 re-normalisation (`RO`; `E5` 19/11).
    - Status: measured + adopted.

## E. Locators, heading regex, start rule and unit expansion

30. **Find a known provision with a full-title heading regex**, `Artikel[^0-9]{1,3}N[^0-9A-Za-z]{1,3}` + title tokens; for Danish law `(?:^|[^0-9])§[ NBSP]N\.[ NBSP\n]`. Take titles from Cellar, not from the corpus.
    - Why: number-only patterns were ambiguous (NIS 2 art. 20/21/23, MDR art. 2). With full titles, 0 headings were missing in every cell (`k2-…md`).
    - Status: adopted.

31. **End the span at the next heading** (`until` = the next article/KAPITEL/AFDELING/BILAG, or `\n§ N.`/Kapitel), and fix the start rule.
    - Why: the old "+1 chunk if the heading sits in the last 300 characters" rule lost the heading for 4–5 targets, and GDPR art. 38 started inside art. 39. After the fix: 71/73 = 97.3 % complete, clean provisions (only CRA was missing a version) (`k9-lokatortabel.md`).
    - Status: measured + adopted.

32. **When merging overlapped chunks, dedupe whole short paragraphs.**
    - Why: a ≥ 16-character overlap minimum failed on list markers such as "g)", leaving 107 joins with duplicated markers (`k9…`).
    - Status: fixed.

33. **Keep provision lookup as an extra RRF list:** resolve "act + Artikel/§/BILAG N" in the user's original sentence against chunk headings in the act's current document.
    - Why: a+c+d hit@6 0.606 → 0.906. Template set c hit@5 0.418 → 1.000, with no query lost. BM25 as a replacement was worse (0.606 → 0.475) (`RO`).
    - Status: measured + adopted (`rrf` rather than `pin`). Caveat: set c is template queries, so coverage is an upper bound.

34. **Read scopes, not collections, for locate.** Locate on `ai-regler-4b` found 92/92; DORA art. 28/30/31 went from truncated to complete (`locate-4b.md`).
    - Caveat: `until` can include the next section heading ("Afdeling II") at the end of a provision.

35. **Expand a retrieved non-pass chunk to its whole unit at answer time,** all-or-nothing and bound to revision/hash. Budget: 4,000 extra tokens per source and 16,000 per query.
    - Why: gold spans delivered rose from 4.1 % to 9.7 % (30 queries better, 0 worse), at a median cost of +521 tokens (`E5` staging eval).
    - DB test found two bugs: recital chunks were never expanded, and a stray row from another revision blocked expansion.
    - Status: adopted (`SAGA_UNIT_EXPANSION=true`).

36. **Short tail chunks are an open problem.**
    - Why: one 334-character tail of AI Act art. 2 (chunk 53623, relevance grade 1) was ranked first by the 4B reranker in all 8 ai-scope queries. That one chunk explained about 37 % of the guard-set nDCG loss (`N/experiments/retrieval-r2b.md`).
    - Unit expansion still serves the art. 2 body, but list-level scoring counts it as lost.
    - Status: diagnosis only; mitigated by routing topics without the reranker. A fix (minimum size, or merging tails into their unit) was never tested.

37. **Parent/child small-to-big did not help.** Children of 400 tokens, parents delivered whole: stk.-set hit@5 0.875 vs 0.775, set d 0.732 vs 0.488 (p=0.013), and +8–14k tokens per query uncapped (`E5` 22/11).
    - Status: negative result; 2048 kept.

## F. Semantic chunk-quality judge

38. **Define the judge's contract as the chunk's own unit:**
    - fail = something missing from its own unit (cut-off sentence, list lead-in, table header, condition or exception in the same unit, a definition made in the unit, governing text immediately above, or the antecedent of an opening reference such as "Det"/"denne frist");
    - text elsewhere (e.g. "jf. § 15") is retrieval's job, not a chunk defect.
    - Why: under the broader contract, the judge caught 0/11 exceptions placed in another section; the prompt and the controls disagreed about what counts (`E5` 20/11).
    - Status: user decision + adopted.

39. **Show the judge numbered segments labelled before/in/after the unit, send the reference once, and budget on the prompt actually sent** (24k/48k characters). Mark omissions explicitly.
    - Why: duplicating the reference caused 3,238 prompts over 32k characters; afterwards 0 were over 48k (`E5`).
    - Status: adopted.

40. **Make the judge do a search task (list dependencies with segment, relation and verbatim anchors) and let code derive the verdict.** Any omission inside the unit can never pass.
    - Qwen dev with prompt v7: 106/115 when mechanical results count as unverified.
    - Sealed set (148): false pass 7.6 %, false alarm 10.7 % (criterion was ≤ 5 %), mechanical 1.4 %. Accepted anyway as a labelling judge (`E5` 20–21/11).
    - Status: measured; adopted with a known breach.

41. **Use the judge to label, not to gate whole documents.**
    - Why: with a median of 27.5 chunks per document, the share of 128 documents with zero false alarms is 16 at 12 % false alarms per chunk, 65 at 2 %, 100 at 0.5 % (design §7.4).
    - Status: adopted.

42. **Do not auto-repair chunks by pasting judge-named segments into them.**
    - Why: of 1,642 repaired chunks, 315 passed, 861 failed again and 466 came back mechanical. 81 % of the new objections were about the pasted fragments themselves (`E5` 21/11).
    - Status: negative result; repair disabled (`max_repair_rounds: 0`). The code was kept.

43. **Keep judge controls free of leakage:**
    - write them prompt-blind and have them blind-reviewed (161/165 agreement);
    - build twin families that differ only in where the dependency sits;
    - never quote dev cases in the prompt (prompt v6 did, and 4 of its 5 improvements were exactly those cases);
    - check a length-only baseline (≈ 0.76 on one set).
    - Status: adopted.

44. **Model notes:**
    - Gemma-26B gave unwarranted passes on missing context.
    - Qwen3.6-35B needs ≥ 8,192 output tokens of reasoning budget (it emitted nothing at 2,048).
    - GLM-5.3-Flash was stronger (0 false passes on visible text) but took about 99 s per case, with 30 of 121 answers cut off.
    - Stream the responses: SSE removed the 300 s timeouts.
    - A reference (session) model labelled the corpus: 77.8 % pass at 1024. It may be inflated because the controls were written by Claude agents.
    - Status: measured.

45. **Mechanical gates Q1–Q7 run before any model call:** fidelity and coverage, boundaries, identity/context, budget, vector/index integrity, frozen probes, full-index check plus atomic promotion. Hash-bind every result so an unchanged input can be reused only with valid proof.
    - Status: adopted.
    - Production result: 138 documents, 6,745 chunks; labels pass 6,182 / fail 503 / unverified 60; probes 56/120 (`E5` 23/11).

## G. Open questions and known gaps

46. Very large units with no proven headings make the whole document one unit (p35 is a single 106,179-character unit), so its chunks can never pass. 248 such cases at 1024 and 147 at 2048. Solution not chosen.

47. Even after chunking, the retrieval gap is at provision level, not document level. Rule card → provision R@10 is 51.4 % (target 95 %), while the current document appears in top-10 88.8 % of the time. Guidance and drafts crowd out acts (`N/experiments/s3-maaling-4b.md`).

48. Not decided:
    - whether to keep the `plainto_tsquery` keyword arm, which is empty for 82 % of natural queries (requires all words), while "any word" was worse at pool 30;
    - whether the heading line should feed the sparse arm;
    - how to handle recitals in retrieval;
    - minimum chunk or tail handling;
    - figure markers for vector graphics without captions.
