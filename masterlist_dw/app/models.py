from app.wsgi import db


class DimUniversity(db.Model):
    __tablename__ = 'dim_universities'
    id = db.Column('id', db.Integer,
                   primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(), index=True)