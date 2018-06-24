'''Transfers data from the scopuspub db to the keyword data warehouse.
'''

from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

Base = automap_base()
pub_engine = create_engine('postgresql+psycopg2://likit:password@localhost/scopuspubs')

Base.prepare(pub_engine, reflect=True)
session = Session(pub_engine)

print(Base.classes.keys())

Pub = Base.classes.pubs

for pub in session.query(Pub).limit(5):
    print(pub.scopus_id, pub.pub_date)