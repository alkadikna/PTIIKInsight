import asyncio
import nest_asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
import json
import pandas as pd

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Function to run async tasks
# def run_async_task(task):
#     loop = asyncio.get_event_loop()
#     if loop.is_running():
#         return asyncio.create_task(task)
#     else:
#         return loop.run_until_complete(task)

async def crawl_article_titles(issue_id):
    # URL based on issue ID
    url = f"https://j-ptiik.ub.ac.id/index.php/j-ptiik/issue/view/{issue_id}"
    
    # Extraction schema to get article titles
    schema = {
        "name": "Daftar Artikel",
        "baseSelector": "li.note-jptiik",  # Adjust to HTML structure
        "fields": [
            {
                "name": "judul",
                "selector": "h3.title a",
                "type": "text",
            }
        ],
    }

    # Crawling configuration
    run_config = CrawlerRunConfig(
        bypass_cache=True,
        extraction_strategy=JsonCssExtractionStrategy(schema)
    )

    # Start crawling process
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=run_config)
        if result.success:
            extracted_data = json.loads(result.extracted_content)
            return {issue_id: [item["judul"] for item in extracted_data]}
        else:
            return {issue_id: f"Gagal crawling: {result.error_message}"}

async def main():
    issue_ids = range(101, 106)  # ID issue yang merepresentasikan tahun terbit
    tasks = [crawl_article_titles(issue_id) for issue_id in issue_ids]
    results = await asyncio.gather(*tasks)

    # to df
    all_data = []
    for result in results:
        for issue_id, titles in result.items():
            if isinstance(titles, list):
                for title in titles:
                    all_data.append({"Issue ID": issue_id, "Judul": title})
            else:
                all_data.append({"Issue ID": issue_id, "Judul": titles})

    df = pd.DataFrame(all_data)
    return df

# Run and save
df_articles = asyncio.run(main())
df_articles.to_csv('crawling_results.csv', index=False)
print("Crawling results saved to crawling_results.csv")