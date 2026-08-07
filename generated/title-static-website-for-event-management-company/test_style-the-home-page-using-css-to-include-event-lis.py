import pytest

def test_home_page_content():
    html = open('style-the-home-page-using-css-to-include-event-lis.html', encoding='utf-8').read()
    assert html, "The HTML file is empty"
    
    html_lower = html.lower()
    assert 'upcoming events' in html_lower
    assert 'event title 1' in html_lower
    assert 'date: january 1, 2024' in html_lower
    assert 'description: this is the description for event title 1.' in html_lower
    assert 'event title 2' in html_lower
    assert 'date: february 15, 2024' in html_lower
    assert 'description: this is the description for event title 2.' in html_lower
    assert 'event title 3' in html_lower
    assert 'date: march 20, 2024' in html_lower
    assert 'description: this is the description for event title 3.' in html_lower

if __name__ == "__main__":
    pytest.main()