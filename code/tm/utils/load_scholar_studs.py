import sys
import pandas as pd
from sqlalchemy import func
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from keywordsdw import ScholarshipInfo, Author

def load_stud_to_db2(inputfile, sheetname):
    df = pd.read_excel(inputfile, sheet_name=sheetname)
    for idx, row in df.iterrows():
        firstname_th = row['FirstNameTh'] if not pd.isna(row['FirstNameTh']) else ''
        lastname_th = row['LastNameTh'] if not pd.isna(row['LastNameTh']) else ''
        affil = row['Department'].lower() if not pd.isna(row['Department']) else ''
        person = session.query(ScholarshipInfo).filter(id==2975).first()
        person = session.query(ScholarshipInfo).filter(
                    ScholarshipInfo.last_name_th==lastname_th,
                    ScholarshipInfo.first_name_th==firstname_th).first()
        person.affil = affil
        # print(person.first_name_th, person.last_name_th, person.affil, person.degree)
        session.add(person)
    session.commit()


def load_stud_to_db(inputfile, sheetname):
    df = pd.read_excel(inputfile, sheet_name=sheetname)
    total_persons = 0
    for idx, row in df.iterrows():
        contact = row['Email'].replace(' ', '') if not pd.isna(row['Email']) else ''
        firstname_en = row['FirstNameEn'] if not pd.isna(row['FirstNameEn']) else ''
        lastname_en = row['LastNameEn'] if not pd.isna(row['LastNameEn']) else ''
        firstname_th = row['FirstNameTh'] if not pd.isna(row['FirstNameTh']) else ''
        lastname_th = row['LastNameTh'] if not pd.isna(row['LastNameTh']) else ''
        affil = row['Department'].lower() if not pd.isna(row['Department']) else ''
        country = row['Country'].lower() if not pd.isna(row['Country']) else ''
        field_of_study = row['Major'].lower() if not pd.isna(row['Major']) else ''
        specialty = row['Specialty'].lower() if not pd.isna(row['Specialty']) else ''
        status = False
        degree_code = row['DegreeId'] if not pd.isna(row['DegreeId']) else ''
        new_person = Person(
            first_name_en=firstname_en,
            last_name_en=lastname_en,
            first_name_th=firstname_th,
            last_name_th=lastname_th,
            country=country,
            status=status,
            field_of_study=field_of_study,
            specialty=specialty,
            degree=degree_code,
            contact=contact,
        )
        print('Model created..')
        session.add(new_person)
        session.commit()
        total_persons += 1
    print(total_persons)

def link_author():
    for n,author in enumerate(session.query(Author)):
        if author.first_name and author.last_name:
            _auth_firstname = author.first_name.lower()
            _auth_lastname = author.last_name.lower()
            sc = session.query(ScholarshipInfo).filter(
                func.lower(ScholarshipInfo.first_name_en)==_auth_firstname,
                func.lower(ScholarshipInfo.last_name_en)==_auth_lastname).first()
            if sc:
                print('linking {} {} to the Author model'.format(_auth_firstname, _auth_lastname))
                author.scholarship_info = sc
                session.add(author)
                session.commit()
        if(n % 20 == 0):
            print('{}...'.format(n))


if __name__ == '__main__':
    engine = create_engine('postgresql+psycopg2://postgres:_genius01_@localhost:5434/keywordsdw')

    Session = sessionmaker(bind=engine)
    session = Session()
    Person = ScholarshipInfo

    inputfile = sys.argv[1]
    sheetname = sys.argv[2]

    if inputfile == 'link':
        link_author()
    else:
        load_stud_to_db2(inputfile, sheetname)

