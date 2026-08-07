import pytest

def test_contact_page_elements():
    html = open('style-the-contact-page-using-css-to-include-a-form.html', encoding='utf-8').read()
    assert len(html) > 0, "HTML file is empty"
    
    html_lower = html.lower()
    assert 'contact us' in html_lower
    assert 'name' in html_lower
    assert 'email' in html_lower
    assert 'message' in html_lower
    assert 'submit' in html_lower