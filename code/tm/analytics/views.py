from django.shortcuts import render
from sqlalchemy import MetaData, create_engine
from collections import namedtuple

meta = MetaData()
engine = create_engine('postgresql+psycopg2://postgres:_genius01_@postgres_db/keywordsdw')
conn = engine.connect()

Researcher = namedtuple('Researcher', ['firstname', 'lastname',
                            'word_en', 'count', 'total_abstracts' ,'sc'])

# Create your views here.
def res_list(request):
    search_term = request.GET.get('q')
    res_list = []
    if search_term:
        results = conn.execute("select distinct first_name, last_name, word_en, count "
                                "from keywords where to_tsvector(word_en) @@ to_tsquery('%s')"
                                " order by count desc" % search_term).fetchall()
        if results:
            for rec in results:
                query = ("select id,scholarship_info_id from authors where lower(first_name)=lower('%s') "
                            "and lower(last_name)=lower('%s')")
                _author_id, _sc_id = conn.execute(query % (rec[0], rec[1])).fetchone()
                if _author_id:
                    query = ('select count(*) from abstracts inner join abstract_has_author '
                                'on abstract_has_author.abstract_id=abstracts.id '
                                'inner join authors on authors.id=abstract_has_author.author_id where authors.id=%d;')
                    total_abstracts = conn.execute(query % _author_id).scalar()
                    if _sc_id:
                        sc = True
                    else:
                        sc = False
                    res_list.append(Researcher(rec[0], rec[1], rec[2], rec[3], total_abstracts, sc))
    return render(request, template_name='analytics/res_list.html',
            context={'search_term': search_term, 'results': res_list})
