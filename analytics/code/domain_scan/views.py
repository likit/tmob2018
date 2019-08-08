from . import domain
from io import BytesIO
from pandas import read_excel, isna
from flask import render_template, jsonify, request, url_for, send_file
from sqlalchemy import Table, select, extract
from app import conn, engine, metadata, kwengine, kwmetadata, kwconn
from collections import defaultdict, Counter
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk import regexp_tokenize, word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfTransformer, TfidfVectorizer

stop_words = set(stopwords.words("english"))


@domain.route('/')
def index():
    return render_template('domain/index.html')


@domain.route('/collaboration')
def collab_view():
    return render_template('domain/collab.html')


@domain.route('/workforce')
def workforce_view():
    return render_template('domain/workforce.html')


@domain.route('/others')
def others_view():
    return render_template('domain/others.html')


@domain.route('/api/v1.0/pub-per-year')
def get_pub_per_year(ntop=20, begin_yr=2006, end_yr=2018):
    PubTable = Table('pubs', metadata, autoload=True, autoload_with=engine)
    s = select([PubTable]).where(extract('year', PubTable.c.pub_date)>=begin_yr)
    s = s.where(extract('year', PubTable.c.pub_date)<=end_yr)
    doctype = request.args.get('doctype', None)
    if doctype:
        s = s.where(PubTable.c.doctype == doctype)
    all_affiliations = defaultdict(list)
    for rec in conn.execute(s):
        affil_set = set()
        affil_data = rec.data['abstracts-retrieval-response'].get('affiliation', [])
        if isinstance(affil_data, list):
            for af in affil_data:
                if af['affiliation-country'] == 'Thailand':
                    affilname = af['affilname']
                    if 'Thammasat' in af['affilname']:
                        affilname = 'Thammasat Univeristy'
                    if 'University of Technology Thonburi' in af['affilname']:
                        affilname = "King Mongkut's University of Technology Thonburi"
                        affil_set.add(affilname)
            all_affiliations[rec.pub_date.year] += list(affil_set)
        elif isinstance(affil_data, dict):
            if affil_data['affiliation-country'] == 'Thailand':
                affilname = affil_data['affilname']
                if 'Thammasat' in affil_data['affilname']:
                    affilname = 'Thammasat Univeristy'
                if 'University of Technology Thonburi' in affil_data['affilname']:
                    affilname = "King Mongkut's University of Technology Thonburi"
                all_affiliations[rec.pub_date.year].append(affilname)

    total_pub_per_affils = defaultdict(int)
    years = sorted(all_affiliations.keys())
    for year in range(begin_yr, end_yr+1):
        for af, pubs in Counter(all_affiliations[year]).items():
            total_pub_per_affils[af] += pubs

    top_affil_items = sorted(
        total_pub_per_affils.items(), key=lambda x: x[1], reverse=True)[:ntop]

    pub_per_years = {'data': [], 'labels': []}
    for year in range(begin_yr, end_yr+1):
        item = {'label': year, 'data': []}
        for af, _ in top_affil_items:
            item['data'].append(Counter(all_affiliations[year]).get(af, 0))
        pub_per_years['data'].append(item)

    for af, _ in top_affil_items:
        pub_per_years['labels'].append(af)

    return jsonify(pub_per_years)


@domain.route('/api/v1.0/total-pub-per-year')
def get_total_pub_per_year(ntop=20, begin_yr=2006, end_yr=2018):
    PubTable = Table('pubs', metadata, autoload=True, autoload_with=engine)
    s = select([PubTable]).where(extract('year', PubTable.c.pub_date)>=begin_yr)
    s = s.where(extract('year', PubTable.c.pub_date)<=end_yr)
    doctype = request.args.get('doctype', None)
    if doctype:
        s = s.where(PubTable.c.doctype == doctype)
    pubs = defaultdict(int)
    for rec in conn.execute(s):
        year = rec.pub_date.year
        pubs[year] += 1

    data = {'data': [], 'labels': []}
    for y in range(begin_yr, end_yr+1):
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
                            author_affiliation_years[year][author['affiliation']['@id']] = set(
                                [author['ce:indexed-name']])

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
                    affilname = affil.get('affilname', '')
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
    ScholarTable = Table('scholarship_info', kwmetadata, autoload=True, autoload_with=kwengine)
    s = select([ScholarTable.c.first_name_en, ScholarTable.c.last_name_en])
    scholars = set()
    for rec in kwconn.execute(s):
        firstname, lastname = rec
        firstname = firstname.lower() \
            .replace('mrs.', '') \
            .replace('mr.', '') \
            .replace('ms.', '') \
            .replace('dr.', '')
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


