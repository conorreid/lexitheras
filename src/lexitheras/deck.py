"""
Anki deck creation functionality
"""

import genanki
import random


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
                {'name': 'Rank'},
                {'name': 'Count'}
            ],
            templates=[
                {
                    'name': 'Greek to English',
                    'qfmt': '<div style="font-size: 32px;">{{Greek}}</div>',
                    'afmt': '''{{FrontSide}}<hr id="answer">
<div style="font-size: 24px; margin: 20px 0;">{{Translation}}</div>
<div style="font-size: 14px; color: #666; margin-top: 20px;">
Rank: {{Rank}} | Occurrences: {{Count}}
</div>''',
                }
            ],
            css='''
            .card {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 20px;
                text-align: center;
                color: black;
                background-color: white;
                padding: 20px;
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
                    str(item['rank']),
                    str(item.get('count', 0))
                ]
            )
            self.deck.add_note(note)
    
    def save_deck(self, filename):
        """Save the deck to a .apkg file"""
        genanki.Package(self.deck).write_to_file(filename)