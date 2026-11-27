---
name: legal-rag
description: >-
  Use when building, changing or evaluating retrieval (RAG) over legal text: Danish laws (Retsinformation),
  EU acts (EUR-Lex/Cellar) and authority guidance. Covers source extraction, chunking with heading paths,
  embedding, query construction, hybrid search, reranking, validity/versions, citation checks and how to
  measure changes. Built from measured results in the AI Regelkompas / Saga project (2026-11).
---

> **Skill loaded:** when you load this skill, announce it to the user as `⚖️ legal-rag`.

# Legal RAG: extract, chunk, embed, retrieve, measure

Every rule below was measured in the Regelkompas/Saga project unless marked **(hypothesis)** or
**(negative)**. Numbers and evidence paths are in the reference files; read the one you need:

- [references/extraction-and-chunking.md](references/extraction-and-chunking.md): sources, PDF/HTML/XML, units, heading paths, chunk size, locators, chunk-quality judge.
- [references/retrieval.md](references/retrieval.md): embedder, query construction, hybrid/lookup arms, reranker, floors and gates, top_k, topic path.
- [references/validity-and-citations.md](references/validity-and-citations.md): editions, consolidated text, drafts, metadata schema, corpus management, verbatim citation checks.
- [references/evaluation.md](references/evaluation.md): facit, panel labelling, metrics, paired tests, guard sets, answer check, determinism.

Defaults when nothing else is known (what runs in production on 2026-11-25):
Qwen3-Embedding-4B Q8_0 at native 2560 dims with a Danish legal query instruction, whole question embedded,
2048-token provision-aware chunks with the heading path in the chunk text, provision lookup as an extra RRF
list, top_k 10, Qwen3-Reranker-4B on the user question only, no LLM rewrite/decomposition, exact dense scan,
validity filter inside every arm.

## 1. Sources and extraction

1. **Prefer structured XML/HTML over PDF.** EU: consolidated Cellar text (`celex/0…-YYYYMMDD`) via SPARQL +
   content negotiation (`Accept-Language: dan`); EUR-Lex web pages answer bots with empty 202s. Danish law:
   Retsinformation XML; `.rdfa` gives in-force and "konsolideret ved" relations.
2. **Audit extraction against the raw source** (markup or page renders), with an independent auditor. Your own
   earlier output and the repair agent's own counts are not evidence.
3. **PDF only with proven rules:** tag tree when provably complete, else geometry, never both in one document;
   paragraph breaks from baseline pitch per font size; remove running headers/footers only when repetition is
   proven; join across pages only with linguistic + layout evidence; footnotes after the paragraph holding their
   marker; hyphens resolved from the document's own vocabulary (no dictionary); reject control characters.
4. **Deterministic and pinned:** stable tie-breaking, parser versions locked (an unpinned pypdf bump re-extracted
   every PDF and destroyed an experiment control).
5. **Non-text content gets visible markers** (`[billede: <alt>]`, `[billede uden tekstbeskrivelse]`,
   `[formel: …]`); decorative images are dropped and counted; a marker never lands across a heading.
6. **Quotation marks pair only inside one article/annex and list item**, never across footnotes (one bad pair
   swallowed AI Act art. 103–113 and all annexes).

## 2. Units, headings and chunks

1. **Units come from the source's literal headings only** (`Artikel N`, `§ N.`, `KAPITEL`, `AFSNIT`, `BILAG`,
   recital block). Guidance gets structure only from heading spans you have frozen. Never guess list items as
   headings; non-increasing numbers (tables of contents, quoted text) are anomalies.
2. **Put the heading path in the chunk text itself**: document title, then ancestor and unit headings verbatim
   (one per line), then required context, blank line, verbatim body. Metadata-only hierarchy gave nothing
   (9/16 vs 9/16); with the header the reranker score of the same stk. went 0.02 → 1.00. Without it only 18/313
   AI Act chunks started with their article heading.
3. **One chunk per unit when it fits; otherwise pack whole segments** (stk., numbered points, letters). Never span
   two units, never merge provisions, overlap only inside a split unit. Blind 512/64 chunking produced ~30 %
   overlap copies and 21/23 locator misses.
4. **Target 2048 tokens with an atomic exception** (an indivisible block may exceed the target if every consumer's
   real token limit holds); never truncate, reject what still does not fit. 2048 gave 83/86 documents passing vs
   50/86 at 512. Count tokens with each consumer's own tokenizer and template, and probe the server's real
   limit (advertised 4096, accepted 4095).
5. **Copy declared dependencies verbatim into the chunk**: list lead-in, table header, quote lead. Tables as one
   row per line with ` | ` separators.
6. **Drop annex reproductions** (Danish acts that reproduce an EU regulation "for praktiske hensyn") at ingest:
   annex-copy citations 179 → 0.
7. **Expand a retrieved chunk to its whole unit at answer time** (bounded budget, bound to revision/hash): gold
   spans delivered 4.1 % → 9.7 %.
