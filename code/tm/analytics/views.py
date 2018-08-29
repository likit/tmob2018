# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from sqlalchemy import MetaData, create_engine
from collections import namedtuple, defaultdict
from py2neo import Graph, Relationship, NodeMatcher, Node
from django.contrib.postgres.search import SearchVector
from django.contrib.auth import get_user_model
from account.models import Profile

User = get_user_model()

graph = Graph(host='neo4j_db', password='_genius01_', scheme='bolt')

meta = MetaData()
engine = create_engine('postgresql+psycopg2://postgres:_genius01_@postgres_db/keywordsdw')
conn = engine.connect()

Researcher = namedtuple('Researcher', ['id', 'firstname', 'lastname',
                                        'word_en', 'count', 'affiliation',
                                        'total_abstract' ,'sc'])

# Create your views here.
def res_list(request):
    search_term = request.GET.get('q')
    res_list = []
    nounchunks = []
    if search_term:
        if len(search_term.split(' ')) > 1:
            tsquery = ' & '.join(search_term.split(' '))
            tsquery_word = ' | '.join(search_term.split(' '))
        else:
            tsquery = search_term
            tsquery_word = search_term
        query = ("select id, chunk_en from noun_chunks where "
                    "to_tsvector(chunk_en) @@ to_tsquery('%s');")
        nounchunks += conn.execute(query % tsquery).fetchall()
        results = conn.execute("select distinct keywords.id, first_name, last_name, word_en, count, affils.name"
                                " from keywords inner join affils on keywords.affil_scopus_id=affils.scopus_id "
                                "where to_tsvector(word_en) @@ to_tsquery('%s')"
                                " order by count desc" % tsquery_word).fetchall()
        if results:
            for rec in results:
                query = ('select count(*) from abstracts inner join abstract_has_keywords '
                            'on abstract_has_keywords.abstract_id=abstracts.id '
                            'inner join keywords on keywords.id=abstract_has_keywords.keyword_id '
                            'where keywords.id=%d;')
                total_abstract = conn.execute(query % int(rec[0])).scalar()

                fname = rec[1].replace("'", "\'") if rec[1] else ''
                lname = rec[2].replace("'", "\'") if rec[2] else ''

                query = ("select id,scholarship_info_id from authors where lower(first_name)=lower(%s) "
                            "and lower(last_name)=lower(%s)")
                _author = conn.execute(query, (fname, lname)).fetchone()
                if _author:
                    _author_id, _sc_id = _author[0], _author[1]
                    if _author_id:
                        if _sc_id:
                            sc = True
                        else:
                            sc = False
                        res_list.append(Researcher(_author_id, rec[1], rec[2], rec[3], rec[4], rec[5], total_abstract, sc))


    profiles = {}
    for word in search_term.split(' '):
        for p in Profile.objects.annotate(
            search=SearchVector('field_of_interest')).filter(search=word):
            field_of_interest = (f.strip() for f in p.field_of_interest.split(','))
            profiles[p.user.username] = (p.user.first_name, p.user.last_name, field_of_interest)

    return render(request, template_name='analytics/res_list.html',
            context={'search_term': search_term, 'results': res_list,
                        'nounchunks': nounchunks, 'profiles': profiles})

def noun_chunk_detail(request):
    nc_id = request.GET.get('ncid')
    abstracts_list = []
    if nc_id:
        nc = conn.execute('select chunk_en from noun_chunks where id=%d' % int(nc_id)).fetchone()[0]
        query = ("select abstracts.id, title_en, pub_date, cited from abstracts "
                    "inner join abstract_has_nounchunk "
                    "on abstract_has_nounchunk.abstract_id=abstracts.id "
                    "inner join noun_chunks on noun_chunks.id=abstract_has_nounchunk.noun_chunk_id "
                    "where noun_chunks.id=%d;")
        for rec in conn.execute(query % int(nc_id)).fetchall():
            _bag = {'abstract': rec}
            _bag['authors'] = conn.execute("select authors.* from abstracts inner join abstract_has_author "
                                "on abstract_has_author.abstract_id=abstracts.id inner join "
                                "authors on abstract_has_author.author_id=authors.id where abstracts.id=%d;"
                                % int(rec[0])).fetchall()
            _bag['nounchunks'] = conn.execute("select noun_chunks.* from abstracts inner join abstract_has_nounchunk "
                                "on abstract_has_nounchunk.abstract_id=abstracts.id inner join "
                                "noun_chunks on abstract_has_nounchunk.noun_chunk_id=noun_chunks.id where abstracts.id=%d;"
                                % int(rec[0])).fetchall()
            abstracts_list.append(_bag)

    else:
        nc = ''
    return render(request, template_name='analytics/nounchunk_abs.html',
                    context={'noun_chunk': nc, 'abstracts': abstracts_list})

