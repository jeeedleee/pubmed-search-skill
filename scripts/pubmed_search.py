#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
USER_AGENT = "pubmed-search-skill/1.0"
TIMEOUT = 20
ARTICLE_TYPE_MAP = {
    "review": "Review[Publication Type]",
    "systematic-review": '"systematic review"[Title/Abstract] OR "Systematic Review"[Publication Type]',
    "meta-analysis": '"Meta-Analysis"[Publication Type] OR meta-analysis[Title/Abstract]',
    "clinical-trial": '"Clinical Trial"[Publication Type]',
    "randomized-controlled-trial": '"Randomized Controlled Trial"[Publication Type]',
}


def build_ssl_context(insecure: bool) -> ssl.SSLContext:
    if insecure:
        return ssl._create_unverified_context()
    return ssl.create_default_context()


def request(url: str, context: ssl.SSLContext) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=context) as resp:
        return resp.read()


def build_search_term(
    query: str,
    days: int | None,
    mindate: str | None,
    maxdate: str | None,
    article_types: list[str],
) -> str:
    term = query.strip()
    if article_types:
        type_clause = " OR ".join(f"({ARTICLE_TYPE_MAP[item]})" for item in article_types)
        term = f"({term}) AND ({type_clause})"
    if days:
        today = dt.date.today()
        start = today - dt.timedelta(days=days)
        date_clause = f'("{start.isoformat()}"[Date - Publication] : "{today.isoformat()}"[Date - Publication])'
        term = f"({term}) AND {date_clause}"
    elif mindate or maxdate:
        start = mindate or "1000-01-01"
        end = maxdate or dt.date.today().isoformat()
        date_clause = f'("{start}"[Date - Publication] : "{end}"[Date - Publication])'
        term = f"({term}) AND {date_clause}"
    return term


def esearch(term: str, retmax: int, sort: str, context: ssl.SSLContext) -> list[str]:
    params = {
        "db": "pubmed",
        "term": term,
        "retmax": str(retmax),
        "retmode": "json",
        "sort": sort,
    }
    url = f"{BASE}/esearch.fcgi?{urllib.parse.urlencode(params)}"
    data = json.loads(request(url, context).decode("utf-8"))
    return data.get("esearchresult", {}).get("idlist", [])


def esummary(pmids: list[str], context: ssl.SSLContext) -> dict[str, dict]:
    if not pmids:
        return {}
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "json",
    }
    url = f"{BASE}/esummary.fcgi?{urllib.parse.urlencode(params)}"
    data = json.loads(request(url, context).decode("utf-8"))
    result = data.get("result", {})
    return {pmid: result.get(pmid, {}) for pmid in pmids}


def text_or_empty(node: ET.Element | None) -> str:
    if node is None:
        return ""
    return "".join(node.itertext()).strip()


def efetch_abstracts(pmids: list[str], context: ssl.SSLContext) -> dict[str, str]:
    if not pmids:
        return {}
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
    }
    url = f"{BASE}/efetch.fcgi?{urllib.parse.urlencode(params)}"
    root = ET.fromstring(request(url, context))
    abstracts: dict[str, str] = {}
    for article in root.findall(".//PubmedArticle"):
        pmid = text_or_empty(article.find("./MedlineCitation/PMID"))
        abstract_nodes = article.findall(".//Abstract/AbstractText")
        parts = []
        for node in abstract_nodes:
            label = node.attrib.get("Label", "").strip()
            text = text_or_empty(node)
            if not text:
                continue
            parts.append(f"{label}: {text}" if label else text)
        abstracts[pmid] = "\n".join(parts).strip()
    return abstracts


def normalize_date(doc: dict) -> str:
    pubdate = doc.get("pubdate") or ""
    epubdate = doc.get("epubdate") or ""
    return epubdate or pubdate


