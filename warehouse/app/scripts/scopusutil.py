''' Retrieve publications from Scopus APIs and add them to the database.

'''

import os
import sys
import requests
import json
import time
import click
from itertools import islice
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import insert, update, select

CURRENT_YEAR = datetime.today().year

meta = MetaData()
pub_engine = create_engine('postgresql+psycopg2://postgres@postgres_db/stagedb')

pub_con = pub_engine.connect()
pub_table = Table('pubs', meta, autoload=True, autoload_with=pub_engine)


@click.group()
def load():
    pass


@click.command()
@click.option('-k', '--keyword',
                help='search keyword or term',
                required=True)
@click.option('-y', '--year',
                help='published year',
                default=CURRENT_YEAR, show_default=True)
@click.option('--doctype', type=click.Choice(
                            ['ar', 'ab', 'ip', 'bk', 'bz',
                            'ch', 'cp', 'cr', 'ed', 'er',
                            'le', 'no', 'pr', 're', 'sh'
                            ]),
                            help='article types', default='ar')
@click.option('--scopus-api-key', envvar='SCOPUS_API_KEY')
@click.option('--item-per-page', default=25, type=int)
@click.option('--sleep-time', default=10, type=int)
def by_keyword(keyword, year, doctype='ar'):
    query = 'TITLE-ABS-KEY({}) PUBYEAR = {} AFFILCOUNTRY(thailand) DOCTYPE({})'.format(keyword, year, doctype)
    params = {'apiKey': SCOPUS_API_KEY, 'query': query, 'httpAccept': 'application/json', 'view': 'COMPLETE'}
    url = 'http://api.elsevier.com/content/search/scopus'
    r = requests.get(url, params).json()

    print('Total articles = {}'.format(r.get('search-results').get('opensearch:totalResults')))

    stats['keyword'] = keyword
    stats['year'] = year
    stats['articles'] = r.get('search-results').get('entry')
    stats['authors'] = []

    for article in r.get('search-results').get('entry'):
        identifier = article.get('dc:identifier', None)
        if identifier:
            scopus_id = identifier.split(':')[1]
        else:
            continue

        params = {'apiKey': SCOPUS_API_KEY, 'query': query, 'httpAccept': 'application/json',
                  'view': 'FULL'}
        url = 'http://api.elsevier.com/content/abstract/scopus_id/' + scopus_id
        print('Downloading from {}'.format(url))
        result = requests.get(url, params=params).json()
        abstract_resp = result.get('abstracts-retrieval-response')
        if abstract_resp:
            citation_count = abstract_resp.get('coredata').get('citedby-count', 0)
            pub_date = abstract_resp.get('coredata').get('prism:coverDate')
            pub_date = datetime.strptime(pub_date, '%Y-%m-%d')

            s = select([pub_table]).where(pub_table.c.scopus_id == scopus_id)
            _pub = pub_con.execute(s).first()
            if _pub:
                print('\tAlready loaded. Updating citation count..'.format(scopus_id))
                u = update(pub_table).where(pub_table.c.scopus_id == scopus_id)
                u = u.values(cited_count=int(citation_count))
                _res = pub_con.execute(u)
                continue  # pub already loaded, move on!
            else:
                ins = insert(pub_table).values(
                    scopus_id=scopus_id,
                    cited_count=int(citation_count),
                    pub_date=pub_date,
                    data=result,
                    doctype=doctype
                )
                pub_con.execute(ins)


@click.command()
@click.option('-y', '--year',
                help='published year',
                default=CURRENT_YEAR, show_default=True)
@click.option('--doctype', type=click.Choice(
                            ['ar', 'ab', 'ip', 'bk', 'bz',
                            'ch', 'cp', 'cr', 'ed', 'er',
                            'le', 'no', 'pr', 're', 'sh'
                            ]),
                            help='article types', default='ar')
@click.option('--scopus-api-key', envvar='SCOPUS_API_KEY')
@click.option('--item-per-page', default=25, type=int)
@click.option('--sleep-time', default=10, type=int)
def by_year(year, doctype='ar'):
    query = 'PUBYEAR = {} AFFILCOUNTRY(thailand) DOCTYPE({})'.format(year, doctype)
    params = {'apiKey': SCOPUS_API_KEY, 'query': query, 'httpAccept': 'application/json', 'view': 'COMPLETE'}
    search_url = 'http://api.elsevier.com/content/search/scopus'
    r = requests.get(search_url, params).json()

    total_articles = r.get('search-results', {}).get('opensearch:totalResults', 0)
    print('Total articles = {}'.format(total_articles))

    for start in range(75, 200, item_per_page):
        search_params = {'apiKey': SCOPUS_API_KEY,
                  'query': query,
                  'start': start,
                  'count': item_per_page,
                  'httpAccept': 'application/json',
                  'view': 'COMPLETE'}

        r = requests.get(search_url, search_params).json()
        print('Start={}'.format(start))

        try:
            articles = r.get('search-results').get('entry')
        except:
            print(r)
            raise SystemExit

        for article in articles:
            identifier = article.get('dc:identifier', None)
            if identifier:
                scopus_id = identifier.split(':')[1]
            else:
                continue

            params = {'apiKey': SCOPUS_API_KEY, 'query': query, 'httpAccept': 'application/json',
                      'view': 'FULL'}
            url = 'http://api.elsevier.com/content/abstract/scopus_id/' + scopus_id
            print('Downloading from {}'.format(url))
            result = requests.get(url, params=params).json()
            abstract_resp = result.get('abstracts-retrieval-response')
            if abstract_resp:
                citation_count = abstract_resp.get('coredata').get('citedby-count', 0)
                pub_date = abstract_resp.get('coredata').get('prism:coverDate')
                pub_date = datetime.strptime(pub_date, '%Y-%m-%d')

                s = select([pub_table]).where(pub_table.c.scopus_id == scopus_id)
                _pub = pub_con.execute(s).first()
                if _pub:
                    print('\tAlready loaded; do nothing..'.format(scopus_id))
                    '''
                    u = update(pub_table).where(pub_table.c.scopus_id == scopus_id)
                    u = u.values(cited_count=int(citation_count))
                    _res = pub_con.execute(u)
                    '''
                    continue  # pub already loaded, move on!
                else:
                    ins = insert(pub_table).values(
                        scopus_id=scopus_id,
                        cited_count=int(citation_count),
                        pub_date=pub_date,
                        data=result,
                        doctype=doctype
                    )
                    pub_con.execute(ins)
        print('Sleeping...')
        time.sleep(sleep_time)


load.add_command(by_keyword)
load.add_command(by_year)


if __name__ == '__main__':
    load()
