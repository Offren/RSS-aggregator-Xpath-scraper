import os
import time
import schedule
import logging
from typing import List, Dict
from config import (
    SCRAPED_FILENAME, FINAL_MERGE_FILENAME,
    GAMERPOWER_GAMES_FILENAME, GAMERPOWER_LOOT_FILENAME,
    REPO_NAME, MAX_RUNTIME_HOURS, FEEDS,
    GAMERPOWER_GAMES_CONFIG, GAMERPOWER_LOOT_CONFIG
)
from utils import setup_logging
from feed_processor import process_feed, parse_existing_xml
from feed_generator import create_merged_rss_feed, merge_all_feeds
from github_uploader import upload_to_github
from gamerpower_processor import process_single_gamerpower_feed, create_gamerpower_feed

def process_gamerpower() -> None:
    """Process GamerPower feeds and upload to GitHub."""
    # Process games feed
    games_results = process_single_gamerpower_feed(GAMERPOWER_GAMES_CONFIG)
    if games_results:
        games_feed = create_gamerpower_feed(games_results, GAMERPOWER_GAMES_CONFIG, GAMERPOWER_GAMES_FILENAME)
        with open(GAMERPOWER_GAMES_FILENAME, "w", encoding="utf-8") as f:
            f.write(games_feed)
        logging.info(f"GamerPower games RSS feed saved as '{GAMERPOWER_GAMES_FILENAME}'")
        
        github_token = os.environ.get("GITHUB_TOKEN")
        if github_token:
            upload_to_github(github_token, REPO_NAME, GAMERPOWER_GAMES_FILENAME, games_feed)
        else:
            logging.error("GITHUB_TOKEN not set")

    # Process loot feed
    loot_results = process_single_gamerpower_feed(GAMERPOWER_LOOT_CONFIG)
    if loot_results:
        loot_feed = create_gamerpower_feed(loot_results, GAMERPOWER_LOOT_CONFIG, GAMERPOWER_LOOT_FILENAME)
        with open(GAMERPOWER_LOOT_FILENAME, "w", encoding="utf-8") as f:
            f.write(loot_feed)
        logging.info(f"GamerPower loot RSS feed saved as '{GAMERPOWER_LOOT_FILENAME}'")
        
        github_token = os.environ.get("GITHUB_TOKEN")
        if github_token:
            upload_to_github(github_token, REPO_NAME, GAMERPOWER_LOOT_FILENAME, loot_feed)
        else:
            logging.error("GITHUB_TOKEN not set")

def job() -> None:
    """Main job function to process feeds and update GitHub."""
    # Process regular feeds
    all_results = []
    for feed_config in FEEDS:
        results = process_feed(feed_config)
        if results:
            all_results.extend(results)

    if all_results:
        existing_items = parse_existing_xml(SCRAPED_FILENAME)
        
        scraped_xml_feed = create_merged_rss_feed(
            all_results,
            "Merged RSS Feed",
            "A merged feed containing items from multiple sources",
            "https://example.com/merged-feed",
            existing_items
        )

        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            logging.error("GITHUB_TOKEN not set")
            return

        if scraped_xml_feed:
            with open(SCRAPED_FILENAME, "w", encoding="utf-8") as f:
                f.write(scraped_xml_feed)
            
            logging.info(f"Scraped RSS feed saved as '{SCRAPED_FILENAME}'")
            
            final_merged_feed = merge_all_feeds(SCRAPED_FILENAME, FINAL_MERGE_FILENAME)
            logging.info(f"Final merged RSS feed saved as '{FINAL_MERGE_FILENAME}'")
            
            upload_to_github(github_token, REPO_NAME, SCRAPED_FILENAME, scraped_xml_feed)
            upload_to_github(github_token, REPO_NAME, FINAL_MERGE_FILENAME, final_merged_feed)
    else:
        logging.warning("No matching content found in processed feeds")

    # Process GamerPower feeds
    process_gamerpower()

def main() -> None:
    """Main function to run the RSS feed processor."""
    setup_logging()
    logging.info("Starting RSS feed processor")

    if not os.environ.get("GITHUB_TOKEN"):
        logging.error("GITHUB_TOKEN environment variable not set")
        return

    # Initial run
    job()

    # Schedule recurring runs
    schedule.every(5).minutes.do(job)
    logging.info("Scheduled to run every 5 minutes")

    start_time = time.time()
    while True:
        schedule.run_pending()
        time.sleep(5)
        
        if time.time() - start_time > MAX_RUNTIME_HOURS * 3600:
            logging.info(f"Maximum runtime of {MAX_RUNTIME_HOURS} hours reached")
            break

if __name__ == "__main__":
    main()