8. **Known weakness (open):** short tail chunks (a 334-character end of AI Act art. 2) get inflated reranker scores
   and outrank whole articles. Merge tails into their unit or set a minimum size **(hypothesis, untested)**.
   Parent/child small-to-big was worse **(negative)**.
9. **Annex points, letters and stk. need their own addressable units.** The AI Act's Annex III is only two chunks,
   so a question about point 4(a) can at best get "the right half of the annex". On 312 Commission Service Desk
   classification cases the Annex III point was served in 53 %, Art. 6(3) in 22 % and Annex I in 0 of 19
   (English questions against a Danish corpus, so language and chunking are mixed in these numbers).
   **(hypothesis: sub-units fix it, untested)**

## 3. Embedding and query construction

1. **Embedder size matters more than tricks:** Qwen3-Embedding-4B vs 0.6B, hit@5 0.31 → 0.58 short, 0.10 → 0.64–0.77
   long. Keep native width (2560 helped long questions); exact float32 scan beats an ANN index with a post-filter,
   which silently starved candidate lists.
2. **Query instruction:** Qwen3 `Instruct: …\nQuery:` asking for provisions in Danish laws, EU acts and guidance,
   on queries only, never on documents (removing it: nDCG@6 −0.074). Re-measure per model (it hurt 0.6B + reranker).
3. **No LLM rewrite or decomposition in front of a strong embedder** (rewrite-free: nDCG@6 0.717 → 0.756; rewrite
   alone damaged the topic guard set by −0.19).
4. **Embed long questions whole;** compact with an LLM only when they exceed the embedding context, and then never
   rerank against the compacted text.
5. **Broad topic texts retrieve guidance, not provisions.** When you know the provision, look it up by heading
   (locator-first gave 100 % vs 14.6 %).

## 4. Search, reranking, floors

1. **Provision lookup as an extra RRF list:** resolve "act + Artikel/§/Bilag N" from the user's original sentence
   against headings in the act's current document (hit@6 0.606 → 0.906). BM25 instead of it was worse **(negative)**;
   a `plainto_tsquery` keyword arm is empty for most natural questions and adds nothing **(negative)**.
2. **Serve 10 sources** (grade-2 recall 0.72 → 0.88, answers cite a governing source more often).
3. **Reranker:** a weak reranker after a strong embedder hurts (0.6B: −0.026 nDCG@6). The 4B reranker helps the
   user question (+0.030) but hurt fixed topic texts (−0.106), so topic retrievals skip it. Removing it costs short
   questions a lot (b-short −0.165, template lookups −0.111). Questions compacted for length skip it anyway, so it
   cannot cause or fix gaps on long texts. Self-convert and validate GGUFs against the transformers reference;
   never score a silent fallback.
4. **Pair guard:** count each (question, chunk) pair with the reranker's own tokenizer before the call and leave out
   only a pair over the server's real limit (placed after the scored items, no score, counted). One oversized pair
   otherwise fails the whole call with HTTP 400 and degrades the turn to RRF order (12/12 long questions degraded →
   0/12, frozen sets unchanged).
5. **A second eval endpoint must be proven score-identical** (same GGUF sha, build, flags, GPU model and driver;
   max |Δscore| 0.0, identical rankings on 4,200 pairs) before it carries eval traffic, and never mix endpoints
   inside one paired comparison.
6. **Floors and gates are model-specific; recalibrate on every model/corpus change** with the empty-band method
   (geometric middle between strongest negative and weakest positive), and report how few negatives you had.
7. **Follow explicit cross-references and supply definitions** ("jf. art. 6, stk. 2" → Annex III; Art. 3
   definitions as context). The skill has no measured method yet **(hypothesis)**.

## 5. Validity, versions and citations

1. **Mark superseded editions with `replacedBy`** (which text to read), not `inForceTo`; keep them in the corpus and
   filter them inside every search arm; validate the markers at load. Superseded citations 117 → 0.
2. **Unknown metadata excludes nothing;** leave unverifiable fields absent. Closed schema (sourceType, status,
   territory, inForceFrom/To, supersedes, replacedBy, omitAnnexes, …).
3. **Drafts and proposals are never a basis:** for anything that feeds an assessment use a filter that admits only
   current *adopted* texts. With a looser filter the bots cited draft guidelines 14× and proposals 16× in 111 answers;
   drafts/proposals were served in 192 of 456 turns. The adopted-only filter removed all of them and raised nDCG@6
   0.713 → 0.747 (long questions 0.633 → 0.709, p < 0.001) with no set worse. It only works on documents that carry
   the marker: audit unmarked documents (25 of 192 had no status) before you rely on it. It also removes proposals
   as a source for "what does the proposal say?" questions; serve those as a labelled signal pool, never as a basis.
   Final guidance can still outrank the act itself (AI Act Art. 5 lost to final prohibited-practice guidance).
4. **Compare every rebuilt index with the seed list,** not with the gold set (gold built on the index found 0 gaps
   while 48 sources were missing). Sources without an audit go in labelled `unverified`; missing proof is never pass.
