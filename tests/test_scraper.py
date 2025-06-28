"""
Basic tests for the scraper
"""

import pytest
from lexitheras.scraper import PerseusVocabScraper


def test_scraper_initialization():
    """Test that scraper initializes correctly"""
    scraper = PerseusVocabScraper()
    assert scraper.base_url == "https://vocab.perseus.org"
    assert scraper.session is not None


def test_scraper_headers():
    """Test that scraper sets proper headers"""
    scraper = PerseusVocabScraper()
    assert 'User-Agent' in scraper.session.headers


@pytest.mark.skip(reason="Requires network access")
def test_scrape_small_text():
    """Test scraping a small text (requires internet)"""
    scraper = PerseusVocabScraper()
    # This would test actual scraping
    # vocab_items = scraper.scrape_vocabulary_list('urn:cts:greekLit:tlg0059.tlg011.perseus-grc2', get_all_pages=False)
    # assert len(vocab_items) > 0
    # assert 'word' in vocab_items[0]
    # assert 'translation' in vocab_items[0]