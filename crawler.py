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
import config


def crawler(url, index_dir, check_ext_links, count):

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
    connection = create_connection(config.database_file)

    #create a table for websites data if it doesn't exist
    create_table(connection, "sites", ("title", "link", "last_updated", "content"), ("TEXT", "TEXT", "INTEGER", "TEXT"), True)
    create_table(connection, "sitelinks", ("link", "refs"), ("TEXT", "TEXT"), True)

    writer = ix.writer()


    base_url = config.base_url
    checked_links=[]
    links_queue=[url]
    refs_to_page = {}
    
    i = 0
    while links_queue and i < count:
        i += 1
        link = links_queue.pop(0)
        if link not in checked_links:
            response = requests.get(link, timeout=5)
            if (not response.ok) or ('html' not in response.headers["Content-Type"]):
                continue

            soup = BeautifulSoup(response.content, 'html.parser')

            web_links_tags = soup.select('a') 
            web_links = [tag.attrs['href'] for tag in web_links_tags if 'href' in tag.attrs]
            web_links = [urljoin(link, href) for href in web_links if '#' not in href]

            if not check_ext_links:
                web_links = [l for l in web_links if base_url in l]

            links_queue.extend(web_links)

            checked_links.append(link)

            cursor = add_to_table(
                connection, 'sites', 
                [str(soup.head.title.text), str(link), int(datetime.datetime.now().timestamp()), str(soup.body.text)],
                1, 'link')
            site_id = cursor.lastrowid

            for l in web_links:
                if check_ext_links and (urlparse(l).netloc == urlparse(link).netloc):
                    continue
                if l in refs_to_page:
                    refs_to_page[l] += f',{site_id}'
                else: 
                    refs_to_page[l] = str(site_id)

            writer.update_document(id=site_id, content=soup.body.text)
            print(f"{link} added to database")

    for link in refs_to_page:
        refs = ','.join(list(set(refs_to_page[link].split(','))))
        query = f"SELECT refs FROM sitelinks where link = '{link}'"
        prev_refs = execute_read_query(connection, query)
        if prev_refs:
            refs = ','.join(list(set(refs.split(',') + prev_refs[0][0].split(','))))
        add_to_table(connection, 'sitelinks', [str(link), str(refs)], 0, 'link')
    writer.commit()

crawler(config.link, config.idxdir, config.check_ext_links, config.count)