@domain.route('/api/v1.0/scholar-first-author')
def get_scholarship_studs_main_author(ntop=20, nyears=20):
    ScholarTable = Table('scholarship_info', kwmetadata, autoload=True, autoload_with=kwengine)
    s = select([ScholarTable.c.first_name_en, ScholarTable.c.last_name_en])
    scholars = set()
    for rec in kwconn.execute(s):
        firstname, lastname = rec
        firstname = firstname.lower() \
            .replace('mrs.', '') \
            .replace('mr.', '') \
            .replace('ms.', '') \
            .replace('dr.', '')
        if firstname and lastname:
            scholars.add('{}.'.format(' '.join([lastname.lower(), firstname.lower()[0]])))

    PubTable = Table('pubs', metadata, autoload=True, autoload_with=engine)
    s = select([PubTable])
    year_scholar_first_authors = defaultdict(set)
    year_scholar_other_authors = defaultdict(set)
    year_scholar_cor_authors = defaultdict(set)
    for rec in conn.execute(s):
        year = rec.pub_date.year
        authors = rec.data['abstracts-retrieval-response']['authors']['author']
        if isinstance(authors, list):
            for author in authors:
                idxname = author['ce:indexed-name'].lower()
                if idxname in scholars:
                    if author['@seq'] == '1':
                        year_scholar_first_authors[year].add(idxname)
                    else:
                        year_scholar_other_authors[year].add(idxname)
        else:
            idxname = authors['ce:indexed-name'].lower()
            if idxname in scholars:
                if author['@seq'] == '1':
                    year_scholar_first_authors[year].add(idxname)
                else:
                    year_scholar_other_authors[year].add(idxname)
        '''
        # Get correspondence authors
        try:
            corres_person = rec.data['abstracts-retrieval-response']['item']['bibrecord']['head']['correspondence']['person']
        except (KeyError, TypeError):
            print(rec.scopus_id)
            continue
        else:
            idxname = corres_person['ce:indexed-name'].lower()
            if idxname in scholars:
                year_scholar_cor_authors[year].add(idxname)
        '''

    sorted_years = sorted(year_scholar_first_authors, reverse=False)[:nyears]

    '''
    for yr in sorted_years:
        year_scholar_cor_authors[yr].difference_update(year_scholar_first_authors[yr])
    '''

    plot_data = {'data': [], 'labels': sorted_years}
    first_authors = []
    other_authors = []
    # cor_authors = []
    for yr in sorted_years:
        first_authors.append(len(year_scholar_first_authors[yr]))
        other_authors.append(len(year_scholar_other_authors[yr]))
        # cor_authors.append(len(year_scholar_cor_authors[yr]))

    plot_data['data'].append({
        'data': first_authors,
        'label': 'First Authors'
    })
    plot_data['data'].append({
        'data': other_authors,
        'label': 'Other Authors'
    })
    '''
    plot_data['data'].append({
        'data': cor_authors,
        'label': 'Correspondence Authors'
    })
    '''

    return jsonify(plot_data)


