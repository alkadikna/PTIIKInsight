import asyncio
import nest_asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
import json
import pandas as pd
import os
from playwright.async_api import async_playwright
import re
import csv
from datetime import datetime

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

async def get_latest_issue_id(crawler):
    url = "https://j-ptiik.ub.ac.id/index.php/j-ptiik/issue/archive"
    schema = {
        "name": "Latest Issue ID",
        "baseSelector": "ul.issues_archive li div.obj_issue_summary",
        "fields": [
            {
                "name": "issue_id",
                "selector": "h2 a.title",
                "type": "attribute",
                "attribute": "href",
            }
        ],
    }

    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=JsonCssExtractionStrategy(schema)
    )

    result = await crawler.arun(url=url, config=run_config)
    if result.success:
        extracted_data = json.loads(result.extracted_content)
        issue_ids = [
            int(link.split("/")[-1]) for link in 
            (item.get("issue_id") for item in extracted_data) 
            if link and link.split("/")[-1].isdigit()
        ]
        print(f"Latest issue ID: {max(issue_ids)}")
        return max(issue_ids) if issue_ids else 0
    else:
        raise Exception(f"Failed to fetch latest issue ID: {result.error_message}")

async def crawl_article_titles(issue_id, crawler):
    url = f"https://j-ptiik.ub.ac.id/index.php/j-ptiik/issue/view/{issue_id}"
    schema = {
        "name": "Daftar Artikel",
        "baseSelector": "li.note-jptiik, div.heading",
        "fields": [
            {
                "name": "judul",
                "selector": "h3.title a",
                "type": "text",
            },
            {
                "name": "penulis",
                "selector": "div.authors",
                "type": "text",
            },
            {
                "name": "published",
                "selector": "div.published span.value.base",
                "type": "text",
            },
            {
                "name": "link_artikel",
                "selector": "h3.title a",
                "type": "attribute",
                "attribute": "href"
            }
        ],
    }

    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=JsonCssExtractionStrategy(schema)
    )

    result = await crawler.arun(url=url, config=run_config)
    if result.success:
        extracted_data = json.loads(result.extracted_content)
        return {issue_id: extracted_data}
    else:
        return {issue_id: f"Gagal crawling: {result.error_message}"}

async def crawl_abstract(link, crawler):
    print(f"[DEBUG] Mengambil abstrak dari: {link}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  
        page = await browser.new_page()
        try:
            await page.goto(link, wait_until="load", timeout=60000) 
        except Exception as e:
            print(f"[ERROR] Gagal membuka {link}: {e}")
            await browser.close()
            return ""

        # Check if abstract element exists
        abstrak_element = await page.query_selector("section.item.abstract > p")
        if abstrak_element:
            abstrak = await abstrak_element.inner_text()
            print(f"[DEBUG] Abstrak ditemukan lewat Playwright langsung.")
            await browser.close()
            return abstrak

        html = await page.content()
        with open("debug_abstrak.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("[WARNING] Tidak bisa temukan elemen abstrak langsung dari page.")
        await browser.close()
        return ""


async def main():
    async with AsyncWebCrawler() as crawler:
        latest_issue_id = await get_latest_issue_id(crawler)
        issue_ids = range(40, 44)  
        tasks = [crawl_article_titles(issue_id, crawler) for issue_id in issue_ids]
        results = await asyncio.gather(*tasks)

        all_data = []
        for result in results:
            for issue_id, articles in result.items():
                if isinstance(articles, list):
                    common_published = None
                    for article in articles:
                        pub = article.get("published")
                        if pub and pub != "N/A":
                            common_published = pub
                            break
                    for article in articles:
                        if article.get("judul", "N/A") == "N/A" and article.get("penulis", "N/A") == "N/A":
                            continue
                        
                        # Formatting published date
                        published = article.get("published", "N/A")
                        if published == "N/A" and common_published:
                            published = common_published

                        # Parsing tahun 
                        tahun = "N/A"
                        if published != "N/A":
                            try:
                                tahun = datetime.strptime(published.strip(), "%d %b %Y").year
                            except ValueError:
                                # Kalau format tidak cocok (misalnya hanya "2017" atau "Jan 2017")
                                match = re.search(r"\b\d{4}\b", published)
                                tahun = int(match.group(0)) if match else "N/A"

                        # Extracting authors into lists
                        penulis_raw = article.get("penulis", "N/A")
                        if penulis_raw != "N/A":
                            penulis_list = [p.strip() for p in penulis_raw.split(";") if p.strip()]
                        else:
                            penulis_list = ["N/A"]

                        link_artikel = article.get("link_artikel", "")
                        if link_artikel:
                            article_id = link_artikel.split("/")[-1]
                            abstract_url = f"https://j-ptiik.ub.ac.id/index.php/j-ptiik/article/view/{article_id}/0"
                            abstrak = await crawl_abstract(abstract_url, crawler)
                        else:
                            abstrak = ""

                        all_data.append({
                            "issue ID": issue_id,
                            "title": article.get("judul", "N/A"),
                            "abstract": abstrak,
                            "authors": penulis_list,
                            "journal_conference_name": "JPTIIK",
                            "publisher": "FILKOM UB",
                            "year": tahun,
                            "doi": link_artikel,
                            "group_name": "GuguGaga"
                        })
                else:
                    all_data.append({"Issue ID": issue_id, "Judul": articles})
        df = pd.DataFrame(all_data)

        with open(JSON_PATH, "w", encoding="utf-8") as json_file:
            json.dump(all_data, json_file, ensure_ascii=False, indent=2)
        
        return df

# Run and save
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "../data/raw/data_raw_v3.csv") 
JSON_PATH = os.path.join(BASE_DIR, "../data/raw/data_raw_v3.json")

df_articles = asyncio.run(main())
df_articles.to_csv(DATA_PATH, index=False)
df_articles.to_json(JSON_PATH, orient="records", indent=2, force_ascii=False)
print("Crawling results saved to", DATA_PATH)