def show_profile(request, author_id):
    degrees = {1: 'Bachelor', 2: 'Master', 3: 'Doctorate'}
    author = conn.execute('select * from authors where id=%s' % author_id).fetchone()
    profile = conn.execute('select * from scholarship_info where scholarship_info.id=%d'
                            % author.scholarship_info_id).fetchone()
    author_scopus_id = author[3]
    if author:
        query = ("select word_en from keywords where author_scopus_id='%s'" % author_scopus_id)
        results = conn.execute(query).fetchall()
        keywords = []
        for rec in results:
            keywords.append(rec[0])

        query = ("select abstracts.id,abstracts.title_en from abstracts inner join abstract_has_author "
                "on abstract_has_author.abstract_id=abstracts.id inner join "
                "authors on abstract_has_author.author_id=authors.id "
                "where authors.id=%s" % author_id)
        abstracts = conn.execute(query).fetchall()
        fields = defaultdict(int)
        for abstract in abstracts:
            query = ("select name from research_fields inner join field_has_abstract on "
                     "field_has_abstract.field_id=research_fields.id inner join "
                     "abstracts on field_has_abstract.abstract_id=abstracts.id "
                     "where abstracts.id=%d" % int(abstract[0]))
            results =  conn.execute(query).fetchall()
            for f in results:
                fields[f[0]] += 1
        fields.default_factory = None
        return render(request, template_name="analytics/profile.html",
                        context={'author': author,
                                'abstracts': abstracts,
                                'profile': profile,
                                'degree': degrees.get(int(profile.degree), 'Other'),
                                'fields': fields,
                                'keywords': keywords})


def main_db(request):
    total_words = conn.execute('select count(*) from keywords').scalar()
    total_abstracts = conn.execute('select count(*) from abstracts').scalar()
    fields = []
    query = ('select count(*), name from research_fields inner join '
                'field_has_abstract on field_has_abstract.field_id=research_fields.id group by name;')
    for field in conn.execute(query).fetchall():
        fields.append(field)

    fields = sorted(fields, key=lambda x: x[0], reverse=True)
    return render(request, template_name="analytics/main.html",
                context={'total_words': total_words,
                            'total_abstracts': total_abstracts,
                            'fields': fields
                            })


def show_field(request, field_name):
    query = 'MATCH (f:Field{name:"%s"})-[:IN]-(:Abstract)-[:AUTHORED]-(au:Author)-[:AFFILIATE]-(af:Affiliation{country:"Thailand"}) RETURN f,au,af' % field_name
    results = list(graph.run(query))
    authors = []
    if results:
        for res in results:
            authors.append((res['au'], res['af']))
    return render(request, template_name="analytics/field_author.html",
                context={'authors': authors, 'field': field_name})

def show_profile_by_name(request):
    first_name = request.GET.get('firstname', '')
    last_name = request.GET.get('lastname', '')
    first_name = first_name.replace("'", "\'") if first_name else first_name
    last_name = last_name.replace("'", "\'") if last_name else last_name
    degrees = {1: 'Bachelor', 2: 'Master', 3: 'Doctorate'}
    if first_name and last_name:
        author = conn.execute("select * from authors where "
                      "lower(first_name)=lower(%s) and lower(last_name)=lower(%s)",
                      (first_name, last_name)).fetchone()
        if author:
            if author.scholarship_info_id:
                profile = conn.execute('select * from scholarship_info where scholarship_info.id=%d'
                                       % author.scholarship_info_id).fetchone()
                degree = degrees.get(profile.degree, '')
            else:
                profile = None
                degree = ''
            keywords = conn.execute("select word_en,count from keywords where author_scopus_id='%s'"
                                    % author.scopus_id).fetchall()
            keywords = set([(kw.word_en,kw.count) for kw in keywords])
            keywords = sorted(keywords, key=lambda x: x[1], reverse=True)
            query = ("select abstracts.id,abstracts.title_en "
                     "from abstracts inner join abstract_has_author "
                     "on abstract_has_author.abstract_id=abstracts.id inner join "
                     "authors on abstract_has_author.author_id=authors.id "
                     "where authors.id=%s" % author.id)
            abstracts = conn.execute(query).fetchall()
            fields = defaultdict(int)
            for abstract in abstracts:
                query = ("select name from research_fields inner join field_has_abstract on "
                         "field_has_abstract.field_id=research_fields.id inner join "
                         "abstracts on field_has_abstract.abstract_id=abstracts.id "
                         "where abstracts.id=%d" % int(abstract[0]))
                results =  conn.execute(query).fetchall()
                for f in results:
                    fields[f[0]] += 1
            fields.default_factory = None
            query = ("select name, country, year from affil_history inner join affils "
                     "on affils.id=affiliation_id where author_id=%s;" % author.id)
            affiliations = set((tuple(af) for af in conn.execute(query).fetchall()))
            affiliations = sorted(affiliations, key=lambda x: x[2])

        return render(request, template_name="analytics/profile_by_name.html",
                      context={'author': author, 'abstracts': abstracts,
                      'fields': fields, 'affils': affiliations,
                      'keywords': keywords, 'profile': profile,
                       'degree': degree})
    return render(request, template_name="analytics/profile_by_name.html",
                  context={})


