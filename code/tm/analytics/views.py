from django.shortcuts import render
from sqlalchemy import MetaData, create_engine
from collections import namedtuple

meta = MetaData()
engine = create_engine('postgresql+psycopg2://postgres:_genius01_@postgres_db/keywordsdw')
conn = engine.connect()

Researcher = namedtuple('Researcher', ['firstname', 'lastname',
                                        'word_en', 'count', 'affiliation',
                                        'fields' ,'sc'])

# Create your views here.
def res_list(request):
    search_term = request.GET.get('q')
    res_list = []
    nounchunks = []
    if search_term:
        tsquery = ' & '.join(search_term.split(' '))
        tsquery_word = ' | '.join(search_term.split(' '))
        query = ("select id, chunk_en from noun_chunks where "
                    "to_tsvector(chunk_en) @@ to_tsquery('%s');")
        nounchunks += conn.execute(query % tsquery).fetchall()
        results = conn.execute("select distinct keywords.id, first_name, last_name, word_en, count, affils.name"
                                " from keywords inner join affils on keywords.affil_scopus_id=affils.scopus_id "
                                "where to_tsvector(word_en) @@ to_tsquery('%s')"
                                " order by count desc" % tsquery_word).fetchall()
        if results:
            fields = set()
            for rec in results:
                query = ('select research_fields.abbr from abstracts inner join abstract_has_keywords '
                            'on abstract_has_keywords.abstract_id=abstracts.id '
                            'inner join keywords on keywords.id=abstract_has_keywords.keyword_id '
                            'inner join field_has_abstract on field_has_abstract.abstract_id=abstracts.id '
                            'inner join research_fields on field_has_abstract.field_id=research_fields.id '
                            'where keywords.id=%d;')
                for field in conn.execute(query % int(rec[0])).fetchall():
                    fields.add(field[0])

                query = ("select id,scholarship_info_id from authors where lower(first_name)=lower('%s') "
                            "and lower(last_name)=lower('%s')")
                _author_id, _sc_id = conn.execute(query % (rec[1], rec[2])).fetchone()
                if _author_id:
                    if _sc_id:
                        sc = True
                    else:
                        sc = False
                    res_list.append(Researcher(rec[1], rec[2], rec[3], rec[4], rec[5], fields, sc))

    return render(request, template_name='analytics/res_list.html',
            context={'search_term': search_term, 'results': res_list, 'nounchunks': nounchunks})

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