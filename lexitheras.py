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
@click.argument('text_urn')
@click.option('--output', '-o', default=None, help='Output filename for Anki deck')
@click.option('--deck-name', '-n', default=None, help='Name for the Anki deck')
def main(text_urn, output, deck_name):
    """
    Create an Anki deck from a Perseus vocabulary list.
    
    TEXT_URN: The URN identifier for the text (e.g., urn:cts:greekLit:tlg0012.tlg001.perseus-grc2)
    """
    if not output:
        # Generate output filename from URN
        safe_name = text_urn.replace(':', '_').replace('.', '_')
        output = f"{safe_name}.apkg"
    
    if not deck_name:
        # Try to extract a readable name from the URN
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