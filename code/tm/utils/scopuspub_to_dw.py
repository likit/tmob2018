'''Transfers data from the scopuspub db to the keyword data warehouse.
'''

from googletrans import Translator
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from keywordsdw import session as kw_session
from keywordsdw import Keyword, Abstract

translator = Translator()

PubBase = automap_base()
pub_engine = create_engine('postgresql+psycopg2://likit:password@localhost/scopuspubs')

PubBase.prepare(pub_engine, reflect=True)
pub_session = Session(pub_engine)

print(PubBase.classes.keys())

Pub = PubBase.classes.pubs

for pub in pub_session.query(Pub).limit(5):
    if 'abstracts-retrieval-response' not in pub.data:
        continue
    else:
        data = pub.data['abstracts-retrieval-response']
    if 'coredata' in data:
        coredata = data['coredata']
    if 'affiliation' in data:
        affiliation = data['affiliation']
    break

print(affiliation.keys())