5. **Verbatim citation check:** normalise (NFKC, invisibles, amendment markers, table `|`, quote marks, dashes,
   line-break hyphens, case, whitespace), then demand exact wording, in order, from the provision that contains it;
   never accept paraphrase or an added full stop. Verified citations 35 % → 85 %.
6. **Enforce verbatim quotes mechanically, not by prompt.** A prompt rule ("quote only verbatim text") moved
   verified quotes 25.0 % → 31.6 % (p = 0.114, not adopted). A gateway guard that removes quotation marks around
   text not found verbatim in a served source (same normalisation as the check; keeps the text, adds nothing) gave
   100 % verified among remaining quotes with no gate worse. Models translate source quotes in other-language
   answers (4 of 113 English-answer quotes were verbatim) and also present translations as Markdown blockquotes,
   so cover blockquotes too.
7. **Measure routing, answer language, and quotation checks separately.** On 237 paired Saga dev items, a
   question-language detector matched all labels. The trailing language rule and fixed English texts did not
   reliably change generated answer language: 102/114 → 103/114 among English pairs answered in both arms
   (one-sided exact McNemar p = 0.50). Danish stayed at 113/113. The same candidate's mechanical blockquote guard
   removed all non-verbatim blockquotes (27 → 0). Saga did not adopt the bundle. Test the guard separately.
   An output-language check and one bounded regeneration are **untested hypotheses**. Do not translate source
   quotations to satisfy a language check. See [Saga #230](https://github.com/FactusConsulting/saga/pull/230).
8. **Remove proposal content from system prompts.** A prompt that described a pending proposal made the bot restate
   that content without a source; removing it made the model invent facts. Name proposals as proposals, forbid
   describing their content, and answer only from excerpts (10/10 probes passed).

## 6. Measuring a change (do this every time)

1. **Measure the route the product actually calls**, with its real query construction, at provision level as well as
   document level (document 88.8 % vs provision 51.4 % on the same run).
2. **Facit = pooled, panel-graded (0/1/2), frozen by hash before scoring.** A citation/catalogue facit alone is
   invalid (75–90 % of its "misses" were relevant). Rescored against the graded facit, the 52 catalogue misses of
   the 51.4 % run were 30 questionable targets, 15 other grade-2 provisions of the same act, 7 real misses (act
   absent, guidance or a draft served), 0 with no grade-2 source. Calibrate each panel model on controls (≥ 95 %),
   label new chunks under the frozen protocol before scoring, unrated is never 0.
3. **Metrics:** nDCG@6 (linear gain = mean grade), grade-2 recall, any grade-2; paired per question (sign-flip
   permutation 10,000, exact McNemar), p < 0.05.
4. **Preregister cells, adoption rule and veto before running.** Keep guard sets for secondary routes (the topic
   guard caught a regression the overall number hid). Run a combination cell; effects do not add.
5. **Answer-level check before rollout** with the production generator: grade-2 cited, citation precision, claims
   without coverage, blind pairwise judgement as a secondary signal only. An LLM judge is never the target metric.
   Expect noise: at temperature 0 on another host with the same model, outcomes matched 29/30 but citation sets
   only 7/30 and wording 1/30.
6. **Determinism:** memoise helper-model outputs, embeddings and reranker answers per exact input (never across
   models), fingerprint the corpus, read production only through a read-only replica snapshot, hard-fail on memo
   misses and block outbound sockets in offline replays. Measure the noise floor before you trust a difference.
7. **Question-and-answer test set, tiered by reference quality.** Gate only on a gold tier (core questions with an
   official answer from an adopted source: FAQ, guidance example, decision). Report separately: official answers
   from drafts, outcome-class items (out of scope, not in corpus, proposals), panel-written references, and
   generated items (missing-fact variants, translations). On one set the gold tier was 285 of 667 items. Generated
   variants are weak labels (one writer, small review), so report them per protocol version.
8. **Clarification mode needs its own measure in both directions:** "asks for the removed fact" on missing-fact
   variants and "unnecessary clarification" on full-context gold items. A structured clarification mode cut false
   answers out of scope (28 → 12 of 46) and unknown-to-"no" (14 → 7 of 93), but asked for the missing fact in only
   9 of 93 variants and, on gold, lowered correct outcome 95.5 % → 83.2 %. Keep it off until both directions pass.

## 7. Where this project still falls short (2026-11-26)

Retrieval quality measured against the graded facit is good for short questions (any grade-2 served 0.95–1.00 per
set) and weaker for long texts (review texts nDCG@6 0.57). The real gaps are drafts/guidance crowding out the act
(adopted-only filter), long questions (short per-fact queries, under test), sub-units in annexes and lists, and
cross-references. Retrieval metrics are not answer quality: build a question-and-answer test set with reference
answers from official sources (Commission, Datatilsynet, EDPB, national authorities, decisions), variants with one
required fact removed, and out-of-scope items, and score answers mechanically (outcome class, governing provision
cited, verbatim quotes, no draft as basis, unknown never "no").