def show_abstract(request, abstract_id):
    if abstract_id:
        abstract = conn.execute("select * from abstracts where id=%s;" % abstract_id).fetchone()
        if abstract:
            authors = conn.execute("select authors.* from abstracts inner join abstract_has_author "
                            "on abstract_has_author.abstract_id=abstracts.id inner join "
                            "authors on abstract_has_author.author_id=authors.id where abstracts.id=%s;"
                            % abstract_id).fetchall()
            keywords = conn.execute("select * from keywords inner join abstract_has_keywords "
                                    "on abstract_has_keywords.keyword_id=keywords.id inner join "
                                    "abstracts on abstract_has_keywords.abstract_id=abstracts.id "
                                    "where abstracts.id=%s" % abstract_id).fetchall()
            keywords = set([kw.word_en for kw in keywords])
            print(keywords)
            return render(request, template_name='analytics/abstract.html',
                  context={'authors': authors, 'abstract': abstract, 'keywords': keywords})
    return render(request, template_name='analytics/abstract.html',
                  context={'authors': [], 'abstract': None})


def show_abstract_per_person(request):
    data = []
    for rec in conn.execute(" select status, count(*) as c from scholarship_info group by status;"):
        data.append(rec[1])
    return JsonResponse({'data': data})

def get_num_active_scholar_studs(request):
    actives = {}
    totals = {}
    sqlquery = ('select affil,count(*) as c from active_scholar_students '
                'inner join scholarship_info on scholarship_info_id=scholarship_info.id '
                'where scholarship_info.status=true '
                'group by affil order by c desc limit 30;')
    for affil, cnt in conn.execute(sqlquery):
        actives[affil] = cnt

    sqlquery = ('select affil,count(*) as c from scholarship_info '
                'where scholarship_info.status=true '
                'group by affil;')

    active_data = []
    inactive_data = []
    labels = []
    activecolors = []
    inactivecolors = []
    for affil, cnt in conn.execute(sqlquery):
        totals[affil] = cnt

    sorted_active_data = sorted([(k,v) for k,v in actives.items()],
                                    key=lambda x: x[1], reverse=True)
    for k,v in sorted_active_data:
        active_data.append(actives[k])
        inactive_data.append(totals[k] - actives[k])
        activecolors.append('rgb(199,0,57)')
        inactivecolors.append('rgb(100,116,164)')
        labels.append(k)

    return JsonResponse({'actives': active_data,
                'inactives': inactive_data,
                'activecolors': activecolors,
                'inactivecolors': inactivecolors,
                'labels': labels})


def get_abstract_fields(request):
    sqlquery = ('select abbr,count(*) as c from field_has_abstract '
                'inner join research_fields on research_fields.id=field_has_abstract.field_id '
                'inner join abstracts on field_has_abstract.abstract_id=abstracts.id '
                'where abstracts.pub_date>\'2013-01-01\' '
                'group by abbr order by c desc;')
    data = []
    labels = []
    backgroundColors = []
    for f,n in conn.execute(sqlquery):
        data.append(n)
        labels.append(f)
        backgroundColors.append('rgb(100,116,164)')

    return JsonResponse({'data': data, 'labels': labels, 'backgroundColors': backgroundColors})


