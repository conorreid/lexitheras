# Lexitheras

A tool to convert Perseus Greek vocabulary lists into Anki flashcard decks.

![Blind Orion Searching for the Rising Sun by Nicolas Poussin (1658)](docs/images/orion_poussin.jpg)
*Blind Orion Searching for the Rising Sun* by Nicolas Poussin (1658) - Metropolitan Museum of Art

## Features

- Search texts by title or author (e.g., "iliad", "homer", "symposium")
- Create Anki decks with Greek→English vocabulary cards
- Cache text catalog for faster searches
- Interactive selection when multiple matches found
- Cards ordered by frequency of appearance

## Installation

### From Source

```bash
git clone git@github.com:conorreid/lexitheras.git
cd lexitheras
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Using pip

```bash
pip install lexitheras
```

## Usage

### Search by title or author
```bash
lexitheras iliad        # Find and create deck for the Iliad
lexitheras symposium    # Choose between Plato's or Xenophon's
lexitheras homer        # See all texts by Homer
```

### List all available texts
```bash
lexitheras --list-texts
```

### Search without creating deck
```bash
lexitheras plato --search-only
```

### Direct URN (if known)
```bash
lexitheras urn:cts:greekLit:tlg0012.tlg001.perseus-grc2
```

### Limit vocabulary items
```bash
lexitheras iliad --limit 100  # Only first 100 most frequent words
```

## Card Format

- **Front**: Greek word (with frequency rank)
- **Back**: English translation and lemma form

## Requirements

- Python 3.6+
- Internet connection to access Perseus

## License

GNU General Public License v3.0