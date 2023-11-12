import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from whoosh.index import create_in, exists_in, open_dir
from whoosh.fields import *
from urllib.parse import urlparse
import os
import datetime


link = "https://vm009.rz.uos.de/crawl/index.html"
idxdir = 'indexdir'

def crawler(url, index_dir, check_ext_links = False):

    #create index directory if it doesn't exist
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)

    #create index if it doesn't exist and open it otherwise
    if exists_in(index_dir):
        ix = open_dir(index_dir,)
    else:
        #create index with unique urls to avoid duplicates
        schema = Schema(link = ID(stored=True, unique=True) ,title=TEXT(stored=True), content=TEXT, last_updated=TEXT(stored=True))
        ix = create_in(index_dir, schema)

    writer = ix.writer()

    base_url = urlparse(url).netloc
    checked_links=[]
    links_queue=[url]
    
    while links_queue:
        link = links_queue.pop(0)
        if link not in checked_links:
            response = requests.get(link, timeout=5)
            if (not response.ok) or ('html' not in response.headers["Content-Type"]):
                continue

            soup = BeautifulSoup(response.content, 'html.parser')

            web_links_tags = soup.select('a') 
            web_links = [urljoin(link, tag['href']) for tag in web_links_tags]

            if not check_ext_links:
                web_links = [i for i in web_links if base_url in i]

            links_queue.extend(web_links)

            checked_links.append(link)
            writer.update_document(link=link, title=soup.head.title.text, content=soup.body.text, last_updated = str(datetime.datetime.now()))

    writer.commit()

crawler(link, idxdir)