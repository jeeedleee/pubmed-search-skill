---
name: pubmed-search
description: Search PubMed and summarize biomedical literature using the NCBI E-utilities API. Use when Codex needs to find recent or relevant PubMed papers, fetch PMID/title/journal/date/abstract details, compare a small set of papers, or produce Chinese literature digests with source links.
---

# PubMed Search

Use the bundled script for deterministic PubMed retrieval instead of manually browsing search pages.

## Quick Start

Run:

```bash
python scripts/pubmed_search.py --query "glioblastoma immunotherapy" --retmax 5 --format json
```

Use `--days` for recent papers:

```bash
python scripts/pubmed_search.py --query "CRISPR delivery" --days 30 --retmax 8 --format markdown
```

Filter by study type and output Chinese reading cards:

```bash
python scripts/pubmed_search.py --query "KRAS G12D lung cancer" --article-type review --article-type clinical-trial --retmax 5 --format chinese-cards
```

## Workflow

1. Run `scripts/pubmed_search.py` with the user's topic, disease, drug, biomarker, or method keywords.
2. Prefer `--days` or `--mindate/--maxdate` when the user asks for latest or recent literature.
3. Add `--article-type` when the user explicitly wants reviews, meta-analyses, or clinical trials.
4. Read the returned metadata and abstracts.
5. Summarize in Chinese unless the user asks otherwise.
6. Keep direct links to PubMed pages in the final answer.

## Output Guidance

For literature lookup requests, include:

- Paper title
- PMID
- Journal
- Publication date
- Study type when available
- Why it matters in one or two sentences
- PubMed link

When the user asks for a shortlist, prioritize:

- Recency
- Clinical or practical relevance
- Stronger study type when obvious from title or abstract
- Review articles when the user asks for an overview

Use `--format chinese-cards` when the user wants a directly readable Chinese shortlist instead of raw metadata.

## Notes

- The script uses NCBI E-utilities and does not require an API key for light usage.
- Keep requests modest. Avoid very high `--retmax` unless the user explicitly wants a broad search.
- If the abstract is missing, say so directly instead of inferring beyond the title and journal metadata.
- Available `--article-type` filters: `review`, `systematic-review`, `meta-analysis`, `clinical-trial`, `randomized-controlled-trial`.

## Resources

- `scripts/pubmed_search.py`
  Deterministic PubMed search and abstract retrieval.

- `references/eutils.md`
  Short reference for the PubMed endpoints used by the script.
