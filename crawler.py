import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from whoosh.index import create_in, exists_in, open_dir
from whoosh.fields import *
from whoosh.analysis import StemmingAnalyzer
from urllib.parse import urlparse
import os
import datetime
from database import *


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
        schema = Schema(id = NUMERIC(int, stored=True, unique=True), content=TEXT(analyzer=StemmingAnalyzer()))
        ix = create_in(index_dir, schema)

    #create database connection
    connection = create_connection("database.sqlite")

    #create a table for websites data if it doesn't exist
    create_table(connection, "sites", ("title", "link", "last_updated", "content"), ("TEXT", "TEXT", "INTEGER", "TEXT"), True)

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

            cursor = add_to_table(
                connection, 'sites', 
                [str(soup.head.title.text), str(link), int(datetime.datetime.now().timestamp()), str(soup.body.text)],
                1, 'link')
            site_id = cursor.lastrowid

            writer.update_document(id=site_id, content=soup.body.text)

    writer.commit()

crawler(link, idxdir)