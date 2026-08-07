import pytest

def test_home_page_content():
    with open('apply-a-consistent-navy-blue-00008b-and-black-0000.html', encoding='utf-8') as file:
        html = file.read()
    
    assert html, "The HTML file is empty."
    html_lower = html.lower()
    assert 'upcoming events' in html_lower
    assert 'event title 1' in html_lower
    assert 'event title 2' in html_lower
    assert 'event title 3' in html_lower

def test_contact_page_content():
    with open('apply-a-consistent-navy-blue-00008b-and-black-0000.html', encoding='utf-8') as file:
        html = file.read()
    
    assert html, "The HTML file is empty."
    html_lower = html.lower()
    assert 'contact us' in html_lower
    assert 'name:' in html_lower
    assert 'email:' in html_lower
    assert 'message:' in html_lower
    assert 'submit' in html_lower