#!/usr/bin/env python3
"""Debug script to test API responses"""

import requests
import json
import re

def test_word(word):
    """Test fetching a word from Wiktionary"""

    # Test Polish Wiktionary
    print(f"\n{'='*60}")
    print(f"Testing word: {word}")
    print(f"{'='*60}\n")

    url = "https://pl.wiktionary.org/w/api.php"
    params = {
        'action': 'parse',
        'page': word,
        'format': 'json',
        'prop': 'text|sections',
        'disabletoc': 1
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'error' in data:
            print(f"Error: {data['error']}")
            return

        if 'parse' not in data:
            print("No parse data in response")
            return

        html_content = data['parse']['text']['*']

        print(f"HTML length: {len(html_content)}")
        print("\nFirst 2000 characters of HTML:")
        print(html_content[:2000])

        # Test the parsing
        print("\n" + "="*60)
        print("Testing parsing...")
        print("="*60 + "\n")

        # Find headings
        headings = re.findall(r'<h[234][^>]*>(.*?)</h[234]>', html_content, re.IGNORECASE)
        print(f"Found {len(headings)} headings:")
        for i, h in enumerate(headings[:10]):
            clean_h = re.sub(r'<[^>]+>', '', h)
            print(f"  {i+1}. {clean_h.strip()}")

        # Find list items
        list_items = re.findall(r'<li[^>]*>(.*?)</li>', html_content, re.DOTALL)
        print(f"\nFound {len(list_items)} list items:")
        for i, item in enumerate(list_items[:10]):
            clean_item = re.sub(r'<[^>]+>', '', item)
            clean_item = re.sub(r'\s+', ' ', clean_item).strip()
            if len(clean_item) > 10:
                print(f"  {i+1}. {clean_item[:100]}...")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == '__main__':
    test_word('dobra')
