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
        "baseSelector": "li.note-jptiik",  # Adjust to HTML structure
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
                "selector": "div.published",
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

async def main():
    issue_ids = range(1, 107)  # ID issue yang merepresentasikan tahun terbit
    tasks = [crawl_article_titles(issue_id) for issue_id in issue_ids]
    results = await asyncio.gather(*tasks)

    # to df
    all_data = []
    for result in results:
        for issue_id, articles in result.items():
            if isinstance(articles, list):
                for article in articles:


                    all_data.append({
                        "Issue ID": issue_id,
                        "Judul": article.get("judul", "N/A"),
                        "Penulis": article.get("penulis", "N/A"),
                        "Tahun": article.get("published", "N/A"),
                    })
            else:
                all_data.append({"Issue ID": issue_id, "Judul": articles})

    df = pd.DataFrame(all_data)
    return df

# Run and save
df_articles = asyncio.run(main())
df_articles.to_csv('data_raw_v2.csv', index=False)
print("Crawling results saved to data_raw_v2.csv")
