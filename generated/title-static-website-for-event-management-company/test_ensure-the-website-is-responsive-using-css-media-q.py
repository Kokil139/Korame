import pytest

def test_home_page_content():
    html = open('ensure-the-website-is-responsive-using-css-media-q.html', encoding='utf-8').read()
    assert html, "The HTML file is empty."
    html_lower = html.lower()
    assert 'event management company' in html_lower
    assert 'home' in html_lower
    assert 'contact' in html_lower
    assert 'event 1' in html_lower
    assert 'event 2' in html_lower
    assert 'event 3' in html_lower

def test_contact_page_form_fields():
    html = open('ensure-the-website-is-responsive-using-css-media-q.html', encoding='utf-8').read()
    assert html, "The HTML file is empty."
    html_lower = html.lower()
    assert 'name' in html_lower
    assert 'email' in html_lower
    assert 'message' in html_lower
    assert 'submit' in html_lower