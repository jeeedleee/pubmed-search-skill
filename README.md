# pubmed-search-skill

English | [中文](#中文说明)

A Codex skill for searching PubMed and generating concise literature summaries.

## Overview

This repository contains a `Codex skill` that helps search PubMed, fetch paper metadata and abstracts, filter by date or study type, and generate readable outputs for literature review workflows.

## Features

- Search PubMed by keyword
- Filter by recent days or explicit date range
- Filter by study type:
  - `review`
  - `systematic-review`
  - `meta-analysis`
  - `clinical-trial`
  - `randomized-controlled-trial`
- Fetch title, PMID, journal, publication date, DOI, and abstract
- Output as:
  - JSON
  - Markdown
  - Chinese reading cards

## Repository Layout

```text
pubmed-search-skill/
|- SKILL.md
|- README.md
|- agents/
|  |- openai.yaml
|- references/
|  |- eutils.md
|- scripts/
   |- pubmed_search.py
```

## Install into Codex

Copy this folder into your Codex skills directory as:

```text
~/.codex/skills/pubmed-search
```

Then restart Codex.

## Script Usage

Basic search:

```bash
python scripts/pubmed_search.py --query "glioblastoma immunotherapy" --retmax 5 --format json
```

Recent papers:

```bash
python scripts/pubmed_search.py --query "CRISPR delivery" --days 30 --retmax 8 --format markdown
```

Filter by study type:

```bash
python scripts/pubmed_search.py --query "lung cancer immunotherapy" --article-type review --retmax 5 --format markdown
```

Chinese reading cards:

```bash
python scripts/pubmed_search.py --query "KRAS G12D lung cancer" --article-type review --retmax 5 --format chinese-cards
```

## Notes

- The script uses the public NCBI E-utilities API.
- No API key is required for light interactive use.
- `--insecure` exists only as a fallback for broken local TLS certificate setups and should be used cautiously.

## 中文说明

这是一个用于 `Codex` 的 `PubMed 检索 skill`，适合做医学文献查询、摘要抓取、按日期或文献类型筛选，以及生成中文速读卡片。

### 功能

- 按关键词检索 PubMed
- 按最近几天或指定日期范围筛选
- 按文献类型筛选：
  - `review`
  - `systematic-review`
  - `meta-analysis`
  - `clinical-trial`
  - `randomized-controlled-trial`
- 获取标题、PMID、期刊、日期、DOI 和摘要
- 支持输出：
  - JSON
  - Markdown
  - 中文文献速读卡片

### 安装到 Codex

把本仓库目录复制到：

```text
~/.codex/skills/pubmed-search
```

然后重启 Codex。

### 脚本示例

基础检索：

```bash
python scripts/pubmed_search.py --query "glioblastoma immunotherapy" --retmax 5 --format json
```

检索最近文献：

```bash
python scripts/pubmed_search.py --query "CRISPR delivery" --days 30 --retmax 8 --format markdown
```

按文献类型筛选：

```bash
python scripts/pubmed_search.py --query "lung cancer immunotherapy" --article-type review --retmax 5 --format markdown
```

输出中文速读卡片：

```bash
python scripts/pubmed_search.py --query "KRAS G12D lung cancer" --article-type review --retmax 5 --format chinese-cards
```

### 说明

- 脚本使用公开的 NCBI E-utilities API。
- 轻量交互使用通常不需要 API key。
- `--insecure` 只是为本地 TLS 证书异常环境准备的兜底开关，使用时要谨慎。