@domain.route('/api/v1.0/collaboration-author')
def get_researcher_collaboration(ntop=15, begin_yr=2006, end_yr=2018):
    PubTable = Table('pubs', metadata, autoload=True, autoload_with=engine)
    s = select([PubTable]).where(extract('year', PubTable.c.pub_date)>=begin_yr)
    s = s.where(extract('year', PubTable.c.pub_date)<=end_yr)
    uni_first_authors = defaultdict(int)
    uni_other_authors = defaultdict(int)
    uni_foreign_authors = defaultdict(int)
    all_affiliations = {}
    total_pubs = defaultdict(int)
    thai_affils = set()
    for rec in conn.execute(s):
        affil_data = rec.data['abstracts-retrieval-response'].get('affiliation', [])
        if isinstance(affil_data, list):
            for af in affil_data:
                all_affiliations[af['@id']] = (af['affilname'],
                                               af['affiliation-country'])
        elif isinstance(affil_data, dict):
            all_affiliations[affil_data['@id']] = (affil_data['affilname'],
                                                   affil_data['affiliation-country'])
        authors = rec.data['abstracts-retrieval-response']['authors']['author']
        if isinstance(authors, list):
            # For multiauthor paper, both the first author and others are counted.
            has_first = False
            has_foriegn = False
            has_other = False
            for author in authors:
                idxname = author['ce:indexed-name'].lower()
                affils = author.get('affiliation', {})
                if isinstance(affils, list):
                    uni_id = affils[0].get('@id', '')
                else:
                    uni_id = author.get('affiliation', {}).get('@id', '')
                if uni_id == '':
                    continue

                uniname, unicountry = all_affiliations[uni_id]
                if 'Thammasat' in uniname:
                    uniname = 'Thammasat Univeristy'
                if 'University of Technology Thonburi' in uniname:
                    uniname = "King Mongkut's University of Technology Thonburi"
                if unicountry != 'Thailand':
                    has_foriegn = True
                else:
                    thai_affils.add(uniname)

                if author['@seq'] == '1':
                    has_first = True
                else:
                    has_other = True
                total_pubs[uniname] += 1

            if has_first:
                uni_first_authors[uniname] += 1
            if has_other:
                uni_other_authors[uniname] += 1
            if has_foriegn:
                uni_foreign_authors[uniname] += 1
        else:
            idxname = authors['ce:indexed-name'].lower()
            affils = author.get('affiliation', {})
            if isinstance(affils, list):
                uni_id = affils[0].get('@id', '')
            else:
                uni_id = author.get('affiliation', {}).get('@id', '')
            if uni_id == '':
                continue

            uniname, unicountry = all_affiliations[uni_id]
            if unicountry != 'Thailand':
                uni_foreign_authors[uniname] += 1
            else:
                thai_affils.add(uniname)

            if author['@seq'] == '1':
                uni_first_authors[uniname] += 1
            else:
                uni_other_authors[uniname] += 1
            total_pubs[uniname] += 1

    sorted_unis = sorted([k for k in total_pubs.keys() if k in thai_affils],
                          key=lambda x: total_pubs[x],
                         reverse=True)[:ntop]

    plot_data = {'data': [], 'labels': sorted_unis}
    first_authors = []
    other_authors = []
    foreign_authors = []
    for u in sorted_unis[:ntop]:
        first_authors.append(uni_first_authors[u])
        other_authors.append(uni_other_authors[u])
        foreign_authors.append(uni_foreign_authors[u])

    plot_data['data'].append({
        'data': first_authors,
        'label': 'First Authors'
    })
    plot_data['data'].append({
        'data': other_authors,
        'label': 'Other Authors'
    })
    plot_data['data'].append({
        'data': foreign_authors,
        'label': 'Foreign Authors'
    })

    return jsonify(plot_data)

@domain.route('/api/v1.0/active-scholar-author')
def get_active_scholarship_studs_author(duration=5, nyears=20):
    ScholarTable = Table('scholarship_info', kwmetadata, autoload=True, autoload_with=kwengine)
    s = select([ScholarTable.c.first_name_en, ScholarTable.c.last_name_en])
    scholars = set()
    for rec in kwconn.execute(s):
        firstname, lastname = rec
        firstname = firstname.lower() \
            .replace('mrs.', '') \
            .replace('mr.', '') \
            .replace('ms.', '') \
            .replace('dr.', '')
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

    sorted_years = sorted(year_scholar_authors, reverse=False)[2:nyears]
    start_year = sorted_years[0]
    last_year = sorted_years[-1]

    active_authors = []
    inactive_authors = []
    all_authors = set()
    for yr in sorted_years:
        if yr > last_year:
            active_author_set = year_scholar_authors[last_year]
        else:
            active_author_set = year_scholar_authors[yr]
        for y in range(yr, yr + duration):
            active_author_set.update(year_scholar_authors[y])
            all_authors.update((year_scholar_authors[y]))
        active_authors.append(len(active_author_set))
        inactive_authors.append(len(all_authors) - len(active_author_set))

    plot_data = {'data': [], 'labels': sorted_years}

    plot_data['data'].append({
        'data': active_authors,
        'label': 'Active Authors'
    })
    plot_data['data'].append({
        'data': inactive_authors,
        'label': 'Inactive Authors'
    })

    return jsonify(plot_data)


