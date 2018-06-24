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
    author_ = kw_session.query(Author).filter(Author.first_name==first_name,
                                Author.last_name==last_name).first()
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
        return new_author


for pub in pub_session.query(Pub).limit(5):
    if 'abstracts-retrieval-response' not in pub.data:
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
        print(coredata.keys())
        break
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
        if abstract_ is None:
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
                nounchunks.append(nc)
    if 'authors' in data:
        author_list = []
        authors = data['authors']
        if 'author' in authors:
            for au in authors['author']:
                author_list.append(add_author(au, pubyear))

    for kw in keywords:
        kw_ = kw_session.query(Keyword).filter(Keyword.word_en==kw).first()
        if kw_:
            for au in author_list:
                wordobj = kw_session.query(Keyword)\
                            .filter(Keyword.word_en==kw,
                                    Keyword.first_name==au.first_name,
                                    Keyword.last_name==au.last_name,
                                    Keyword.scopus_id==au.scopus_id).first()
                if wordobj:
                    wordobj.count += 1
                    kw_session.add(wordobj)
                    kw_session.commit()
        else:
            kw_th = translator.translate(kw, dest='th').text
            for au in author_list:
                new_keyword = Keyword(
                    word_en=kw,
                    word_th=kw_th,
                    count=1,
                    first_name=au.first_name,
                    last_name=au.last_name,
                    scopus_id=au.scopus_id,
                    from_keyword=False,
                    abstract=abstract_,
                )
                kw_session.add(new_keyword)
            kw_session.commit()
# title_th = translator.translate(title, dest='th').text
