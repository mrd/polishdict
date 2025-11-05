#!/usr/bin/env python3
"""Save HTML from Wiktionary for debugging"""

import requests
import json

def save_html(word):
    """Save HTML from both Wiktionaries"""

    # Polish Wiktionary
    print(f"Fetching from Polish Wiktionary...")
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

        print(f"Response status: {response.status_code}")

        data = response.json()

        if 'error' in data:
            print(f"API error: {data['error']}")
            return

        if 'parse' in data:
            html = data['parse']['text']['*']
            filename = f"{word}_pl_wiktionary.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"Saved Polish Wiktionary HTML to {filename}")
            print(f"Size: {len(html)} bytes")
    except Exception as e:
        print(f"Error: {e}")

    # English Wiktionary
    print(f"\nFetching from English Wiktionary...")
    url = "https://en.wiktionary.org/w/api.php"

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if 'parse' in data:
            html = data['parse']['text']['*']
            filename = f"{word}_en_wiktionary.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"Saved English Wiktionary HTML to {filename}")
            print(f"Size: {len(html)} bytes")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 save_html.py <word>")
        sys.exit(1)

    save_html(sys.argv[1])
