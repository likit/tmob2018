from datetime import datetime

from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask import Flask
import pandas as pd
import os
import click
from app.config import *

if os.environ.get('FLASK_ENV', 'production') == 'development':
    DEV_DATABASE = os.environ.get('DEV_DATABASE')
    if DEV_DATABASE is None:
        raise ValueError('Development database must be specified for the development mode.')
    config = DevelopmentConfig
else:
    DATABASE = os.environ.get('DATABASE')
    if DATABASE is None:
        raise ValueError('Production database must be specified for the production mode.')
    config = ProductionConfig

db = SQLAlchemy()
migrate = Migrate()
admin = Admin()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app)

    from app.api import api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app


# Models must be loaded before app creation
from app.models import *

admin.add_view(ModelView(DimEmail, db.session, category='Dimensions'))
admin.add_view(ModelView(DimEmailGroup, db.session, category='Dimensions'))
admin.add_view(ModelView(BridgeEmailGroup, db.session, category='Dimensions'))
admin.add_view(ModelView(FactResearcher, db.session, category='Facts'))
admin.add_view(ModelView(DimAcademicPosition, db.session, category='Dimensions'))
admin.add_view(ModelView(DimUniversity, db.session, category='Dimensions'))
admin.add_view(ModelView(DimUniversityGroup, db.session, category='Dimensions'))
admin.add_view(ModelView(BridgeUniversityGroup, db.session, category='Dimensions'))
admin.add_view(ModelView(DimThaiName, db.session, category='Dimensions'))
admin.add_view(ModelView(DimThaiNameGroup, db.session, category='Dimensions'))
admin.add_view(ModelView(BridgeThaiNameGroup, db.session, category='Dimensions'))
admin.add_view(ModelView(DimEngName, db.session, category='Dimensions'))
admin.add_view(ModelView(DimEngNameGroup, db.session, category='Dimensions'))
admin.add_view(ModelView(BridgeEngNameGroup, db.session, category='Dimensions'))
admin.add_view(ModelView(DimSCUniversity, db.session, category='Dimensions'))
admin.add_view(ModelView(DimSCCountry, db.session, category='Dimensions'))

app = create_app(config)


@app.cli.command('importdata')
@click.argument('jsonfile')
def import_data(jsonfile):
    print('Loading data...')
    df = pd.read_json(jsonfile).fillna('')
    num = 0
    for idx, row in df.iterrows():
        num += 1
        fact = FactResearcher.query.filter_by(old_id=idx).first()
        if not fact:
            fact = FactResearcher(old_id=idx)
        else:
            print('ID {} already exists..'.format(idx))
            continue

        academic_title = row.updated_academic_title
        if academic_title:
            _title = DimAcademicPosition.query.filter_by(title=academic_title).first()
            if not _title:
                new_title = DimAcademicPosition(title=academic_title)
                db.session.add(new_title)
                db.session.commit()
                fact.academic_position = new_title
            else:
                fact.academic_position = _title
        th_names = set([n for n in row[['Name_Thai', 'fullname_th_sc', 'fullname_th_m']]
                        if n != ''])
        if th_names:
            th_name_group = DimThaiNameGroup()
            for t in th_names:
                try:
                    _firstname, _lastname = t.split()
                except:
                    continue

                _thname = DimThaiName(firstname=_firstname, lastname=_lastname)
                br_th_name = BridgeThaiNameGroup(
                    th_name_group=th_name_group,
                    name=_thname
                )
                db.session.add(br_th_name)
            fact.th_name_group = th_name_group
        en_names = set([n.lower()
                        for n in row[['Name_Eng', 'sc_fullname_en', 'nr_fullname_en']]
                        if n != ''])
        if en_names:
            en_name_group = DimEngNameGroup()
            for n in en_names:
                try:
                    _firstname, _lastname = n.split()
                    _firstname = _firstname.title()
                    _lastname = _lastname.title()
                    _initial = '{} {}'.format(_lastname, _firstname[0])
                except:
                    continue
                _en_name = DimEngName(firstname=_firstname,
                                      lastname=_lastname,
                                      initial=_initial)
                br_en_name = BridgeEngNameGroup(
                    en_name_group=en_name_group,
                    name=_en_name
                )
                db.session.add(br_en_name)
            fact.en_name_group = en_name_group
        if row['email_sc']:
            emails = set([e for e in row['email_sc'].replace(';', ',').split(', ')
                          if e != ''])
        else:
            emails = set()
        emails.update([e for e in row['email_m'].replace(';', ',').split(', ')
                       if e != ''])
        if emails:
            email_group = DimEmailGroup()
            for e in emails:
                _email = DimEmail(email=e)
                br_email = BridgeEmailGroup(
                    email_group=email_group,
                    email=_email
                )
                db.session.add(br_email)
            fact.email_group = email_group

        unis = set([u for u in row[['University', 'university_name_cleaned']]
                    if u != ''])
        if unis:
            university_group = DimUniversityGroup()
            for u in unis:
                _university = DimUniversity.query.filter_by(name=u).first()
                if not _university:
                    _university = DimUniversity(name=u)
                br_university = BridgeUniversityGroup(
                    university_group=university_group,
                    university=_university
                )
                db.session.add(br_university)
            fact.university_group = university_group

        sc_country_name = row['country'].strip()
        if sc_country_name:
            sc_country = DimSCCountry.query.filter_by(name=sc_country_name).first()
            if not sc_country:
                sc_country = DimSCCountry(name=sc_country_name)
                db.session.add(sc_country)
                db.session.commit()
            fact.sc_country = sc_country

        sc_university_name = row['university'].strip()
        if sc_university_name:
            sc_university = DimSCUniversity.query.filter_by(name=sc_university_name).first()
            if not sc_university:
                sc_university = DimSCUniversity(name=sc_university_name)
                db.session.add(sc_university)
                db.session.commit()
            fact.sc_university = sc_university

        graduation = row['graduated_date']
        if graduation != 'NaT' and graduation != '':
            graduation = datetime.strptime(graduation, '%Y-%m-%d')
            fact.sc_graduated_date = graduation

        fact.sc_field = row['field_of_study'].strip()
        fact.sc_specialty = row['specialty'].strip()
        db.session.add(fact)
        db.session.commit()
        if num % 1000 == 0:
            print('{}...'.format(num))
