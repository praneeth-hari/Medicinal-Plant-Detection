"""
PubMed Research Papers Endpoint
===============================
Provides reliable, cached querying of NCBI PubMed for medicinal plant research,
clinical trials, pharmacology reviews, and toxicological safety profiles.
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any

from fastapi import APIRouter, Query

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory LRU/TTL cache: query -> { "timestamp": float, "data": dict }
_CACHE: dict[str, dict[str, Any]] = {}
_CACHE_TTL = 3600.0  # 1 hour cache


def _fetch_from_ncbi(query: str, limit: int = 30) -> dict[str, Any]:
    """Execute esearch, esummary, and efetch against NCBI E-utilities."""
    clean_q = query.strip()
    tool_params = "&tool=MediPlantAI&email=info@mediplant.ai"

    # Step 1: ESearch
    search_url = (
        f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        f"?db=pubmed&term={urllib.parse.quote(clean_q)}&retmode=json&retmax={limit}&sort=relevance{tool_params}"
    )
    req = urllib.request.Request(search_url, headers={"User-Agent": "MediPlantAI/1.0"})
    with urllib.request.urlopen(req, timeout=12) as resp:
        search_data = json.loads(resp.read().decode("utf-8"))

    esearch_res = search_data.get("esearchresult", {})
    id_list = esearch_res.get("idlist", [])
    total_count = int(esearch_res.get("count", 0))

    if not id_list:
        return {"total_count": 0, "papers": []}

    ids_param = ",".join(id_list)

    # Step 2: ESummary
    sum_url = (
        f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        f"?db=pubmed&id={ids_param}&retmode=json{tool_params}"
    )
    req_sum = urllib.request.Request(sum_url, headers={"User-Agent": "MediPlantAI/1.0"})
    with urllib.request.urlopen(req_sum, timeout=12) as resp:
        sum_data = json.loads(resp.read().decode("utf-8")).get("result", {})

    # Step 3: EFetch for abstracts (best effort)
    abstract_map: dict[str, str] = {}
    try:
        fetch_url = (
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            f"?db=pubmed&id={ids_param}&rettype=abstract&retmode=xml{tool_params}"
        )
        req_fetch = urllib.request.Request(fetch_url, headers={"User-Agent": "MediPlantAI/1.0"})
        with urllib.request.urlopen(req_fetch, timeout=15) as resp:
            xml_text = resp.read().decode("utf-8", errors="replace")
            root = ET.fromstring(xml_text)
            for article in root.findall(".//PubmedArticle"):
                pmid_el = article.find(".//MedlineCitation/PMID")
                if pmid_el is not None and pmid_el.text:
                    pmid = pmid_el.text.strip()
                    abstract_texts = [
                        el.text.strip()
                        for el in article.findall(".//Abstract/AbstractText")
                        if el.text
                    ]
                    if abstract_texts:
                        abstract_map[pmid] = " ".join(abstract_texts)
    except Exception as exc:
        logger.warning("Could not fetch or parse PubMed XML abstracts: %s", exc)

    # Step 4: Assemble structured paper records
    papers = []
    for pid in id_list:
        item = sum_data.get(pid, {})
        authors = ", ".join([a.get("name", "") for a in item.get("authors", [])]) or "Unknown Authors"
        doi = ""
        for aid in item.get("articleids", []):
            if aid.get("idtype") == "doi":
                doi = aid.get("value", "")
                break

        papers.append({
            "id": pid,
            "title": item.get("title") or "Untitled Publication",
            "authors": authors,
            "journal": item.get("source") or "Unknown Journal",
            "pubDate": item.get("pubdate") or "N/A",
            "doi": doi,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",
            "abstract": abstract_map.get(pid) or "Abstract not available in public index.",
        })

    return {
        "total_count": total_count,
        "papers": papers,
    }


@router.get("/search")
async def search_papers(
    q: str = Query(..., description="Plant or medical research query string"),
    limit: int = Query(30, ge=1, le=80, description="Maximum number of papers to retrieve"),
) -> dict[str, Any]:
    """Search peer-reviewed literature indexed in NCBI PubMed."""
    cache_key = f"{q.strip().lower()}::{limit}"
    now = time.time()

    if cache_key in _CACHE:
        entry = _CACHE[cache_key]
        if now - entry["timestamp"] < _CACHE_TTL:
            return entry["data"]

    try:
        data = await asyncio.to_thread(_fetch_from_ncbi, q, limit=limit)
        _CACHE[cache_key] = {"timestamp": now, "data": data}
        return data
    except Exception as exc:
        logger.error("Failed to query NCBI PubMed: %s", exc)
        return {
            "total_count": 0,
            "papers": [],
            "error": str(exc),
        }
