from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from keywordsdw import ResearchField
from py2neo import Graph, Relationship, NodeMatcher, Node
from datetime import datetime

graph = Graph(host='localhost', password='_genius01_', scheme='bolt')
engine = create_engine('postgresql+psycopg2://postgres:_genius01_@localhost:5434/keywordsdw')
session = Session(engine)
matcher = NodeMatcher(graph)

graph.delete_all()

def from_research_field():
    num_abs = 0
    for field in session.query(ResearchField):
        print('Working on {}'.format(field.name))
        fNode = Node('Field', name=field.name, abbr=field.abbr, fieldId=field.id)
        graph.create(fNode)
        for ab in field.abstracts:
            _abstract = matcher.match('Abstract', scopus_id=ab.scopus_id).first()
            if _abstract:
                # print('\tabstract exists..skipped')
                continue
            else:
                num_abs += 1
                if num_abs % 100 == 0:
                    print('{}...'.format(num_abs))

                pubdate = datetime.strftime(ab.pub_date, '%Y-%m-%d')
                abNode = Node('Abstract', title_en=ab.title_en, scopus_id=ab.scopus_id,
                                pubdate=pubdate, cited=ab.cited)
                graph.create(abNode)
                graph.create(Relationship(abNode, 'IN', fNode))
                for author in ab.authors:
                    # print('\t\tAdding authors {} {}'.format(author.first_name, author.last_name))
                    _author = matcher.match('Author', scopus_id=author.scopus_id).first()
                    if _author:
                        # print('\t\t\texists..skipped')
                        continue
                    else:
                        auNode = Node('Author', first_name=author.first_name,
                                    last_name=author.last_name, scopus_id=author.scopus_id)
                        graph.create(auNode)
                        graph.create(Relationship(auNode, 'AUTHORED', abNode))
                        # print('\t\tAdding affiliation..')
                        for af in author.affiliations:
                            _affil = matcher.match('Affiliation', scopus_id=af.affiliation.scopus_id)
                            if _affil:
                                # print('\t\t{} exists..'.format(af.affiliation.name))
                                continue
                            else:
                                afNode = Node('Affiliation', name=af.affiliation.name,
                                                scopus_id=af.affiliation.scopus_id,
                                                country=af.affiliation.country,
                                                city=af.affiliation.city)
                                graph.create(afNode)
                                _affil = afNode
                            graph.create(Relationship(auNode, 'AFFILIATE', _affil))


if __name__ == '__main__':
    from_research_field()