@domain.route('/api/v1.0/active-scholar-author-graduate')
def get_active_scholarship_studs_author_graduate(duration=5, nyears=20):
    ScholarTable = Table('scholarship_info', kwmetadata, autoload=True, autoload_with=kwengine)
    s = select([ScholarTable.c.first_name_en, ScholarTable.c.last_name_en, ScholarTable.c.graduated_date])
    scholars = {}
    for rec in kwconn.execute(s):
        firstname, lastname, graduate_date = rec
        firstname = firstname.lower() \
            .replace('mrs.', '') \
            .replace('mr.', '') \
            .replace('ms.', '') \
            .replace('dr.', '')
        if firstname and lastname:
            scholars['{}.'.format(' '.join(
                [lastname.lower(), firstname.lower()[0]]))] = graduate_date

    PubTable = Table('pubs', metadata, autoload=True, autoload_with=engine)
    s = select([PubTable])
    scholar_authors = defaultdict(set)
    for rec in conn.execute(s):
        year = rec.pub_date.year
        authors = rec.data['abstracts-retrieval-response']['authors']['author']
        if isinstance(authors, list):
            for author in authors:
                idxname = author['ce:indexed-name'].lower()
                if idxname in scholars:
                    if author['@seq'] == '1':
                        scholar_authors[idxname].add(year)
        else:
            idxname = authors['ce:indexed-name'].lower()
            if idxname in scholars:
                if author['@seq'] == '1':
                    scholar_authors[idxname].add(year)

    time_after_graduate = defaultdict(int)

    for author in scholar_authors:
        graduate_date = scholars[author]
        if graduate_date:
            valid_pub_years = [i for i in scholar_authors[author] if i > graduate_date.year]
            if valid_pub_years:
                tag = min(valid_pub_years) - graduate_date.year
                time_after_graduate[tag] += 1

    numyear = range(min(time_after_graduate.keys()), max(time_after_graduate.keys())+1)
    tagdata = []
    for ny in numyear:
        tagdata.append(time_after_graduate[ny])
    plot_data = {'data': [], 'labels': list(numyear)}

    plot_data['data'].append({
        'data': tagdata,
        'label': 'Time after graduate'
    })

    return jsonify(plot_data)

@domain.route('/api/v1.0/scholar-academic-position')
def get_scholar_academic_position(ntop=20, nyears=20):
    ScholarTable = Table('scholarship_info', kwmetadata, autoload=True, autoload_with=kwengine)
    s = select([ScholarTable.c.first_name_en, ScholarTable.c.last_name_en])
    scholars = set()
    for rec in kwengine.execute(s):
        firstname, lastname = rec
        firstname = firstname.lower() \
            .replace('mrs.', '') \
            .replace('mr.', '') \
            .replace('ms.', '') \
            .replace('dr.', '')
        if firstname and lastname:
            scholars.add('{}.'.format(' '.join([lastname.lower(), firstname.lower()[0]])))

    df = read_excel('static/data/nap_2562-04-02.xlsx')
    academics = defaultdict(set)

    for _, row in df.iterrows():
        if not isna(row.Name_Eng):
            try:
                firstname, lastname = row.Name_Eng.split()
            except ValueError:
                continue
            else:
                if firstname and lastname:
                    name = '{}.'.format(' '.join([lastname.lower(), firstname.lower()[0]]))
                    if name in scholars:
                        academics[row.Academic_Position].add(name)

    plot_data = {'data': [], 'labels': []}
    for k in academics:
        plot_data['data'].append(len(academics[k]))
        plot_data['labels'].append(k)

    total_rschrs = sum(plot_data['data'])
    plot_data['data'] = [round(float(num)/total_rschrs,4)*100.0 for num in plot_data['data']]

    return jsonify(plot_data)


@domain.route('/api/v1.0/researcher-academic-position')
def get_researcher_academic_position_period(begin_yr=2014, end_yr=2018):
    PubTable = Table('pubs', metadata, autoload=True, autoload_with=engine)
    s = select([PubTable]).where(extract('year', PubTable.c.pub_date)>=begin_yr)
    s = s.where(extract('year', PubTable.c.pub_date)<=end_yr)
    researchers = set()
    for rec in conn.execute(s):
        year = rec.pub_date.year
        authors = rec.data['abstracts-retrieval-response']['authors']['author']
        if isinstance(authors, list):
            for author in authors:
                idxname = author['ce:indexed-name'].lower()
                researchers.add(idxname)
        else:
            idxname = authors['ce:indexed-name'].lower()
            researchers.add(idxname)

    df = read_excel('static/data/nap_2562-04-02.xlsx')
    academics = defaultdict(set)

    for _, row in df.iterrows():
        if not isna(row.Name_Eng):
            try:
                firstname, lastname = row.Name_Eng.split()
            except ValueError:
                continue
            else:
                if firstname and lastname:
                    name = '{}.'.format(' '.join([lastname.lower(), firstname.lower()[0]]))
                    if name in researchers:
                        academics[row.Academic_Position].add(name)

    plot_data = {'data': [], 'labels': []}
    for k in academics:
        plot_data['data'].append(len(academics[k]))
        plot_data['labels'].append(k)

    total_rschrs = sum(plot_data['data'])
    plot_data['data'] = [round(float(num)/total_rschrs*100,2) for num in plot_data['data']]

    return jsonify(plot_data)