def get_researcher_by_field(request):
    inactive_counts = defaultdict(int)
    active_counts = defaultdict(int)

    all_researchers = defaultdict(dict)
    sqlquery = ('select authors.id,research_fields.abbr,count(research_fields.abbr) as num_papers from field_has_abstract inner join research_fields on field_has_abstract.field_id=research_fields.id '
                'inner join abstract_has_author on abstract_has_author.abstract_id=field_has_abstract.abstract_id '
                'inner join authors on authors.id=abstract_has_author.author_id '
                'inner join scholarship_info on scholarship_info.id=authors.scholarship_info_id '
                'where scholarship_info.status=true '
                'group by authors.id,abbr '
                'order by authors.id,num_papers desc;')
    for auth_id, field_abbr, num_papers in conn.execute(sqlquery):
        if auth_id not in all_researchers:
            all_researchers[auth_id] = field_abbr

    active_researchers = set()
    sqlquery = 'select author_id from active_scholar_students;'
    for row in conn.execute(sqlquery):
        active_researchers.add(row[0])


    for auth_id in all_researchers:
        if auth_id in active_researchers:
            active_counts[all_researchers[auth_id]] += 1
        else:
            inactive_counts[all_researchers[auth_id]] += 1

    actives = []
    inactives = []
    labels = []
    activecolors = []
    inactivecolors = []
    data = [(k,v) for k,v in active_counts.items()]
    sorted_fields = [k for k,v in sorted(data,key=lambda x: x[1], reverse=True)]
    for field in sorted_fields:
        actives.append(active_counts[field])
        inactives.append(inactive_counts[field])
        labels.append(field)
        activecolors.append('rgb(199,0,57)')
        inactivecolors.append('rgb(100,116,164)')

    return JsonResponse({'actives': actives, 'inactives': inactives,
                            'labels': labels,
                            'activecolors': activecolors,
                            'inactivecolors': inactivecolors})


def get_scholar_joined_tm_ratio(request):
    sqlquery = ('select count(*) as c from tm_researcher_profile;')
    total_tm = conn.execute(sqlquery).scalar()
    sqlquery = ('select count(*) as c from tm_researcher_profile '
                'where scholarship_info_id is not NULL')
    total_scholar = conn.execute(sqlquery).scalar()
    return JsonResponse({'data': [total_scholar, total_tm],
                'labels': ['scholarship', 'non-scholarship']})


def get_num_active_scholar_tm(request):
    actives = {}
    totals = {}
    sqlquery = ('select affil,count(*) as c from scholarship_info '
                'inner join tm_researcher_profile on tm_researcher_profile.scholarship_info_id=scholarship_info.id '
                'where scholarship_info.status=true '
                'group by affil order by c desc limit 30;')
    for affil, cnt in conn.execute(sqlquery):
        actives[affil] = cnt

    sqlquery = ('select affil,count(*) as c from scholarship_info '
                'where scholarship_info.status=true '
                'group by affil;')

    active_data = []
    inactive_data = []
    labels = []
    activecolors = []
    inactivecolors = []
    for affil, cnt in conn.execute(sqlquery):
        totals[affil] = cnt

    sorted_active_data = sorted([(k,v) for k,v in actives.items()],
                                key=lambda x: x[1], reverse=True)
    for k,v in sorted_active_data:
        active_data.append(actives[k])
        inactive_data.append(totals[k] - actives[k])
        activecolors.append('rgb(199,0,57)')
        inactivecolors.append('rgb(100,116,164)')
        labels.append(k)

    return JsonResponse({'actives': active_data,
                         'inactives': inactive_data,
                         'activecolors': activecolors,
                         'inactivecolors': inactivecolors,
                         'labels': labels})


def get_activeness_scholar_tm(request):
    tm_actives = {}
    totals = {}
    sqlquery = ('select affil,count(*) as c from active_scholar_students '
                'inner join scholarship_info on active_scholar_students.scholarship_info_id=scholarship_info.id '
                'inner join tm_researcher_profile on tm_researcher_profile.scholarship_info_id=active_scholar_students.scholarship_info_id '
                'where scholarship_info.status=true '
                'group by affil;')
    for affil, cnt in conn.execute(sqlquery):
        tm_actives[affil] = cnt

    sqlquery = ('select affil,count(*) as c from scholarship_info '
                'inner join tm_researcher_profile on tm_researcher_profile.scholarship_info_id=scholarship_info.id '
                'where scholarship_info.status=true '
                'group by affil;')

    labels = []
    inactive_data = []
    active_data = []
    activecolors = []
    inactivecolors = []
    for affil, cnt in conn.execute(sqlquery):
        totals[affil] = cnt

    sorted_active_data = sorted([(k,v) for k,v in totals.items()],
                                key=lambda x: x[1], reverse=True)
    for k,v in sorted_active_data:
        if k in tm_actives:
            inactive_data.append(totals[k]-tm_actives[k])
            active_data.append(tm_actives[k])
            activecolors.append('rgb(199,0,57)')
            inactivecolors.append('rgb(100,116,164)')
            labels.append(k)

    return JsonResponse({'actives': active_data,
                         'inactives': inactive_data,
                         'activecolors': activecolors,
                         'inactivecolors': inactivecolors,
                         'labels': labels})


