"""
Search functionality for Perseus texts
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin


class PerseusTextSearcher:
    def __init__(self):
        self.base_url = "https://vocab.perseus.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        self.cache_file = os.path.expanduser('~/.lexitheras_cache.json')
        self.cache_duration = timedelta(days=7)
    
    def _load_cache(self):
        """Load cached text catalog"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    cache_time = datetime.fromisoformat(cache['timestamp'])
                    if datetime.now() - cache_time < self.cache_duration:
                        return cache['texts']
            except:
                pass
        return None
    
    def _save_cache(self, texts):
        """Save text catalog to cache"""
        cache = {
            'timestamp': datetime.now().isoformat(),
            'texts': texts
        }
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    
    def get_all_texts(self):
        """Scrape all available texts from Perseus editions page"""
        # Try cache first
        cached = self._load_cache()
        if cached:
            return cached
        
        url = f"{self.base_url}/editions/"
        response = self.session.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        texts = []
        
        current_author = None
        
        # Process all elements in order to maintain author groupings
        for element in soup.find_all(['h4', 'a']):
            if element.name == 'h4':
                # New author section
                current_author = element.text.strip()
            elif element.name == 'a' and '/word-list/' in element.get('href', ''):
                # Text under current author
                title = element.text.strip()
                href = element.get('href', '')
                
                # Extract URN from URL
                urn_match = re.search(r'word-list/(urn:cts:greekLit:[^/]+)', href)
                if urn_match:
                    urn = urn_match.group(1)
                    texts.append({
                        'author': current_author or 'Unknown',
                        'title': title,
                        'urn': urn,
                        'url': urljoin(self.base_url, href)
                    })
        
        # Save to cache
        self._save_cache(texts)
        return texts
    
    def search_texts(self, query):
        """Search for texts by title or author"""
        texts = self.get_all_texts()
        query_lower = query.lower()
        
        matches = []
        
        # First try exact matches
        for text in texts:
            if query_lower in text['title'].lower() or query_lower in text['author'].lower():
                matches.append(text)
        
        # If no matches, try fuzzy matching
        if not matches:
            # Common variations
            variations = {
                'iliad': ['iliad', 'ilias'],
                'odyssey': ['odyssey', 'odyssea'],
                'anabasis': ['anabasis', 'anab'],
                'symposium': ['symposium', 'symp'],
                'republic': ['republic', 'politeia', 'res publica'],
                'homer': ['homer', 'homerus'],
                'plato': ['plato', 'platon'],
                'xenophon': ['xenophon', 'xenophon']
            }
            
            # Check variations
            for key, variants in variations.items():
                if query_lower in variants:
                    for text in texts:
                        if any(v in text['title'].lower() or v in text['author'].lower() 
                               for v in [key] + variants):
                            matches.append(text)
        
        return matches