@domain.route('/api/v1.0/wordcloud')
def get_wordcloud():
    year = int(request.args.get('year'))
    PubTable = Table('pubs', metadata, autoload=True, autoload_with=engine)
    abstracts = []

    s = select([PubTable])
    for row in conn.execute(s):
        if row.pub_date.year == year:
            try:
                abstract = row.data['abstracts-retrieval-response']['coredata']['dc:description']
            except KeyError:
                continue
            abstract = [token.lower() for token in regexp_tokenize(abstract, '[^\d\W\s]{3,}') if
                        token.lower() not in stop_words]
            abstracts.append(' '.join(abstract))

    img = BytesIO()
    wordcloud = WordCloud(
        background_color='white',
        stopwords=stop_words,
        max_words=200,
        max_font_size=40,
        random_state=42,
        width=800,
        height=400
    ).generate(str(abstracts))
    wordcloud.to_image().save(img, 'png')
    img.seek(0)
    return send_file(img, mimetype='image/png')


@domain.route('/api/v1.0/wordcloud-field')
def get_wordcloud_field():
    area = request.args.get('area', 'all')
    PubTable = Table('pubs', metadata, autoload=True, autoload_with=engine)
    s = select([PubTable])
    abstracts = []
    for row in conn.execute(s):
        if area == 'all':
            try:
                abstract = row.data['abstracts-retrieval-response']['coredata']['dc:description']
            except KeyError:
                continue
            abstract = [token.lower() for token in regexp_tokenize(abstract, '[^\d\W\s]{3,}') if
                        token.lower() not in stop_words]
            abstracts.append(' '.join(abstract))

        else:
            for sbj in row.data['abstracts-retrieval-response']['subject-areas']['subject-area']:
                if sbj['@abbrev'] == area:
                    try:
                        abstract = row.data['abstracts-retrieval-response']['coredata']['dc:description']
                    except KeyError:
                        continue
                    abstract = [token.lower() for token in regexp_tokenize(abstract, '[^\d\W\s]{3,}') if
                                token.lower() not in stop_words]
                    abstracts.append(' '.join(abstract))

    img = BytesIO()
    wordcloud = WordCloud(
        background_color='white',
        stopwords=stop_words,
        max_words=100,
        max_font_size=40,
        random_state=42,
        width=800,
        height=400
    ).generate(str(abstracts))
    wordcloud.to_image().save(img, 'png')
    img.seek(0)
    return send_file(img, mimetype='image/png')


@domain.route('/api/v1.0/wordcloud-affil')
def create_wordcloud_image_affil():
    affil = request.args.get('affil', None)
    PubTable = Table('pubs', metadata, autoload=True, autoload_with=engine)
    s = select([PubTable])
    abstracts = []
    pub_set = set()
    for rec in conn.execute(s):
        if affil:
            affil_data = rec.data['abstracts-retrieval-response'].get('affiliation', [])
            if isinstance(affil_data, list):
                for af in affil_data:
                    if af['affilname'] == affil:
                        try:
                            pub_set.add(rec.data['abstracts-retrieval-response']['coredata']['dc:description'])
                        except KeyError:
                            continue
            elif isinstance(affil_data, dict):
                if affil_data['affilname'] == affil:
                    try:
                        pub_set.add(rec.data['abstracts-retrieval-response']['coredata']['dc:description'])
                    except KeyError:
                        continue

    for abstract in pub_set:
        abstract = [token.lower() for token in regexp_tokenize(abstract, '[^\d\W\s]{3,}') if
                    token.lower() not in stop_words]
        abstracts.append(' '.join(abstract))

    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 1),
                                 analyzer='word', min_df=10, max_df=0.8)

    # TODO: try generate from frequencies
    img = BytesIO()
    wordcloud = WordCloud(
        background_color='white',
        stopwords=stop_words,
        max_words=200,
        max_font_size=40,
        random_state=42,
        width=800,
        height=400
    ).generate(str(abstracts))
    wordcloud.to_image().save(img, 'png')
    img.seek(0)
    return send_file(img, mimetype='image/png')


