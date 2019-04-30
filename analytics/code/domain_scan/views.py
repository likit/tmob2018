from . import domain
from flask import render_template, jsonify, request
from sqlalchemy import Table, select
from app import conn, engine, metadata
from collections import defaultdict, Counter

@domain.route('/')
def index():
    return render_template('domain/index.html')


@domain.route('/api/v1.0/pub-per-year')
def get_pub_per_year(ntop=25, nyears=15):
    PubTable = Table('pubs', metadata, autoload=True, autoload_with=engine)
    s = select([PubTable])
    doctype = request.args.get('doctype', None)
    if doctype:
        s = s.where(PubTable.c.doctype==doctype)
    all_affiliations = defaultdict(list)
    for rec in conn.execute(s):
        affil_set = set()
        affil_data = rec.data['abstracts-retrieval-response'].get('affiliation', [])
        if isinstance(affil_data, list):
            for af in affil_data:
                if af['affiliation-country'] == 'Thailand':
                    affil_set.add(af['affilname'])
            all_affiliations[rec.pub_date.year] += list(affil_set)
        elif isinstance(affil_data, dict):
            if affil_data['affiliation-country'] == 'Thailand':
                all_affiliations[rec.pub_date.year].append(affil_data['affilname'])

    total_pub_per_affils = defaultdict(int)
    years = sorted(all_affiliations.keys())
    for year in years[-nyears:]:
        for af, pubs in Counter(all_affiliations[year]).items():
            total_pub_per_affils[af] += pubs

    top_affil_items = sorted(
        total_pub_per_affils.items(), key=lambda x: x[1], reverse=True)[:ntop]

    years = sorted(all_affiliations.keys())
    pub_per_years = {'data': [], 'labels': []}
    for year in years[-nyears:]:
        item = {'label': year, 'data': []}
        for af,_ in top_affil_items:
             item['data'].append(Counter(all_affiliations[year]).get(af, 0))
        pub_per_years['data'].append(item)
    
    for af,_ in top_affil_items:
        pub_per_years['labels'].append(af)
    print(pub_per_years)

    return jsonify(pub_per_years)


@domain.route('/api/v1.0/total-pub-per-year')
def get_total_pub_per_year(ntop=25, nyears=20):
    PubTable = Table('pubs', metadata, autoload=True, autoload_with=engine)
    s = select([PubTable])
    doctype = request.args.get('doctype', None)
    if doctype:
        s = s.where(PubTable.c.doctype==doctype)
    pubs = defaultdict(int)
    for rec in conn.execute(s):
        year = rec.pub_date.year
        pubs[year] += 1

    data = {'data': [], 'labels': []}
    for y in sorted(pubs.keys())[-nyears:]:
        data['data'].append(pubs[y])
        data['labels'].append(str(y))

    return jsonify(data)