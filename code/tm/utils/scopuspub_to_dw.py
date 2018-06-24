'''Transfers data from the scopuspub db to the keyword data warehouse.
'''

import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from googletrans import Translator
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from keywordsdw import session as kw_session
from keywordsdw import Keyword, Abstract, Author, NounChunk, Affiliation, AffiliationHistory

translator = Translator()
nlp = spacy.load('en_core_web_sm')

PubBase = automap_base()
pub_engine = create_engine('postgresql+psycopg2://likit:password@localhost/scopuspubs')

PubBase.prepare(pub_engine, reflect=True)
pub_session = Session(pub_engine)

Pub = PubBase.classes.pubs

def add_affiliation(affiliation):
    city = affiliation['affiliation-city']
    name = affiliation['affilname']
    affil_id = affiliation['@id']
    country = affiliation['affiliation-country']
    affil_ = kw_session.query(Affiliation).filter(Affiliation.scopus_id==affil_id).first()
    if affil_:
        print(name, affil_id, 'exists..')
    else:
        new_affil = Affiliation(
                        city=city,
                        country=country,
                        name=name,
                        scopus_id=affil_id)
        kw_session.add(new_affil)
        kw_session.commit()
        print(city, country, name, affil_id, 'added to the db..')


def add_author(au, pubyear):
    first_name = au.get('ce:given-name')
    last_name = au.get('ce:surname')
    auid = au.get('@auid')
    if 'affiliation' in au:
        affil_id = au['affiliation'].get('@id', None)
        affil_ = kw_session.query(Affiliation).filter(Affiliation.scopus_id==affil_id).first()
    else:
        affil_id = None
    author_ = kw_session.query(Author).filter(Author.scopus_id==scopus_id).first()
    if author_:
        print('Author exists!')
        return author_
    else:
        new_author = Author(
            first_name=first_name,
            last_name=last_name,
            scopus_id=auid,
        )
        kw_session.add(new_author)
        new_affil_history = AffiliationHistory(
                                    year=pubyear,
                                    affiliation=affil_,
                                    author=new_author)
        kw_session.add(new_affil_history)
        kw_session.commit()
        print('New author!', first_name, last_name)
        return new_author, affil_id


for pub in pub_session.query(Pub).limit(5):
    print('Pub ID: {}'.format(pub.scopus_id))
    if 'abstracts-retrieval-response' not in pub.data:
        print('\tNo abstract data found..')
        continue
    else:
        data = pub.data['abstracts-retrieval-response']
    if 'affiliation' in data:
        affiliation = data['affiliation']
        if isinstance(affiliation, dict):
            add_affiliation(affiliation)
        elif isinstance(affiliation, list):
            for af in affiliation:
                add_affiliation(af)
    if 'coredata' in data:
        coredata = data['coredata']
        if 'prism:coverDate' in coredata:
            pubdate = coredata['prism:coverDate']
            pubyear = int(pubdate.split('-')[0])
        else:
            pubyear = None
        title_en = coredata.get('dc:title')
        title_th = translator.translate(title_en, dest='th').text
        abstract_en = coredata.get('dc:description')
        abstract_th = translator.translate(abstract_en, dest='th').text
        doi = coredata.get('prism:doi')
        cited = int(coredata.get('citedby_count', 0))
        scopus_id = coredata.get('dc:identifier').lstrip('SCOPUS_ID:')
        abstract_ = kw_session.query(Abstract).filter(Abstract.scopus_id==scopus_id).first()
        if abstract_ is not None:
            print('\tPublication #SCOPUS_ID={} exists!'.format(abstract_.scopus_id))
            continue
        else:
            new_abstract = Abstract(
                                    doi=doi,
                                    scopus_id=scopus_id,
                                    abstract_en=abstract_en,
                                    abstract_th=abstract_th,
                                    title_en=title_en,
                                    title_th=title_th,
                                    pub_date=pubdate,
                                    cited=cited,
                                )
            kw_session.add(new_abstract)
            kw_session.commit()
            abstract_ = new_abstract
        keywords = []
        nounchunks = []
        for text in [title_en, abstract_en]:
            doc = nlp(text)
            for token in doc:
                word = str(token).lower()
                if word not in STOP_WORDS and word.isalpha() and len(word) > 1:
                    keywords.append(word)
            for nc in list(doc.noun_chunks):
                nounchunks.append(str(nc))
    if 'authors' in data:
        author_list = []
        affil_id_list = []
        authors = data['authors']
        if 'author' in authors:
            for au in authors['author']:
                a, f = add_author(au, pubyear)
                author_list.append(a)
                affil_id_list.append(f)

    for kw in keywords:
        kw_ = kw_session.query(Keyword).filter(Keyword.word_en==kw).first()
        if kw_:
            for i in range(len(author_list)):
                au = author_list[i]
                afid = affil_id_list[i]
                wordobj = kw_session.query(Keyword)\
                            .filter(Keyword.word_en==kw,
                                    Keyword.first_name==au.first_name,
                                    Keyword.last_name==au.last_name,
                                    Keyword.author_scopus_id==au.scopus_id,
                                    Keyword.affil_scopus_id==afid).first()
                if wordobj:
                    wordobj.count += 1
                    kw_session.add(wordobj)
                    kw_session.commit()
        else:
            kw_th = translator.translate(kw, dest='th').text
            for i in range(len(author_list)):
                au = author_list[i]
                afid = affil_id_list[i]
                new_keyword = Keyword(
                    word_en=kw,
                    word_th=kw_th,
                    count=1,
                    first_name=au.first_name,
                    last_name=au.last_name,
                    author_scopus_id=au.scopus_id,
                    affil_scopus_id=afid,
                    from_keyword=False,
                    abstract=abstract_,
                )
                kw_session.add(new_keyword)
            kw_session.commit()
    for nc in nounchunks:
        nc_ = kw_session.query(NounChunk).filter(NounChunk.chunk_en==nc).first()
        if nc_ is None:
            nc_th = translator.translate(nc, dest='th').text
            new_nc = NounChunk(chunk_en=nc,
                                chunk_th=nc_th,
                                abstract=abstract_,
                                keywords=[],
                                )
            doc = nlp(nc)
            for token in doc:
                token = str(token).lower()
                new_nc.keywords += kw_session.query(Keyword).filter(Keyword.word_en==token).all()
            kw_session.add(new_nc)
            kw_session.commit()
# title_th = translator.translate(title, dest='th').text