@domain.route('/topics')
@domain.route('/topics/')
def topics(year=None):
    year = int(request.args.get('year', 0))
    area = request.args.get('area', 'all')
    years = set()
    PubTable = Table('pubs', metadata, autoload=True, autoload_with=engine)
    s = select([PubTable])
    abstracts = []
    bigram_set = defaultdict(int)
    areas = set()
    all_affiliations = set()
    for row in conn.execute(s):
        years.add(row.pub_date.year)
        for sbj in row.data['abstracts-retrieval-response']['subject-areas']['subject-area']:
            areas.add(sbj['@abbrev'])

        try:
            abstract = row.data['abstracts-retrieval-response']['coredata']['dc:description']
        except KeyError:
            continue
        # abstract = [token.lower() for token in regexp_tokenize(abstract, '[^\d\W\s]{3,}') if token.lower() not in stop_words]
        # abstracts.append(' '.join(abstract))
        abstract = abstract.lower()
        abstracts.append(abstract)
        if row.pub_date.year == year:
            for bg in nltk.ngrams(abstract.split(), 2):
                bigram_set[' '.join(bg)] += 1

        affil_set = set()
        affil_data = row.data['abstracts-retrieval-response'].get('affiliation', [])
        if isinstance(affil_data, list):
            for af in affil_data:
                if af['affiliation-country'] == 'Thailand':
                    affil_set.add(af['affilname'])
            all_affiliations.update(affil_set)
        elif isinstance(affil_data, dict):
            if affil_data['affiliation-country'] == 'Thailand':
                all_affiliations.add(affil_data['affilname'])

    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(2, 2),
                                 analyzer='word', min_df=10, max_df=0.8)
    vectorizer.fit(abstracts)
    highlights = {}
    for k in bigram_set:
        highlights[k] = float(vectorizer.vocabulary_.get(k, 0))

    highlights = sorted(highlights.items(), key=lambda x: x[1], reverse=True)[:20]

    if year == 0:
        year = sorted(years)[-1]

    return render_template('domain/topics.html', years=sorted(years),
                           year=year, areas=sorted(areas), area=area,
                           highlights=highlights, affiliations=sorted(all_affiliations))


@domain.route('/api/v1.0/bigram-tdif')
def calculate_tdif():
    year = int(request.args.get('year', 0))
    PubTable = Table('pubs', metadata, autoload=True, autoload_with=engine)
    abstracts = []

    bigram_set = defaultdict(int)

    s = select([PubTable])
    for row in conn.execute(s):
        try:
            abstract = row.data['abstracts-retrieval-response']['coredata']['dc:description']
        except KeyError:
            continue
        abstract = [token.lower() for token in regexp_tokenize(abstract, '[^\d\W\s]{3,}') if
                    token.lower() not in stop_words]
        abstracts.append(' '.join(abstract))
        if row.pub_date.year == year:
            for bg in nltk.ngrams(abstract, 2):
                bigram_set[' '.join(bg)] += 1

    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(2, 2),
                                 analyzer='word', min_df=10, max_df=0.8)
    vectorizer.fit(abstracts)
    highlights = {}
    for k in bigram_set:
        highlights[k] = float(vectorizer.vocabulary_.get(k, 0))

    plot_data = {'data': [], 'labels': []}
    for k, v in sorted(highlights.items(), key=lambda x: x[1], reverse=True)[:100]:
        plot_data['data'].append(v)
        plot_data['labels'].append(k)

    return jsonify(plot_data)


@domain.route('/wordcloud-affil')
def get_wordcloud_affil():
    affil = request.args.get('affil', '')

    PubTable = Table('pubs', metadata, autoload=True, autoload_with=engine)
    s = select([PubTable])
    all_affiliations = set()
    for rec in conn.execute(s):
        affil_data = rec.data['abstracts-retrieval-response'].get('affiliation', [])
        if isinstance(affil_data, list):
            for af in affil_data:
                if af['affiliation-country'] == 'Thailand':
                    all_affiliations.add(af['affilname'])
        elif isinstance(affil_data, dict):
            if affil_data['affiliation-country'] == 'Thailand':
                all_affiliations.add(affil_data['affilname'])
    return render_template('/domain/wordcloud-affil.html', affil=affil,
                           affils=sorted(all_affiliations))
