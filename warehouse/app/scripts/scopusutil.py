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


@click.group()
# These db variables should be able to get from the environment.
@click.option('--dbname', required=True)
@click.option('--dbhost', required=True)
@click.option('--dbport', default=5432, type=int, show_default=True)
@click.option('--dbtable', default='pubs', show_default=True)
@click.option('--dbuser', required=True)
@click.option('--dbpass', default='', show_default=True)
@click.pass_context
def load(ctx, dbname, dbhost, dbuser, dbtable, dbpass, dbport):
    click.echo(dbport)
    ctx.ensure_object(dict)
    click.echo('Initializing..')
    meta, pub_engine, pub_table, pub_con = \
            _init(dbname, dbhost, dbuser, dbtable, dbpass, dbport)
    ctx.obj['meta'] = meta
    ctx.obj['pub_engine'] = pub_engine
    ctx.obj['pub_table'] = pub_table
    ctx.obj['pub_con'] = pub_con


@load.command()
@click.option('-k', '--keyword',
                help='search keyword or term',
                required=True,
                multiple=True)
@click.option('-y', '--year',
                help='published year',
                default=CURRENT_YEAR, show_default=True)
@click.option('--doctype', type=click.Choice(
                            ['ar', 'ab', 'ip', 'bk', 'bz',
                            'ch', 'cp', 'cr', 'ed', 'er',
                            'le', 'no', 'pr', 're', 'sh'
                            ]),
                            help='article types', default='ar')
@click.option('--item-per-page', default=25, type=int)
@click.option('--sleep-time', default=10, type=int)
@click.option('--dry', is_flag=True)
@click.option('--scopus-api-key', envvar='SCOPUS_API_KEY', required=True)
@click.pass_context
def by_keyword(ctx, keyword, year, scopus_api_key,
               item_per_page, sleep_time, doctype, dry):
    query = 'TITLE-ABS-KEY({}) PUBYEAR = {} AFFILCOUNTRY(thailand) DOCTYPE({})'.format(keyword, year, doctype)
    params = {'apiKey': scopus_api_key, 'query': query, 'httpAccept': 'application/json', 'view': 'COMPLETE'}
    url = 'http://api.elsevier.com/content/search/scopus'
    print(query)
    pub_table = ctx.obj['pub_table']
    pub_con = ctx.obj['pub_con']
    r = requests.get(url, params).json()

    print('Total articles = {}'.format(r.get('search-results').get('opensearch:totalResults')))

    stats = {'keyword': keyword, 'year': year, 'authors': []}
    stats['articles'] = r.get('search-results').get('entry')

    for article in r.get('search-results').get('entry'):
        identifier = article.get('dc:identifier', None)
        if identifier:
            scopus_id = identifier.split(':')[1]
        else:
            continue

        params = {'apiKey': scopus_api_key, 'query': query, 'httpAccept': 'application/json',
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
                if dry:
                    print(str(u))
                else:
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
                if dry:
                    print(str(ins))
                else:
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
    params = {'apiKey': scopus_api_key, 'query': query, 'httpAccept': 'application/json', 'view': 'COMPLETE'}
    search_url = 'http://api.elsevier.com/content/search/scopus'
    r = requests.get(search_url, params).json()

    total_articles = r.get('search-results', {}).get('opensearch:totalResults', 0)
    print('Total articles = {}'.format(total_articles))

    for start in range(75, 200, item_per_page):
        search_params = {'apiKey': scopus_api_key,
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

            params = {'apiKey': scopus_api_key, 'query': query, 'httpAccept': 'application/json',
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



def _init(dbname, host, user, table='pubs', password=None, port=5432):
    meta = MetaData()
    if password:
        cred = '{}:{}'.format(user, password)
    else:
        cred = user

    pub_engine = create_engine(
        'postgresql+psycopg2://{}@{}:{}/{}'.format(cred, host, port, dbname))

    pub_con = pub_engine.connect()
    pub_table = Table(table, meta, autoload=True, autoload_with=pub_engine)
    return meta, pub_engine, pub_table, pub_con


if __name__ == '__main__':
    load(obj={})
