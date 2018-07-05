# -*- coding: utf-8 -*-
from django.shortcuts import render
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

                query = ("select id,scholarship_info_id from authors where lower(first_name)=lower('%s') "
                            "and lower(last_name)=lower('%s')")
                _author = conn.execute(query % (rec[1], rec[2])).fetchone()
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

        query = ("select * from abstracts inner join abstract_has_author "
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
    if first_name and last_name:
        author = conn.execute("select * from authors where "
                      "lower(first_name)=lower('%s') and lower(last_name)=lower('%s')"
                      % (first_name, last_name)).fetchone()
        if author:
            keywords = conn.execute("select word_en,count from keywords where author_scopus_id='%s'"
                                    % author.scopus_id).fetchall()
            query = ("select * from abstracts inner join abstract_has_author "
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
                      'fields': fields, 'affils': affiliations, 'keywords': keywords})
    return render(request, template_name="analytics/profile_by_name.html",
                  context={})