def build_items(pmids: list[str], summaries: dict[str, dict], abstracts: dict[str, str]) -> list[dict]:
    items = []
    for pmid in pmids:
        doc = summaries.get(pmid, {})
        items.append(
            {
                "pmid": pmid,
                "title": doc.get("title", ""),
                "journal": doc.get("fulljournalname") or doc.get("source", ""),
                "pubdate": normalize_date(doc),
                "authors": [a.get("name", "") for a in doc.get("authors", []) if a.get("name")],
                "doi": next((aid.get("value", "") for aid in doc.get("articleids", []) if aid.get("idtype") == "doi"), ""),
                "pubtype": doc.get("pubtype", []),
                "abstract": abstracts.get(pmid, ""),
                "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            }
        )
    return items


def format_markdown(items: list[dict], query: str) -> str:
    lines = [f"# PubMed results for: {query}", ""]
    if not items:
        lines.append("No matching papers found.")
        return "\n".join(lines) + "\n"
    for idx, item in enumerate(items, start=1):
        lines.append(f"## {idx}. {item['title'] or '(untitled)'}")
        lines.append(f"- PMID: {item['pmid']}")
        lines.append(f"- Journal: {item['journal'] or 'unknown'}")
        lines.append(f"- Date: {item['pubdate'] or 'unknown'}")
        lines.append(f"- Link: {item['pubmed_url']}")
        if item["doi"]:
            lines.append(f"- DOI: {item['doi']}")
        if item["abstract"]:
            lines.append(f"- Abstract: {item['abstract']}")
        lines.append("")
    return "\n".join(lines)


def summarize_significance(item: dict) -> str:
    journal = item["journal"] or "期刊未标明"
    date = item["pubdate"] or "日期未标明"
    pubtypes = "、".join(item.get("pubtype", [])[:3]) or "文献类型未标明"
    if item["abstract"]:
        abstract = item["abstract"].replace("\n", " ")
        short = abstract[:160].rstrip()
        if len(abstract) > 160:
            short += "..."
        return f"这篇文献发表于 {journal}（{date}），类型为 {pubtypes}。摘要显示其核心内容是：{short}"
    return f"这篇文献发表于 {journal}（{date}），类型为 {pubtypes}。当前记录未提供摘要，解读应以标题和期刊信息为主。"


def format_chinese_cards(items: list[dict], query: str) -> str:
    lines = [f"# PubMed 文献速读卡片", "", f"查询主题：{query}", ""]
    if not items:
        lines.append("没有检索到符合条件的文献。")
        return "\n".join(lines) + "\n"
    for item in items:
        authors = "，".join(item["authors"][:4]) if item["authors"] else "作者未标明"
        pubtypes = "、".join(item.get("pubtype", [])[:3]) or "未标明"
        lines.append(f"## {item['title'] or '(无标题)'}")
        lines.append(f"- PMID：{item['pmid']}")
        lines.append(f"- 期刊：{item['journal'] or '未知'}")
        lines.append(f"- 日期：{item['pubdate'] or '未知'}")
        lines.append(f"- 作者：{authors}")
        lines.append(f"- 类型：{pubtypes}")
        lines.append(f"- 速读：{summarize_significance(item)}")
        lines.append(f"- 链接：{item['pubmed_url']}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Search PubMed and fetch abstracts.")
    parser.add_argument("--query", required=True, help="PubMed search query")
    parser.add_argument("--retmax", type=int, default=5, help="Number of papers to return")
    parser.add_argument("--sort", default="relevance", choices=("relevance", "pub+date"), help="PubMed sort order")
    parser.add_argument("--days", type=int, help="Restrict to the last N days")
    parser.add_argument("--mindate", help="Minimum publication date in YYYY-MM-DD")
    parser.add_argument("--maxdate", help="Maximum publication date in YYYY-MM-DD")
    parser.add_argument("--article-type", action="append", choices=tuple(ARTICLE_TYPE_MAP.keys()), help="Filter by publication/study type; can be repeated")
    parser.add_argument("--format", default="json", choices=("json", "markdown", "chinese-cards"))
    parser.add_argument("--insecure", action="store_true", help="Disable TLS certificate verification for broken local CA setups")
    args = parser.parse_args()

    if args.retmax < 1 or args.retmax > 50:
        print("--retmax must be between 1 and 50", file=sys.stderr)
        return 1
    if args.days is not None and args.days < 1:
        print("--days must be at least 1", file=sys.stderr)
        return 1

    context = build_ssl_context(args.insecure)
    article_types = args.article_type or []
    term = build_search_term(args.query, args.days, args.mindate, args.maxdate, article_types)
    try:
        pmids = esearch(term, args.retmax, args.sort, context)
        summaries = esummary(pmids, context)
        abstracts = efetch_abstracts(pmids, context)
    except urllib.error.URLError as exc:
        msg = str(exc.reason) if getattr(exc, "reason", None) else str(exc)
        if "CERTIFICATE_VERIFY_FAILED" in msg and not args.insecure:
            print("TLS verification failed. Retry with --insecure only if you trust your network.", file=sys.stderr)
            return 2
        raise

    items = build_items(pmids, summaries, abstracts)
    payload = {"query": args.query, "search_term": term, "count": len(items), "items": items}

    if args.format == "markdown":
        sys.stdout.write(format_markdown(items, args.query))
    elif args.format == "chinese-cards":
        sys.stdout.write(format_chinese_cards(items, args.query))
    else:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
