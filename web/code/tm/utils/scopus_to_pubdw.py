'''Transfers data from the scopuspub db to the keyword data warehouse.
'''

from itertools import islice
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from pubdw import (Author, AuthorList, Abstract, FieldPub, Field,
                   Affiliation, Keyword, NounChunk, KeywordList,
                   NounChunkWordList, NounChunkList)
import spacy
from spacy.lang.en.stop_words import STOP_WORDS

nlp = spacy.load('en_core_web_sm')

PubBase = automap_base()
pub_engine = create_engine('postgresql+psycopg2://likit:password@localhost/scopuspubs')
dw_engine = create_engine('postgresql+psycopg2://postgres:_genius01_@localhost:5434/pubdw')

PubBase.prepare(pub_engine, reflect=True)
pub_session = Session(pub_engine)
dw_session = Session(dw_engine)

Pub = PubBase.classes.pubs

def add_affiliation(affiliation):
    city = affiliation['affiliation-city']
    name = affiliation['affilname']
    affil_id = affiliation['@id']
    country = affiliation['affiliation-country']
    affil_ = dw_session.query(Affiliation).filter(Affiliation.scopus_id==affil_id).first()
    if affil_:
        # print('\t\t', name, affil_id, 'exists..skipped.')
        pass
    else:
        new_affil = Affiliation(
                        city=city,
                        country=country,
                        name=name,
                        scopus_id=affil_id)
        dw_session.add(new_affil)
        dw_session.commit()
        # print('\t\t', city, country, name, affil_id, 'added to the db..skipped.')


def add_author(au, pubyear):
    first_name = au.get('ce:given-name')
    last_name = au.get('ce:surname')
    auid = au.get('@auid')
    if 'affiliation' in au:
        if isinstance(au['affiliation'], dict):
            affil_id = au['affiliation'].get('@id', None)
            affil_ = dw_session.query(Affiliation).filter(Affiliation.scopus_id==affil_id).first()
        elif isinstance(au['affiliation'], list):
            for f in au['affiliation']:
                affil_id = f.get('@id', None)
                affil_ = dw_session.query(Affiliation).filter(Affiliation.scopus_id==affil_id).first()
    else:
        affil_ = None

    author_ = dw_session.query(Author).filter(Author.scopus_id==auid).first()
    if author_:
        # print('\t\tAuthor exists!')
        return author_, affil_
    else:
        new_author = Author(
            first_name=first_name,
            last_name=last_name,
            scopus_id=auid,
        )
        dw_session.add(new_author)
        dw_session.commit()
        # print('\t\tNew author!', first_name, last_name)
        return new_author, affil_


def add_subject_area(subj):
    name = subj.get('$')
    scopus_id = subj.get('@code')
    abbr = subj.get('@abbrev')
    field_ = dw_session.query(Field).filter(Field.scopus_id==scopus_id).first()
    if field_ is not None:
        return field_
    else:
        new_field = Field(
            fullname=name,
            abbr=abbr,
            scopus_id=scopus_id,
        )
        dw_session.add(new_field)
        dw_session.commit()
        return new_field


for n, pub in enumerate(pub_session.query(Pub)):
    # print('Pub #{}, ID={}'.format(n, pub.scopus_id))
    if 'abstracts-retrieval-response' not in pub.data:
        print('\t\tPub #{}, ID={} No abstract data found..skipped.'.format(n, pub.scopus_id))
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

    subj_areas = []
    if 'subject-areas' in data:
        if 'subject-area' in data['subject-areas']:
            for subj in data['subject-areas']['subject-area']:
                subj_areas.append(add_subject_area(subj))

    '''
    nounchunks = []
    if 'authkeyword' in data:
        if 'author-keyword' in data['authkeyword']:
            for ak in data['authkeywords']['author-keyword']:
                nounchunks.append((ak['$'].lower()), True)
    '''

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
        abstract_ = dw_session.query(Abstract).filter(Abstract.scopus_id==scopus_id).first()
        keywords = []
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
                                    pub_date=pubdate,
                                    cited=cited,
                                )
            dw_session.add(new_abstract)
            dw_session.commit()
            abstract_ = new_abstract
            '''
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
                    nounchunks.append((str(nc).lower(), False))
            '''
    field_pubs = []
    for subj in subj_areas:
        field_pub = FieldPub(field=subj, abstract=abstract_)
        dw_session.add(field_pub)
        field_pubs.append(field_pub)
    dw_session.commit()

    if 'authors' in data:
        authors = data['authors']
        if 'author' in authors:
            for au in authors['author']:
                a, f = add_author(au, pubyear)
                for field_pub in field_pubs:
                    al = AuthorList(author=a, affil=f, field_pub=field_pub)
                    dw_session.add(al)
            dw_session.commit()

    '''
    for kw in keywords:
        word = dw_session.query(Keyword).filter(Keyword.word_en==kw).first()
        if word:
            word.count += 1
            dw_session.add(word)
            dw_session.commit()
        else:
            kw_th = ''
            word = Keyword(
                word_en=kw,
                word_th=kw_th,
                count=1,
            )
            dw_session.add(word)
        for field_pub in field_pubs:
            word_list = KeywordList(keyword=word, field_pub=field_pub)
            dw_session.add(word_list)
        dw_session.commit()

    for nc in nounchunks:
        chunk = dw_session.query(NounChunk).filter(NounChunk.chunk_en==nc[0]).first()
        for field_pub in field_pubs:
            if chunk is not None:
                chunk_list = NounChunkList(noun_chunk=chunk, field_pub=field_pub)
            else:
                nc_th = ''
                chunk = NounChunk(chunk_en=nc[0], chunk_th=nc_th, is_auth_keywords=nc[1])
                chunk_list = NounChunkList(noun_chunk=chunk, field_pub=field_pub)
                dw_session.add(chunk)
                doc = nlp(nc[0])
                for token in doc:
                    token = str(token).lower()
                    word = dw_session.query(Keyword).filter(Keyword.word_en==token).first()
                    if word is not None:
                        nounchunk_world_list = NounChunkWordList(noun_chunk=chunk,
                                                                 keyword=word)
                        dw_session.add(nounchunk_world_list)
            dw_session.add(chunk_list)
    dw_session.commit()
    '''
    if n%100==0:
        print('{}...'.format(n))
