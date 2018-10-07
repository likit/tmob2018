from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from keywordsdw import ScholarshipInfo, TMResearcherProfile


tmengine = create_engine('mysql+mysqlconnector://root:_genius01_@localhost/talent3')
scengine = create_engine('postgresql+psycopg2://postgres:_genius01_@localhost:5434/keywordsdw')

tmconn = tmengine.connect()
scconn = scengine.connect()

Session = sessionmaker(bind=tmengine)
tmsession = Session()
Session = sessionmaker(bind=scengine)
scsession = Session()

import pandas as pd

# in the future, all researchers could be loaded then the isRegistered column keeps updated
df = pd.read_sql_query('select * from researcher_profiles where isRegistered=true', con=tmconn)

for ix, row in df.iterrows():
    # print(row['id'], row['email'], row['firstname_en'], row['lastname_en'], row['firstname_th'], row['lastname_th'], row['gender'], row['birthday'],row['isRegistered'])
    pf = scsession.query(TMResearcherProfile).filter(
        func.lower(TMResearcherProfile.first_name_en)==row['firstname_en'].lower(),
        func.lower(TMResearcherProfile.last_name_en)==row['lastname_en'].lower()).first()
    if pf:
        print('Profile with ID:{} already exists!'.format(row['id']))
        continue

    sc = scsession.query(ScholarshipInfo).filter(
        func.lower(ScholarshipInfo.first_name_en)==row['firstname_en'].lower(),
        func.lower(ScholarshipInfo.last_name_en)==row['lastname_en'].lower()).first()
    if sc:
        scholarship_info_id = sc.id
    else:
        scholarship_info_id = None

    profile = TMResearcherProfile(
        scholarship_info_id=scholarship_info_id,
        first_name_en=row['firstname_en'],
        last_name_en=row['lastname_en'],
        first_name_th=row['firstname_th'],
        last_name_th=row['lastname_th'],
        gender=row['gender'],
        dob=row['birthday'],
        email=row['email'],
        isRegistered=row['isRegistered'],
        profile_id=row['id']
    )
    scsession.add(profile)
    scsession.commit()

