"""
Command-line interface for Lexitheras
"""

import click
import re
from .search import PerseusTextSearcher
from .scraper import PerseusVocabScraper
from .deck import AnkiDeckCreator


@click.command()
@click.argument('text_identifier')
@click.option('--output', '-o', default=None, help='Output filename for Anki deck')
@click.option('--deck-name', '-n', default=None, help='Name for the Anki deck')
@click.option('--list-texts', '-l', is_flag=True, help='List all available texts')
@click.option('--search-only', '-s', is_flag=True, help='Only search, don\'t create deck')
@click.option('--limit', default=0, help='Limit number of vocabulary items (0 = no limit)')
def main(text_identifier, output, deck_name, list_texts, search_only, limit):
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
        
        # Apply limit if specified
        if limit > 0 and len(vocab_items) > limit:
            vocab_items = vocab_items[:limit]
            click.echo(f"Limited to {limit} items")
        
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