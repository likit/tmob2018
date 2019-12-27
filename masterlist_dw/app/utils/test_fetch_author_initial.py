import pytest
from . scopus_author_search import fetch_author_initial


def test_no_lastname_input():
    with pytest.raises(ValueError):
        next(fetch_author_initial('Likit', ''))

def test_no_firstname_input():
    with pytest.raises(ValueError):
        next(fetch_author_initial('', 'Preeyanon'))


def test_no_firstname_lastname_input():
    with pytest.raises(ValueError):
        next(fetch_author_initial('', ''))


def test_get_author_no_variants():
    assert len(list(fetch_author_initial('Likit', 'Preeyanon'))) == 1


def test_get_author_with_variants():
    assert len(list(fetch_author_initial('Virapong', 'Prachayasittikul'))) == 2
