from typing import List, Dict
from rfeed import Item, Feed, Enclosure
from datetime import datetime
import pytz
import logging
from feed_processor import parse_existing_xml

def create_merged_rss_feed(results: List[Dict], title: str, description: str, link: str, existing_items: List[Item]) -> str:
    """Create a merged RSS feed from results and existing items."""
    items = []
    for result in results:
        item_kwargs = {
            'title': result['title'],
            'link': result['link'],
            'description': result['description'],
            'pubDate': result['pubDate']
        }
        
        # Add image enclosure if available
        if 'image_url' in result:
            item_kwargs['enclosure'] = Enclosure(
                url=result['image_url'],
                length='0',  # Length is required but not critical for images
                type='image/jpeg'  # Default to JPEG, could be made more specific if needed
            )
        
        items.append(Item(**item_kwargs))
    
    # Combine new and existing items, removing duplicates
    all_items = items + existing_items
    unique_items = {item.link: item for item in all_items}.values()
    
    feed = Feed(
        title=title,
        link=link,
        description=description,
        language="en-US",
        lastBuildDate=datetime.now(pytz.UTC),
        items=list(unique_items)
    )
    
    return feed.rss()

def merge_all_feeds(scraped_filename: str, final_merge_filename: str) -> str:
    """Merge multiple RSS feeds into a single feed."""
    try:
        with open(scraped_filename, 'r', encoding='utf-8') as f:
            scraped_content = f.read()
            
        feed = Feed(
            title="Final Merged Feed",
            link="https://example.com/final-feed",
            description="Combined feed from multiple sources",
            language="en-US",
            lastBuildDate=datetime.now(pytz.UTC),
            items=parse_existing_xml(scraped_filename)
        )
        
        merged_content = feed.rss()
        with open(final_merge_filename, 'w', encoding='utf-8') as f:
            f.write(merged_content)
            
        return merged_content
    except Exception as e:
        logging.error(f"Error merging feeds: {str(e)}")
        return ""
