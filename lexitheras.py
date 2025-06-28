#!/usr/bin/env python3
"""
Lexitheras - Perseus Vocabulary List to Anki Deck Converter
Scrapes Greek vocabulary lists from Perseus and creates Anki decks
"""

import requests
from bs4 import BeautifulSoup
import genanki
import random
import click
import re
from urllib.parse import urljoin
import json
import os
from datetime import datetime, timedelta


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


class PerseusVocabScraper:
    def __init__(self):
        self.base_url = "https://vocab.perseus.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
    
    def scrape_vocabulary_list(self, text_urn, get_all_pages=True):
        """Scrape vocabulary from Perseus for a given text URN"""
        if get_all_pages:
            url = f"{self.base_url}/word-list/{text_urn}/?page=all"
        else:
            url = f"{self.base_url}/word-list/{text_urn}/"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        vocab_items = []
        
        # Find vocabulary table
        table = soup.find('table', class_='word-list')
        if not table:
            raise ValueError("Could not find vocabulary table on page")
        
        rows = table.find_all('tr')[1:]  # Skip header row
        
        for idx, row in enumerate(rows, 1):
            cells = row.find_all('td')
            if len(cells) >= 2:
                # Extract data from cells
                # Column 0: Greek word
                # Column 1: English translation/definition
                greek_word = cells[0].text.strip()
                translation = cells[1].text.strip()
                
                vocab_items.append({
                    'rank': idx,  # Use row position as rank
                    'word': greek_word,
                    'lemma': greek_word,  # Perseus doesn't separate lemma in this view
                    'translation': translation
                })
        
        return vocab_items


class AnkiDeckCreator:
    def __init__(self, deck_name):
        self.deck_id = random.randrange(1 << 30, 1 << 31)
        self.deck = genanki.Deck(self.deck_id, deck_name)
        self.model = self._create_model()
    
    def _create_model(self):
        """Create Anki note model for Greek vocabulary"""
        return genanki.Model(
            random.randrange(1 << 30, 1 << 31),
            'Greek Vocabulary',
            fields=[
                {'name': 'Greek'},
                {'name': 'Translation'},
                {'name': 'Lemma'},
                {'name': 'Rank'}
            ],
            templates=[
                {
                    'name': 'Greek to English',
                    'qfmt': '{{Greek}}<br><small>Rank: {{Rank}}</small>',
                    'afmt': '{{FrontSide}}<hr id="answer">{{Translation}}<br><br><small>Lemma: {{Lemma}}</small>',
                }
            ],
            css='''
            .card {
                font-family: arial;
                font-size: 20px;
                text-align: center;
                color: black;
                background-color: white;
            }
            '''
        )
    
    def add_vocabulary_items(self, vocab_items):
        """Add vocabulary items to the deck"""
        for item in vocab_items:
            note = genanki.Note(
                model=self.model,
                fields=[
                    item['word'],
                    item['translation'],
                    item['lemma'],
                    str(item['rank'])
                ]
            )
            self.deck.add_note(note)
    
    def save_deck(self, filename):
        """Save the deck to a .apkg file"""
        genanki.Package(self.deck).write_to_file(filename)


@click.command()
@click.argument('text_identifier')
@click.option('--output', '-o', default=None, help='Output filename for Anki deck')
@click.option('--deck-name', '-n', default=None, help='Name for the Anki deck')
@click.option('--list-texts', '-l', is_flag=True, help='List all available texts')
@click.option('--search-only', '-s', is_flag=True, help='Only search, don\'t create deck')
def main(text_identifier, output, deck_name, list_texts, search_only):
    """
    Create an Anki deck from a Perseus vocabulary list.
    
    TEXT_IDENTIFIER: Either a URN (e.g., urn:cts:greekLit:tlg0012.tlg001.perseus-grc2)
                     or a search term (e.g., "iliad", "homer", "symposium")
    """
    searcher = PerseusTextSearcher()
    
    # Handle --list-texts flag
    if list_texts:
        click.echo("Fetching all available texts...")
        texts = searcher.get_all_texts()
        
        # Group by author
        by_author = {}
        for text in texts:
            author = text['author']
            if author not in by_author:
                by_author[author] = []
            by_author[author].append(text)
        
        # Display grouped
        for author in sorted(by_author.keys()):
            click.echo(f"\n{click.style(author, bold=True)}:")
            for text in by_author[author]:
                click.echo(f"  - {text['title']} ({text['urn']})")
        return
    
    # Check if text_identifier is a URN or search term
    if text_identifier and text_identifier.startswith('urn:cts:greekLit:'):
        # Direct URN provided
        text_urn = text_identifier
        selected_text = None
    else:
        # Search for text
        click.echo(f"Searching for '{text_identifier}'...")
        matches = searcher.search_texts(text_identifier)
        
        if not matches:
            click.echo(f"No texts found matching '{text_identifier}'", err=True)
            click.echo("\nTry --list-texts to see all available texts", err=True)
            raise click.Abort()
        
        if len(matches) == 1:
            selected_text = matches[0]
            text_urn = selected_text['urn']
            click.echo(f"Found: {selected_text['title']} by {selected_text['author']}")
        else:
            # Multiple matches - let user choose
            click.echo(f"\nFound {len(matches)} matches:")
            for i, match in enumerate(matches, 1):
                click.echo(f"{i}. {match['title']} by {match['author']}")
            
            if search_only:
                return
            
            # Get user choice
            while True:
                try:
                    choice = click.prompt('\nSelect a text (number)', type=int)
                    if 1 <= choice <= len(matches):
                        selected_text = matches[choice - 1]
                        text_urn = selected_text['urn']
                        break
                    else:
                        click.echo("Invalid choice. Please enter a number from the list.")
                except:
                    click.echo("Invalid input. Please enter a number.")
    
    if search_only:
        return
    if not output:
        # Generate output filename from URN or selected text
        if selected_text:
            # Clean filename
            safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', selected_text['title'])
            safe_author = re.sub(r'[^a-zA-Z0-9_-]', '_', selected_text['author'])
            output = f"{safe_author}_{safe_title}.apkg"
        else:
            safe_name = text_urn.replace(':', '_').replace('.', '_')
            output = f"{safe_name}.apkg"
    
    if not deck_name:
        # Generate deck name
        if selected_text:
            deck_name = f"{selected_text['title']} - {selected_text['author']}"
        else:
            parts = text_urn.split(':')
            if len(parts) >= 4:
                deck_name = f"Greek Vocabulary - {parts[3]}"
            else:
                deck_name = f"Greek Vocabulary - {text_urn}"
    
    click.echo(f"Scraping vocabulary for {text_urn}...")
    
    try:
        scraper = PerseusVocabScraper()
        vocab_items = scraper.scrape_vocabulary_list(text_urn)
        
        click.echo(f"Found {len(vocab_items)} vocabulary items")
        
        # Create Anki deck
        deck_creator = AnkiDeckCreator(deck_name)
        deck_creator.add_vocabulary_items(vocab_items)
        deck_creator.save_deck(output)
        
        click.echo(f"Successfully created Anki deck: {output}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()