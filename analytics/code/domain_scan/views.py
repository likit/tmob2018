from . import domain
from flask import render_template, jsonify, request
from sqlalchemy import Table, select
from app import conn, engine, metadata, kwengine, kwmetadata, kwconn
from collections import defaultdict, Counter

@domain.route('/')
def index():
    return render_template('domain/index.html')


@domain.route('/api/v1.0/pub-per-year')
def get_pub_per_year(ntop=20, nyears=15):
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

    pub_per_years = {'data': [], 'labels': []}
    for year in years[-nyears:]:
        item = {'label': year, 'data': []}
        for af,_ in top_affil_items:
             item['data'].append(Counter(all_affiliations[year]).get(af, 0))
        pub_per_years['data'].append(item)
    
    for af,_ in top_affil_items:
        pub_per_years['labels'].append(af)

    return jsonify(pub_per_years)


@domain.route('/api/v1.0/total-pub-per-year')
def get_total_pub_per_year(ntop=20, nyears=15):
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


@domain.route('/api/v1.0/author-per-year')
def get_author_per_year(ntop=20, nyears=15):
    PubTable = Table('pubs', metadata, autoload=True, autoload_with=engine)
    s = select([PubTable])
    rp = conn.execute(s)
    author_affiliation_years = defaultdict(dict)
    affiliation_dict = {}
    affiliation_pubs = defaultdict(int)
    for rec in rp.fetchall():
        thai_affs = set()
        affil_data = rec.data['abstracts-retrieval-response'].get('affiliation', [])
        
        if isinstance(affil_data, dict):
            if affil_data['affiliation-country'] == 'Thailand':
                thai_affs.add(affil_data['@id'])
                affiliation_dict[affil_data['@id']] = affil_data['affilname']
                affiliation_pubs[affil_data['@id']] += 1
        elif isinstance(affil_data, list):
            for affil in affil_data:
                if affil['affiliation-country'] == 'Thailand':
                    thai_affs.add(affil['@id'])
                    affiliation_dict[affil['@id']] = affil['affilname']
                    affiliation_pubs[affil['@id']] += 1

        authors = rec.data['abstracts-retrieval-response']['authors']['author']
        year = rec.pub_date.year
        if year not in author_affiliation_years:
            author_affiliation_years[year] = defaultdict(dict)
        if isinstance(authors, list):
            for author in authors:
                if 'affiliation' in author:
                    if isinstance(author['affiliation'], list):  # multiple affiliations
                        for affil in author['affiliation']:
                            if affil['@id'] in thai_affs:
                                if affil['@id'] in author_affiliation_years[year]:
                                    author_affiliation_years[year][affil['@id']].add(author['ce:indexed-name'])
                                else:
                                    author_affiliation_years[year][affil['@id']] = set([author['ce:indexed-name']])
                    elif author['affiliation']['@id'] in thai_affs:
                        if author['affiliation']['@id'] in author_affiliation_years[year]:
                            author_affiliation_years[year][author['affiliation']['@id']].add(author['ce:indexed-name'])
                        else:
                            author_affiliation_years[year][author['affiliation']['@id']] = set([author['ce:indexed-name']])

    top_universities = [x[0] for x in sorted(affiliation_pubs.items(),
                            key=lambda x: x[1], reverse=True)[:ntop]]
    sorted_years = sorted(author_affiliation_years.keys(), reverse=False)[-nyears:]
    plot_data = {'data': [], 'labels': sorted_years}

    for af in top_universities:
        item = {'label': affiliation_dict[af], 'data': []}
        for year in sorted_years:
            item['data'].append(len(author_affiliation_years[year][af]))
        plot_data['data'].append(item)

    return jsonify(plot_data)


@domain.route('/api/v1.0/percent-pub')
def get_percent_pub(ntop=20, nyears=15):
    PubTable = Table('pubs', metadata, autoload=True, autoload_with=engine)
    s = select([PubTable])
    rp = conn.execute(s)
    affiliation_dict = {}
    affil_pubs = defaultdict(int)
    for rec in rp.fetchall():
        affil_data = rec.data['abstracts-retrieval-response'].get('affiliation', [])
        
        if isinstance(affil_data, dict):
            if affil_data['affiliation-country'] == 'Thailand':
                affilname = affil_data.get('affilname', '')
                if affilname:
                    affil_pubs[affilname] += 1
        elif isinstance(affil_data, list):
            for affil in affil_data:
                if affil['affiliation-country'] == 'Thailand':
                    affilname = affil.get('affilname','')
                    if affilname:
                        affil_pubs[affilname] += 1
    top_universities = sorted(affil_pubs.items(), key=lambda x: x[1], reverse=True)[:ntop]
    other_universities = sorted(affil_pubs.items(), key=lambda x: x[1], reverse=True)[ntop:]
    plot_data = {'data': [], 'labels': []}

    for item in top_universities:
        af, num = item
        plot_data['data'].append(affil_pubs[af])
        plot_data['labels'].append(af)
    other_num = sum([num for af, num in other_universities])
    plot_data['data'].append(other_num)
    plot_data['labels'].append('others')

    return jsonify(plot_data)


@domain.route('/api/v1.0/num-scholarship')
def get_num_scholarship_studs(ntop=20, nyears=20):
    PubTable = Table('scholarship_info', kwmetadata, autoload=True, autoload_with=kwengine)
    s = select([PubTable.c.first_name_en, PubTable.c.last_name_en])
    scholars = set()
    for rec in kwconn.execute(s):
        firstname, lastname = rec
        firstname = firstname.lower()\
                        .replace('mrs.', '')\
                        .replace('mr.', '')\
                        .replace('ms.', '')\
                        .replace('dr.','')
        if firstname and lastname:
            scholars.add('{}.'.format(' '.join([lastname.lower(), firstname.lower()[0]])))

    PubTable = Table('pubs', metadata, autoload=True, autoload_with=engine)
    s = select([PubTable])
    year_scholar_authors = defaultdict(set)
    for rec in conn.execute(s):
        year = rec.pub_date.year
        authors = rec.data['abstracts-retrieval-response']['authors']['author']
        if isinstance(authors, list):
            for author in authors:
                idxname = author['ce:indexed-name'].lower()
                if idxname in scholars:
                    year_scholar_authors[year].add(idxname)
        else:
            idxname = authors['ce:indexed-name'].lower()
            if idxname in scholars:
                year_scholar_authors[year].add(idxname)

    sorted_years = sorted(year_scholar_authors, reverse=False)[:nyears]
    all_scholar_authors = set()
    old_scholars = defaultdict(set)
    new_scholars = defaultdict(set)
    for yr in sorted_years:
        old_scholars[yr] = year_scholar_authors[yr].intersection(all_scholar_authors)
        new_scholars[yr] = year_scholar_authors[yr].difference(all_scholar_authors)
        all_scholar_authors.update(year_scholar_authors[yr])

    plot_data = {'data': [], 'labels': sorted_years}
    oldss = []
    newss = []
    for yr in sorted_years:
        oldss.append(len(old_scholars[yr]))
        newss.append(len(new_scholars[yr]))

    plot_data['data'].append({
        'data': oldss,
        'label': 'Scholars'
    })
    plot_data['data'].append({
        'data': newss,
        'label': 'New Scholars'
    })

    return jsonify(plot_data)
