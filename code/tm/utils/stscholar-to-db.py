import sys
from datetime import datetime
import xml.etree.ElementTree as ET
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy import func, select, update, insert, and_

engine = create_engine('postgresql+psycopg2://postgres@postgres_db/keywordsdw')

metadata = MetaData()

connect = engine.connect()

ScholarTable = Table('scholarship_info', metadata, autoload=True, autoload_with=engine)

def import_data(filename):
    '''Reads XML data from a file to ElementTree.
    '''

    xmldata = ET.parse(filename)
    root = xmldata.getroot()
    for child in root:
        student = {'student_id': child.attrib['student_id']}
        for el in child.iter():
            student[el.tag] = el.text
        try:
            firstname_en, lastname_en = student['NameEn'].split()
        except:
            continue
        else:
            firstname_en = firstname_en.replace('Mr.', '')
            firstname_en = firstname_en.replace('Miss', '')
            firstname_en = firstname_en.replace('Mrs.', '')
            s = select([ScholarTable]).where(and_(
                    func.lower(ScholarTable.c.first_name_en) == firstname_en.lower(),
                    func.lower(ScholarTable.c.last_name_en) == lastname_en.lower()
                    )
                )
            res = connect.execute(s).fetchone()
            if res:
                try:
                    dob = datetime.strptime(student['Birthdate'], '%Y-%m-%d')
                except ValueError:
                    dob = None

                try:
                    graduated_date = datetime.strptime(student['Enddate'], '%Y-%m-%d')
                except ValueError:
                    graduated_date = student['Enddate'][:4]
                    try:
                        graduated_date = datetime.strptime(graduated_date, '%Y')
                    except ValueError:
                        graduated_date = None

                u = update(ScholarTable).values(
                    student_id=int(student['student_id']),
                    dob=dob,
                    graduated_date=graduated_date,
                    country=student['Country'],
                    university=student['University'],
                    email=student['Email'],
                ).where(ScholarTable.c.id==res.id)
            else:
                try:
                    firstname_th, lastname_th = student['NameTh'].split()
                except:
                    firstname_th = student['NameTh']
                    lastname_th = ''
                else:
                    u = insert(ScholarTable).values(
                            student_id=int(student['student_id']),
                            dob=dob,
                            graduated_date=graduated_date,
                            first_name_en=firstname_en,
                            last_name_en=lastname_en,
                            first_name_th=firstname_th,
                            last_name_th=lastname_th,
                            country=student['Country'],
                            university=student['University'],
                            affil=student['Department'],
                            email=student['Email']
                        )
            result = connect.execute(u)



if __name__ == "__main__":
    filename = sys.argv[1]
    import_data(filename)