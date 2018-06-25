'''Transfers data from the scopuspub db to the keyword data warehouse.
'''

import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from googletrans import Translator
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from keywordsdw import session as kw_session
from keywordsdw import Keyword, Abstract, Author, NounChunk, Affiliation, AffiliationHistory, ResearchField

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
        print('\t\t', name, affil_id, 'exists..skipped.')
    else:
        new_affil = Affiliation(
                        city=city,
                        country=country,
                        name=name,
                        scopus_id=affil_id)
        kw_session.add(new_affil)
        kw_session.commit()
        print('\t\t', city, country, name, affil_id, 'added to the db..skipped.')


def add_author(au, pubyear):
    first_name = au.get('ce:given-name')
    last_name = au.get('ce:surname')
    auid = au.get('@auid')
    affil_list = []
    if 'affiliation' in au:
        if isinstance(au['affiliation'], dict):
            affil_id = au['affiliation'].get('@id', None)
            affil_ = kw_session.query(Affiliation).filter(Affiliation.scopus_id==affil_id).first()
            affil_list.append(affil_)
        elif isinstance(au['affiliation'], list):
            for f in au['affiliation']:
                affil_id = f.get('@id', None)
                affil_ = kw_session.query(Affiliation).filter(Affiliation.scopus_id==affil_id).first()
                affil_list.append(affil_)

    author_ = kw_session.query(Author).filter(Author.scopus_id==auid).first()
    if author_:
        print('\t\tAuthor exists!')
        for a in affil_list:
            history_ = kw_session.query(AffiliationHistory).filter(
                                    AffiliationHistory.affiliation==a,
                                    AffiliationHistory.author==author_,
                                    AffiliationHistory.year==pubyear,
                                ).first()
            if history_ is None:
                new_history = AffiliationHistory(
                    year=pubyear,
                    affiliation=a,
                    author=author_
                )
                kw_session.add(new_history)
                kw_session.commit()
        return author_, affil_list
    else:
        new_author = Author(
            first_name=first_name,
            last_name=last_name,
            scopus_id=auid,
        )
        kw_session.add(new_author)
        for a in affil_list:
            new_affil_history = AffiliationHistory(
                                    year=pubyear,
                                    affiliation=a,
                                    author=new_author)
            kw_session.add(new_affil_history)
        kw_session.commit()
        print('\t\tNew author!', first_name, last_name)
        return new_author, affil_list


def add_subject_area(subj):
    name = subj.get('$')
    scopus_id = subj.get('@code')
    abbr = subj.get('@abbrev')
    field_ = kw_session.query(ResearchField).filter(ResearchField.scopus_id==scopus_id).first()
    if field_ is not None:
        return field_
    else:
        new_field = ResearchField(
            name=name,
            abbr=abbr,
            scopus_id=scopus_id,
            abstracts=[],
        )
        kw_session.add(new_field)
        kw_session.commit()
        return new_field


