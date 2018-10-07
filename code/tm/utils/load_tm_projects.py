from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from keywordsdw import TMResearchProject, TMResearcherProfile, Base


tmengine = create_engine('mysql+mysqlconnector://root:_genius01_@localhost/talent3')
scengine = create_engine('postgresql+psycopg2://postgres:_genius01_@localhost:5434/keywordsdw')

tmconn = tmengine.connect()
scconn = scengine.connect()

Session = sessionmaker(bind=tmengine)
tmsession = Session()
Session = sessionmaker(bind=scengine)
scsession = Session()

Base.metadata.create_all(scengine)

import pandas as pd

# in the future, all researchers could be loaded then the isRegistered column keeps updated
df = pd.read_sql_query('select * from researcher_projects', con=tmconn)

for ix, row in df.iterrows():
    researcher_id = row['researcher_profile_id']
    researcher = scsession.query(TMResearcherProfile).filter(
                    TMResearcherProfile.profile_id==researcher_id).first()
    if researcher:
        project = TMResearchProject(
            year=int(row['year_th']-543),
            title=row['project_title'],
            is_leader=row['isProjectLeader'],
        )
        researcher.projects.append(project)
        scsession.add(project)
        scsession.commit()
