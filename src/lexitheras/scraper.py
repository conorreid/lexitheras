"""
Perseus vocabulary scraper
"""

import requests
from bs4 import BeautifulSoup
import re


class PerseusVocabScraper:
    def __init__(self):
        self.base_url = "https://vocab.perseus.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
    
    def scrape_vocabulary_list(self, text_urn, get_all_pages=True):
        """Scrape vocabulary from Perseus for a given text URN"""
        vocab_items = []
        
        # Use page=all to get all vocabulary at once
        if get_all_pages:
            url = f"{self.base_url}/word-list/{text_urn}/?page=all"
        else:
            url = f"{self.base_url}/word-list/{text_urn}/"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Find vocabulary table
        table = soup.find('table', class_='word-list')
        if not table:
            raise ValueError("Could not find vocabulary table on page")
        
        # Get all rows (skip header)
        rows = table.find_all('tr')[1:]
        
        for idx, row in enumerate(rows, 1):
            # Extract Greek word from element with class 'lemma_text'
            lemma_elem = row.find(class_='lemma_text')
            if not lemma_elem:
                continue
            greek_word = lemma_elem.text.strip()
            
            # Extract translation from td with class 'shortdef'
            shortdef_elem = row.find('td', class_='shortdef')
            if not shortdef_elem:
                continue
            translation = shortdef_elem.text.strip()
            
            # Extract count from td with class 'count'
            count_elem = row.find('td', class_='count')
            count = 0
            if count_elem:
                count_text = count_elem.text.strip()
                # Remove commas and convert to int
                try:
                    count = int(count_text.replace(',', ''))
                except ValueError:
                    count = 0
            
            vocab_items.append({
                'rank': idx,
                'word': greek_word,
                'lemma': greek_word,
                'translation': translation,
                'count': count
            })
        
        return vocab_items