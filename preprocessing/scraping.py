import asyncio
import nest_asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
import json
import pandas as pd

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

async def crawl_article_titles(issue_id):
    # URL based on issue ID
    url = f"https://j-ptiik.ub.ac.id/index.php/j-ptiik/issue/view/{issue_id}"
    # Extraction schema to get article titles, authors, and years
    schema = {
        "name": "Daftar Artikel",
        "baseSelector": "li.note-jptiik, div.heading",  # Adjust to HTML structure
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
            }
        ],
    }

    # Crawling configuration
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=JsonCssExtractionStrategy(schema)
    )

    # Start crawling process
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=run_config)
        if result.success:
            extracted_data = json.loads(result.extracted_content)
            return {issue_id: extracted_data}
        else:
            return {issue_id: f"Gagal crawling: {result.error_message}"}

async def get_latest_issue_id():
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

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=run_config)
        if result.success:
            extracted_data = json.loads(result.extracted_content)
            issue_ids = [
                int(link.split("/")[-1]) for link in 
                (item.get("issue_id") for item in extracted_data) 
                if link and link.split("/")[-1].isdigit()
            ]
            print(f"Latest issue IDs: {max(issue_ids)}")
            return max(issue_ids) if issue_ids else 0
        else:
            raise Exception(f"Failed to fetch latest issue ID: {result.error_message}")

async def main():
    latest_issue_id = await get_latest_issue_id()
    issue_ids = range(1, latest_issue_id + 1)
    tasks = [crawl_article_titles(issue_id) for issue_id in issue_ids]
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
                    published = article.get("published", "N/A")
                    if published == "N/A" and common_published:
                        published = common_published
                    all_data.append({
                        "Issue ID": issue_id,
                        "Judul": article.get("judul", "N/A"),
                        "Penulis": article.get("penulis", "N/A"),
                        "Tahun": published,
                    })
            else:
                all_data.append({"Issue ID": issue_id, "Judul": articles})
    
    df = pd.DataFrame(all_data)
    return df

# Run and save
df_articles = asyncio.run(main())
df_articles.to_csv('../data/data_raw_api.csv', index=False)
print("Crawling results saved to data_raw_api.csv")
