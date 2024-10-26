import feedparser
import requests
from lxml import html
from typing import List, Dict, Optional
from datetime import datetime
import pytz
from rfeed import Item, Feed, Enclosure
import logging
from utils import get_headers
from email.utils import parsedate_to_datetime
import urllib.parse

def clean_infognu_url(url: str, feed_config: Dict) -> str:
    """Clean infognu.com URLs by removing the enrollment prefix."""
    if feed_config['link'] == 'https://infognu.com/':
        prefix = 'https://infognu.com/go/enroll?link='
        if url.startswith(prefix):
            return url[len(prefix):]
    return url

def get_absolute_url(url: str, base_url: str) -> str:
    """Convert relative URLs to absolute URLs."""
    if url.startswith(('http://', 'https://')):
        return url
    return urllib.parse.urljoin(base_url, url)

def process_feed(feed_config: Dict) -> Optional[List[Dict]]:
    """Process a single feed configuration and extract items."""
    try:
        feed = feedparser.parse(feed_config['rss_url'])
        results = []
        
        for entry in feed.entries[:feed_config['max_entries']]:
            try:
                response = requests.get(entry.link, headers=get_headers(), timeout=10)
                if response.status_code == 200:
                    tree = html.fromstring(response.content)
                    urls = tree.xpath(feed_config['xpath'])
                    
                    if urls:
                        # Clean the URL if it's from infognu.com
                        cleaned_url = clean_infognu_url(urls[0], feed_config)
                        
                        # Extract image URL using image_xpath
                        image_url = None
                        if 'image_xpath' in feed_config:
                            image_elements = tree.xpath(feed_config['image_xpath'])
                            if image_elements:
                                image_url = get_absolute_url(image_elements[0], entry.link)
                        
                        # Convert the published date to a datetime object
                        if 'published' in entry:
                            pub_date = parsedate_to_datetime(entry.published)
                        else:
                            pub_date = datetime.now(pytz.UTC)
                            
                        result = {
                            'title': entry.title,
                            'link': cleaned_url,
                            'description': entry.get('description', ''),
                            'pubDate': pub_date
                        }
                        
                        # Add image URL if found
                        if image_url:
                            result['image_url'] = image_url
                            
                        results.append(result)
            except Exception as e:
                logging.error(f"Error processing entry {entry.link}: {str(e)}")
                
        return results
    except Exception as e:
        logging.error(f"Error processing feed {feed_config['rss_url']}: {str(e)}")
        return None

def parse_existing_xml(filename: str) -> List[Item]:
    """Parse existing XML feed and return items."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            feed = feedparser.parse(f.read())
            items = []
            for entry in feed.entries:
                item_kwargs = {
                    'title': entry.title,
                    'link': entry.link,
                    'description': entry.description,
                    'pubDate': parsedate_to_datetime(entry.published)
                }
                
                # Handle enclosures (images)
                if hasattr(entry, 'enclosures') and entry.enclosures:
                    enclosure = entry.enclosures[0]
                    if 'url' in enclosure:
                        item_kwargs['enclosure'] = Enclosure(
                            url=enclosure.url,
                            length=enclosure.get('length', '0'),
                            type=enclosure.get('type', 'image/jpeg')
                        )
                
                items.append(Item(**item_kwargs))
            return items
    except FileNotFoundError:
        return []
    except Exception as e:
        logging.error(f"Error parsing existing XML: {str(e)}")
        return []
