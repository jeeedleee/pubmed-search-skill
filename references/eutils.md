# E-utilities Notes

This skill uses the public NCBI E-utilities endpoints:

- `esearch.fcgi`
  Search PubMed and return PMIDs.

- `esummary.fcgi`
  Fetch paper metadata such as title, journal, date, and identifiers.

- `efetch.fcgi`
  Fetch XML records and extract abstract text.

Practical guidance:

- Keep result counts small for interactive use.
- Prefer `pub+date` when the user asks for the latest papers.
- Prefer `relevance` for topic overviews.
- Abstract availability varies by record.
