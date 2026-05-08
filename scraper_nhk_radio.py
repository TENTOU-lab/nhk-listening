#!/usr/bin/env python3
"""
NHK Radio News Scraper - 单条版本
只抓取最新的1条广播音频

使用方法:
    python scraper_nhk_radio.py
"""

import requests
import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime

# NHK Radio News RSS
RSS_URL = "https://www.nhk.or.jp/s-media/news/podcast/list/v1/all.xml"
OUTPUT_FILE = "articles_nhk_radio.json"

def parse_rss():
    """Fetch and parse NHK Radio News RSS feed."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(RSS_URL, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text

def parse_datetime(date_str):
    """Parse RFC 2822 date format used in RSS."""
    try:
        formats = [
            '%a, %d %b %Y %H:%M:%S %z',
            '%a, %d %b %Y %H:%M:%S +0000',
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt
            except:
                continue
        return None
    except:
        return None

def process_item(item):
    """Process a single RSS item."""
    # Get title
    title = ""
    title_elem = item.find('title')
    if title_elem is not None and title_elem.text:
        title = title_elem.text.strip()
    
    # Get audio URL from enclosure
    mp3_url = ""
    enclosure = item.find('enclosure')
    if enclosure is not None:
        mp3_url = enclosure.get('url', '')
    
    # Get publication date
    pub_date = ""
    parsed_date = None
    date_elem = item.find('pubDate')
    if date_elem is not None and date_elem.text:
        pub_date = date_elem.text.strip()
        parsed_date = parse_datetime(pub_date)
        if parsed_date:
            pub_date = parsed_date.strftime('%Y-%m-%d %H:%M')
    
    # Get GUID
    guid = ""
    guid_elem = item.find('guid')
    if guid_elem is not None and guid_elem.text:
        guid = guid_elem.text.strip()
    
    # Get duration
    duration = ""
    itunes_duration = item.find('itunes:duration')
    if itunes_duration is not None and itunes_duration.text:
        duration = itunes_duration.text.strip()
    
    return {
        'id': guid or (parsed_date.strftime('%Y%m%d') if parsed_date else ''),
        'title': title,
        'mp3_url': mp3_url,
        'date': pub_date,
        'guid': guid,
        'duration': duration,
        # Text content - must be added manually
        'paragraphs': [],
        'sentences_beginner': [],
        'sentences_intermediate': [],
        'sentences_advanced': [],
        'translations': [],
        'has_text': False
    }

def main():
    print("Fetching NHK Radio News RSS feed...")
    try:
        xml_content = parse_rss()
    except Exception as e:
        print(f"Error fetching RSS: {e}")
        return
    
    root = ET.fromstring(xml_content)
    
    channel = root.find('channel')
    if channel is None:
        print("Error: No channel element found in RSS")
        return
    
    # Get first (latest) item only
    items = []
    for item in channel.findall('item'):
        if len(items) >= 1:  # Only get the latest 1
            break
        article = process_item(item)
        items.append(article)
    
    if items:
        latest = items[0]
        print(f"\n获取到最新广播:")
        print(f"  标题: {latest['title']}")
        print(f"  日期: {latest['date']}")
        print(f"  时长: {latest['duration']}")
        print(f"  音频: {latest['mp3_url']}")
    else:
        print("未获取到任何广播")
        return
    
    # Save to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    
    print(f"\n已保存到 {OUTPUT_FILE}")
    print("\n提示: 运行后请在网页上手动输入日文文字进行练习")

if __name__ == '__main__':
    main()
