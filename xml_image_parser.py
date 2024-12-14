from os import makedirs, path, getcwd
from bs4 import BeautifulSoup as bs
from requests import get

f = open('8o039clockranch.WordPress.2024-12-11.xml', 'r')

contents = f.read()
soup = bs(contents, 'xml')

guids = soup.find_all('guid')

image_urls = []
makedirs('images', exist_ok=True)

for guid in guids:
    url = guid.get_text()
    image_urls.append(url)

for url in image_urls:
    filename = path.join(getcwd(), "images", url.split('/')[-1])
    response = get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
            print("Downloaded %s" % filename)
    else:
        print("Failed to download %s" % url)

f.close()