def get_tm_researchers_graph_data(request):
    sqlquery = ('select authors.id from authors '
                'inner join scholarship_info on authors.scholarship_info_id=scholarship_info.id '
                'where scholarship_info.status=true')

    scholars = set()
    for row in conn.execute(sqlquery):
        scholars.add(row[0])


    sqlquery = ('select authors.id, abstracts.id from scholarship_info '
                'inner join tm_researcher_profile on tm_researcher_profile.scholarship_info_id=scholarship_info.id '
                'inner join authors on scholarship_info.id=authors.scholarship_info_id '
                'inner join abstract_has_author on abstract_has_author.author_id=authors.id '
                'inner join abstracts on abstract_has_author.abstract_id=abstracts.id '
                'where scholarship_info.status=true '
                )

    tm_abstracts = set()
    tm_authors = set()
    for author_id, abstract_id in conn.execute(sqlquery):
        tm_abstracts.add(abstract_id)
        tm_authors.add(author_id)

    sqlquery = ('select authors.id,authors.first_name, authors.last_name,abstracts.id from abstracts '
                'inner join abstract_has_author on abstract_has_author.abstract_id=abstracts.id '
                'inner join authors on abstract_has_author.author_id=authors.id;'
                )
    abstracts = {}
    for author_id, first_name, last_name, abstract_id in conn.execute(sqlquery):
        if abstract_id in tm_abstracts:
            if abstract_id in abstracts:
                abstracts[abstract_id].append((author_id, '{} {}'.format(first_name, last_name)))
            else:
                abstracts[abstract_id] = [(author_id, '{} {}'.format(first_name, last_name))]

    edges = {}
    nodes = {}
    n = 0
    for abstract_id, authors in abstracts.items():
        n += 1
        first_author_id = authors[0][0]
        if first_author_id not in nodes:
            nodes[first_author_id] = {'name': authors[0][1], 'papers': 1}
        else:
            nodes[first_author_id]['papers'] += 1
        if first_author_id not in edges:
            edges[first_author_id] = {}
        if len(authors) > 1:
            for author in authors[1:]:
                if author[0] not in nodes:
                    nodes[author[0]] = {'name': author[1], 'papers': 1}
                else:
                    nodes[author[0]]['papers'] += 1
                if author[0] in edges and edges[author[0]].get(first_author_id, None):
                    continue
                else:
                    edges[first_author_id][author[0]] = edges[first_author_id].get(author[0], 0) + 1

    nodes_data = []
    edges_data = []
    flt_nodes = set()
    for n in nodes:
        if nodes[n]['papers'] > 2:
            flt_nodes.add(n)
            if n in tm_authors:
                color = '#ff9900'
            elif n in scholars:
                color = '#33cc33'
            else:
                color = '#0099ff'
            nodes_data.append({
                'id': n,
                'value': nodes[n]['papers'],
                'label': nodes[n]['name'],
                'color': color
            })
    for _from in list(flt_nodes):
        for _to in edges.get(_from, []):
            if edges[_from][_to] >= 1:
                edges_data.append({
                    'from': _from,
                    'to': _to,
                    'value': edges[_from][_to],
                    'title': '{} publications'.format(edges[_from][_to])
                })
            if _to not in flt_nodes:
                if _to in tm_authors:
                    color = '#ff9900'
                elif n in scholars:
                    color = '#33cc33'
                else:
                    color = '#0099ff'
                nodes_data.append({
                    'id': _to,
                    'value': nodes[_to]['papers'],
                    'label': nodes[_to]['name'],
                    'color': color
                })
                flt_nodes.add(_to)


    return JsonResponse({'edges': edges_data, 'nodes': nodes_data})


def show_scholar_dashboard(request):
    return render(request, template_name="analytics/scholar-dashboard.html",
                  context={'board': 'scholar'})


def show_tm_dashboard(request):
    return render(request, template_name="analytics/tm-dashboard.html",
                  context={'board': 'tm'})