for n, pub in enumerate(pub_session.query(Pub)):
    print('Pub #{}, ID={}'.format(n, pub.scopus_id))
    if n < 414:
        continue
    if 'abstracts-retrieval-response' not in pub.data:
        print('\t\tNo abstract data found..skipped.')
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
    nounchunks = []
    if 'authkeyword' in data:
        if 'author-keyword' in data['authkeyword']:
            for ak in data['authkeywords']['author-keyword']:
                nounchunks.append(ak['$'].lower())

    subj_areas = []
    if 'subject-areas' in data:
        if 'subject-area' in data['subject-areas']:
            for subj in data['subject-areas']['subject-area']:
                subj_areas.append(add_subject_area(subj))

    if 'coredata' in data:
        coredata = data['coredata']
        if 'prism:coverDate' in coredata:
            pubdate = coredata['prism:coverDate']
            pubyear = int(pubdate.split('-')[0])
        else:
            pubyear = None
        title_en = coredata.get('dc:title')
        title_th = ''
        abstract_en = coredata.get('dc:description')
        abstract_th = ''
        doi = coredata.get('prism:doi')
        cited = int(coredata.get('citedby_count', 0))
        scopus_id = coredata.get('dc:identifier').lstrip('SCOPUS_ID:')
        abstract_ = kw_session.query(Abstract).filter(Abstract.scopus_id==scopus_id).first()
        if abstract_ is not None:
            print('\t\tPublication #SCOPUS_ID={} exists!'.format(abstract_.scopus_id))
            continue
        else:
            new_abstract = Abstract(
                                    doi=doi,
                                    scopus_id=scopus_id,
                                    abstract_en=abstract_en,
                                    abstract_th=abstract_th,
                                    title_en=title_en,
                                    title_th=title_th,
                                    authors=[],
                                    pub_date=pubdate,
                                    cited=cited,
                                )
            kw_session.add(new_abstract)
            kw_session.commit()
            abstract_ = new_abstract
        for subj in subj_areas:
            subj.abstracts.append(abstract_)
            kw_session.add(subj)
        kw_session.commit()
        keywords = []
        for text in [title_en, abstract_en]:
            # some abstracts do not have title or abstract text
            if title_en is None:
                continue
            elif abstract_en is None:
                continue
            doc = nlp(text)
            for token in doc:
                word = str(token).lower()
                if word not in STOP_WORDS and word.isalpha() and len(word) > 1:
                    keywords.append(word)
            for nc in list(doc.noun_chunks):
                nounchunks.append(str(nc).lower())
    if 'authors' in data:
        author_list = []
        affil_id_list = []
        authors = data['authors']
        if 'author' in authors:
            for au in authors['author']:
                a, f = add_author(au, pubyear)
                abstract_.authors.append(a)
                author_list.append(a)
                affil_id_list.append(f)
            kw_session.add(abstract_)
            kw_session.commit()

    for kw in keywords:
        kw_ = kw_session.query(Keyword).filter(Keyword.word_en==kw).first()
        if kw_:
            for i in range(len(author_list)):
                au = author_list[i]
                for afid in affil_id_list[i]:
                    wordobj = kw_session.query(Keyword)\
                                .filter(Keyword.word_en==kw,
                                    Keyword.first_name==au.first_name,
                                    Keyword.last_name==au.last_name,
                                    Keyword.author_scopus_id==au.scopus_id,
                                    Keyword.affil_scopus_id==afid.scopus_id).first()
                if wordobj:
                    wordobj.count += 1
                    wordobj.abstracts.append(abstract_)
                    kw_session.add(wordobj)
                    kw_session.commit()
        else:
            kw_th = ''
            for i in range(len(author_list)):
                au = author_list[i]
                for afid in affil_id_list[i]:
                    new_keyword = Keyword(
                        word_en=kw,
                        word_th=kw_th,
                        count=1,
                        first_name=au.first_name,
                        last_name=au.last_name,
                        author_scopus_id=au.scopus_id,
                        affil_scopus_id=afid.scopus_id,
                        abstracts=[abstract_],
                    )
                kw_session.add(new_keyword)
            kw_session.commit()
    for nc in nounchunks:
        nc_ = kw_session.query(NounChunk).filter(NounChunk.chunk_en==nc).first()
        if nc_ is not None:
            nc_.abstracts.append(abstract_)  # nc exists, add abstract
            kw_session.add(nc_)
            kw_session.commit()
        else:
            nc_th = ''
            new_nc = NounChunk(chunk_en=nc,
                                chunk_th=nc_th,
                                abstracts=[abstract_],
                                keywords=[],
                                )
            doc = nlp(nc)
            for token in doc:
                token = str(token).lower()
                new_nc.keywords += kw_session.query(Keyword).filter(Keyword.word_en==token).all()
            kw_session.add(new_nc)
            kw_session.commit()