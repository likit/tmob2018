from app.wsgi import db


class DimSCCountry(db.Model):
    __tablename__ = 'dim_sc_countries'
    id = db.Column('id', db.Integer,
                   primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(), index=True)

    def __str__(self):
        return self.name


class DimSCUniversity(db.Model):
    __tablename__ = 'dim_sc_universities'
    id = db.Column('id', db.Integer,
                   primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(), index=True)

    def __str__(self):
        return self.name


class DimUniversity(db.Model):
    __tablename__ = 'dim_universities'
    id = db.Column('id', db.Integer,
                   primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(), index=True)

    def __str__(self):
        return self.name


class DimAcademicPosition(db.Model):
    __tablename__ = 'dim_academic_positions'
    id = db.Column('id', db.Integer,
                   primary_key=True, autoincrement=True)
    title = db.Column('title', db.String(), index=True)

    def __str__(self):
        return self.title


class DimThaiName(db.Model):
    __tablename__ = 'dim_thai_names'
    id = db.Column('id', db.Integer,
                   primary_key=True, autoincrement=True)
    firstname = db.Column('firstname', db.String(), index=True)
    lastname = db.Column('lastname', db.String(), index=True)

    @property
    def fullname(self):
        return '{} {}'.format(self.firstname, self.lastname)

    def __str__(self):
        return '{} {}'.format(self.firstname, self.lastname)


class DimThaiNameGroup(db.Model):
    __tablename__ = 'dim_thai_name_groups'
    id = db.Column('id', db.Integer,
                   primary_key=True, autoincrement=True)


class BridgeThaiNameGroup(db.Model):
    __tablename__ = 'br_thai_name_groups'
    th_name_id = db.Column('thname_id',
                          db.ForeignKey('dim_thai_names.id'),
                          primary_key=True)
    th_name_group_id = db.Column('thname_group_id',
                                db.ForeignKey('dim_thai_name_groups.id'),
                                primary_key=True)
    name = db.relationship('DimThaiName')
    th_name_group = db.relationship('DimThaiNameGroup',
                                    backref=db.backref('names'))

    @property
    def fullname(self):
        return self.name.fullname


class DimEngName(db.Model):
    __tablename__ = 'dim_eng_names'
    id = db.Column('id', db.Integer,
                   primary_key=True, autoincrement=True)
    firstname = db.Column('firstname', db.String(), index=True)
    lastname = db.Column('lastname', db.String(), index=True)
    initial = db.Column('initial', db.String(), index=True)

    @property
    def fullname(self):
        return '{} {}'.format(self.firstname, self.lastname)

    def __str__(self):
        return self.fullname


class DimEngNameGroup(db.Model):
    __tablename__ = 'dim_eng_name_groups'
    id = db.Column('id', db.Integer,
                   primary_key=True, autoincrement=True)


class BridgeEngNameGroup(db.Model):
    __tablename__ = 'br_eng_name_groups'
    en_name_id = db.Column('en_name_id',
                          db.ForeignKey('dim_eng_names.id'),
                          primary_key=True)
    en_name_group_id = db.Column('en_name_group_id',
                                db.ForeignKey('dim_eng_name_groups.id'),
                                primary_key=True)
    name = db.relationship('DimEngName')
    en_name_group = db.relationship('DimEngNameGroup',
                                    backref=db.backref('names'))

    @property
    def fullname(self):
        return self.name.fullname


class DimUniversityGroup(db.Model):
    __tablename__ = 'dim_university_groups'
    id = db.Column('id', db.Integer,
                   primary_key=True, autoincrement=True)


class BridgeUniversityGroup(db.Model):
    __tablename__ = 'br_university_groups'
    university_group_id = db.Column('university_group_id',
                                    db.ForeignKey('dim_university_groups.id'),
                                    primary_key=True)
    university_id = db.Column('university_id',
                              db.ForeignKey('dim_universities.id'),
                              primary_key=True)
    university_group = db.relationship('DimUniversityGroup',
                                       backref=db.backref('universities'))
    university = db.relationship('DimUniversity')

    def __str__(self):
        return self.university.name


class DimEmail(db.Model):
    __tablename__ = 'dim_email'
    id = db.Column('id', db.Integer,
                   primary_key=True, autoincrement=True)
    email = db.Column('email', db.String(), index=True)

    def __str__(self):
        return self.email


class DimEmailGroup(db.Model):
    __tablename__ = 'dim_email_group'
    id = db.Column('id', db.Integer,
                   primary_key=True, autoincrement=True)


class BridgeEmailGroup(db.Model):
    __tablename__ = 'br_email_group'
    email_group_id = db.Column('email_group_id',
                               db.ForeignKey('dim_email_group.id'),
                               primary_key=True)
    email_id = db.Column('email_id',
                         db.ForeignKey('dim_email.id'),
                         primary_key=True)
    email_group = db.relationship('DimEmailGroup',
                                  backref=db.backref('emails'))
    email = db.relationship('DimEmail')

    def __str__(self):
        return self.email.email


class FactResearcher(db.Model):
    __tablename__ = 'fact_researchers'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    old_id = db.Column('old_id', db.Integer)
    email_group_id = db.Column('email_group_id',
                               db.ForeignKey('dim_email_group.id'))
    email_group = db.relationship('DimEmailGroup',
                                  backref=db.backref('researcher', uselist=False))
    academic_position_id = db.Column('academic_position_id',
                                     db.ForeignKey('dim_academic_positions.id'))
    academic_position = db.relationship('DimAcademicPosition',
                                        backref=db.backref('researchers', lazy='dynamic'))
    university_group_id = db.Column('university_group_id',
                                    db.ForeignKey('dim_university_groups.id'))
    university_group = db.relationship('DimUniversityGroup',
                                       backref=db.backref('researcher', uselist=False))
    th_name_group_id = db.Column('thname_group_id',
                                db.ForeignKey('dim_thai_name_groups.id'))
    th_name_group = db.relationship('DimThaiNameGroup',
                                   backref=db.backref('researcher', uselist=False))
    en_name_group_id = db.Column('en_name_group_id',
                                 db.ForeignKey('dim_eng_name_groups.id'))
    en_name_group = db.relationship('DimEngNameGroup',
                                    backref=db.backref('researcher', uselist=False))
    sc_graduated_date = db.Column('sc_graduated_year', db.Date())
    sc_country_id = db.Column('sc_country_id', db.ForeignKey('dim_sc_countries.id'))
    sc_university_id = db.Column('sc_university_id', db.ForeignKey('dim_sc_universities.id'))
    sc_field = db.Column('sc_field', db.String())
    sc_specialty = db.Column('sc_specialty', db.String())

