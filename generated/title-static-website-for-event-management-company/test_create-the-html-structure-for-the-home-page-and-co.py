import pytest

def test_home_page_elements():
    html = open('create-the-html-structure-for-the-home-page-and-co.html', encoding='utf-8').read()
    assert html, "The HTML file is empty."
    html_lower = html.lower()
    assert 'event management company' in html_lower
    assert 'event title 1' in html_lower
    assert 'event title 2' in html_lower
    assert 'event title 3' in html_lower

def test_contact_page_elements():
    html = open('create-the-html-structure-for-the-home-page-and-co.html', encoding='utf-8').read()
    assert html, "The HTML file is empty."
    html_lower = html.lower()
    assert 'contact us' in html_lower
    assert 'name' in html_lower
    assert 'email' in html_lower
    assert 'message' in html_lower
    assert 'submit' in html_lower