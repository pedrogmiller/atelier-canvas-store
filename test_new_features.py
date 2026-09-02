from fastapi.testclient import TestClient
from storefront.app import app

client = TestClient(app)

def test_all():
    # 1. Home page
    home = client.get('/')
    print('1. Home page status:', home.status_code)
    assert home.status_code == 200
    assert '/static/images/logo_emblem.png' in home.text
    assert '/static/favicon.png' in home.text

    # 2. Static logo emblem
    logo = client.get('/static/images/logo_emblem.png')
    print('2. Logo emblem status:', logo.status_code, 'Bytes:', len(logo.content))
    assert logo.status_code == 200
    assert len(logo.content) > 1000

    # 3. Favicon
    fav = client.get('/static/favicon.png')
    print('3. Favicon status:', fav.status_code, 'Bytes:', len(fav.content))
    assert fav.status_code == 200
    assert len(fav.content) > 1000

    # 4. Sitemap
    sitemap = client.get('/sitemap.xml')
    url_count = sitemap.text.count('<url>')
    print(f'4. Sitemap status: {sitemap.status_code}, URLs: {url_count}')
    assert sitemap.status_code == 200
    assert url_count == 53

    # 5. Robots.txt
    robots = client.get('/robots.txt')
    print('5. Robots.txt status:', robots.status_code)
    assert robots.status_code == 200
    assert 'Sitemap: https://www.oakprintstudio.com/sitemap.xml' in robots.text

    # 6. Product Detail with JSON-LD
    prod = client.get('/product/amalfi-lemon-groves-terracotta-heirloom-amalfi-lemon-branch-with-leaves-no-5-3927d3')
    print('6. Product detail status:', prod.status_code)
    assert prod.status_code == 200
    assert '"@type": "Product"' in prod.text
    assert 'OAK PRINT STUDIO' in prod.text

    print('\nSUCCESS: ALL VERIFICATION TESTS PASSED 100%!')

if __name__ == '__main__':
    test_all()
