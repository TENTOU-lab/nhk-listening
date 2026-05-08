#!/usr/bin/env python3
"""
NHK Easier RSS Scraper
Fetches articles from nhkeasier.com RSS feed and saves to JSON
"""

import requests
import xml.etree.ElementTree as ET
import json
import re
from html import unescape
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

RSS_URL = "https://nhkeasier.com/feed/"
OUTPUT_FILE = "articles.json"
JST_OFFSET = timedelta(hours=9)

def parse_rss():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(RSS_URL, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text

def get_element_text(elem, tag, default=""):
    child = elem.find(tag)
    if child is not None and child.text:
        return child.text.strip()
    return default

def extract_clean_text(html):
    """Extract clean Japanese text by stripping ALL HTML tags including ruby markup.
    Returns a list of paragraphs."""
    if not html:
        return []
    html = unescape(html)
    soup = BeautifulSoup(html, 'html.parser')
    
    # Strip all ruby-related tags, keep text only
    for tag_name in ['ruby', 'rb', 'rt', 'rp']:
        for tag in soup.find_all(tag_name):
            tag.unwrap()
    
    # Remove img and other non-text tags
    for tag in soup.find_all(['img', 'script', 'style', 'iframe']):
        tag.decompose()
    
    paragraphs = []
    for p in soup.find_all('p'):
        text = p.get_text(separator=' ', strip=True)
        # Remove extra spaces between Japanese characters
        text = re.sub(r'\s+', ' ', text)
        # Remove spaces between Japanese characters (kanji + hiragana + katakana)
        text = re.sub(r'([\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff])\s+', r'\1', text)
        text = re.sub(r'\s+([\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff])', r'\1', text)
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        if text:
            paragraphs.append(text)
    
    if not paragraphs:
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'([\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff])\s+', r'\1', text)
        text = re.sub(r'\s+([\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff])', r'\1', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        if text:
            paragraphs = [text]
    
    return paragraphs

def split_sentences_beginner(text):
    """Split into short segments by 、 and 。"""
    sentences = []
    parts = re.split(r'([、。])', text)
    current = ""
    for part in parts:
        current += part
        if part in ['、', '。']:
            s = current.strip()
            if s:
                sentences.append(s)
            current = ""
    if current.strip():
        sentences.append(current.strip())
    return [s for s in sentences if s]

def split_sentences_intermediate(text):
    """Split by 。 only for complete sentences"""
    sentences = []
    parts = re.split(r'([。])', text)
    current = ""
    for part in parts:
        current += part
        if part == '。':
            s = current.strip()
            if s:
                sentences.append(s)
            current = ""
    if current.strip():
        sentences.append(current.strip())
    return [s for s in sentences if s]

def extract_image_from_description(html):
    html = unescape(html)
    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html)
    if match:
        return match.group(1)
    return ""

def parse_date(date_str):
    date_str = date_str.strip()
    try:
        date_str = re.sub(r'^[A-Za-z]+,\s*', '', date_str)
        dt = datetime.strptime(date_str, '%d %b %Y %H:%M:%S %z')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return datetime.now().strftime('%Y-%m-%d')

def parse_item(item_xml, index):
    title = get_element_text(item_xml, 'title', "")
    link = get_element_text(item_xml, 'link', "")
    
    article_id = str(index + 1)
    if link:
        match = re.search(r'/story/(\d+)/', link)
        if match:
            article_id = match.group(1)
    
    description_html = get_element_text(item_xml, 'description', "")
    
    mp3_url = ""
    enclosure = item_xml.find('enclosure')
    if enclosure is not None:
        mp3_url = enclosure.get('url', '')
    if not mp3_url:
        for elem in item_xml.iter():
            if 'enclosure' in elem.tag.lower():
                mp3_url = elem.get('url', '')
                break
    
    pubdate = get_element_text(item_xml, 'pubDate', "")
    pubdate = parse_date(pubdate)
    
    # Get clean paragraphs (plain Japanese text without ruby)
    paragraphs = extract_clean_text(description_html)
    
    # Combine all text for sentence splitting
    all_text = " ".join(paragraphs)
    all_text = re.sub(r'\s+', '', all_text)
    
    sentences_beginner = split_sentences_beginner(all_text)
    sentences_intermediate = split_sentences_intermediate(all_text)
    sentences_advanced = [p for p in paragraphs if p]
    
    image_url = extract_image_from_description(description_html)
    
    # Translations: nhkeasier.com doesn't provide them
    # Placeholder - will be added manually later
    translations = [""] * len(sentences_advanced)
    
    return {
        "id": article_id,
        "title": title,
        "link": link,
        "mp3_url": mp3_url,
        "date": pubdate,
        "image_url": image_url,
        "paragraphs": paragraphs,
        "sentences_beginner": sentences_beginner,
        "sentences_intermediate": sentences_intermediate,
        "sentences_advanced": sentences_advanced,
        "translations": translations
    }

def main():
    print(f"Fetching RSS feed from {RSS_URL}...")
    
    try:
        xml_content = parse_rss()
        print(f"Received {len(xml_content)} bytes")
        
        root = ET.fromstring(xml_content)
        items = root.findall('.//item')
        
        if not items:
            channel = root.find('.//channel')
            if channel is not None:
                items = channel.findall('item')
        
        print(f"Found {len(items)} articles")
        
        articles = []
        for i, item in enumerate(items):
            try:
                article = parse_item(item, i)
                articles.append(article)
                print(f"  [{i+1}] ID:{article['id']} - {article['title'][:40]}...")
            except Exception as e:
                print(f"  Error parsing item {i}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        now = datetime.now() + JST_OFFSET
        output_data = {
            "last_updated": now.strftime('%Y-%m-%d'),
            "last_updated_time": now.strftime('%Y-%m-%d %H:%M:%S JST'),
            "total_articles": len(articles),
            "source_url": RSS_URL,
            "articles": articles
        }
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\nSuccessfully saved {len(articles)} articles to {OUTPUT_FILE}")
        
    except requests.RequestException as e:
        print(f"Network error: {e}")
        raise
    except ET.ParseError as e:
        print(f"XML parse error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    main()
