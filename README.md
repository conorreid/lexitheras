# Lexitheras

A tool to convert Perseus Greek vocabulary lists into Anki flashcard decks.

## Features

- Search texts by title or author (e.g., "iliad", "homer", "symposium")
- Create Anki decks with Greek→English vocabulary cards
- Cache text catalog for faster searches
- Interactive selection when multiple matches found
- Cards ordered by frequency of appearance

## Installation

```bash
git clone git@github.com:conorreid/lexitheras.git
cd lexitheras
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Search by title or author
```bash
python lexitheras.py iliad        # Find and create deck for the Iliad
python lexitheras.py symposium    # Choose between Plato's or Xenophon's
python lexitheras.py homer        # See all texts by Homer
```

### List all available texts
```bash
python lexitheras.py --list-texts
```

### Search without creating deck
```bash
python lexitheras.py plato --search-only
```

### Direct URN (if known)
```bash
python lexitheras.py urn:cts:greekLit:tlg0012.tlg001.perseus-grc2
```

## Card Format

- **Front**: Greek word (with frequency rank)
- **Back**: English translation and lemma form

## Requirements

- Python 3.6+
- Internet connection to access Perseus

## License

GNU General Public License v3.0