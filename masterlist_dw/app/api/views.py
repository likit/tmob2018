from . import api_blueprint as api
from http import HTTPStatus
from marshmallow_sqlalchemy.fields import Nested
from marshmallow import fields
from flask_restful import Resource
from app.models import *
from app.wsgi import ma


class UniversitySchema(ma.ModelSchema):
    class Meta:
        model = DimUniversity


university_schema = UniversitySchema()
universities_schema = UniversitySchema(many=True)

class UniversityListResource(Resource):
    def get(self):
        universities = DimUniversity.query.all()
        return {'data': universities_schema.dump(universities)}, HTTPStatus.OK


class UniversityResource(Resource):
    def get(self, id):
        university = DimUniversity.query.get(id)
        if university is None:
            return {'message': 'University with ID {} not found.'.format(id)}, HTTPStatus.NOT_FOUND
        else:
            return {'data': university_schema.dump(university)}, HTTPStatus.OK


class EmailSchema(ma.Schema):
    email_data = Nested(DimEmail)
    email = fields.Method('get_json', data_key='@email')

    def get_json(self, obj):
        return {
            'email': obj.email.email,
            'id': obj.email.id
        }


class EmailGroupSchema(ma.ModelSchema):
    emails = Nested(EmailSchema, many=True)
    class Meta:
        model = DimEmailGroup


class ThaiNameSchema(ma.Schema):
    name_data = Nested(DimThaiName)
    name = fields.Method('get_json', data_key='@name')

    def get_json(self, obj):
        return {
            'firstname': obj.name.firstname,
            'lastname': obj.name.lastname,
            'id': obj.name.id
        }


class ThaiNameGroupSchema(ma.ModelSchema):
    names = Nested(ThaiNameSchema, many=True)
    class Meta:
        model = DimThaiNameGroup


class EngNameSchema(ma.Schema):
    name_data = Nested(DimEngName)
    name = fields.Method('get_json', data_key='@name')

    def get_json(self, obj):
        return {
            'firstname': obj.name.firstname,
            'lastname': obj.name.lastname,
            'initial': obj.name.initial,
            'id': obj.name.id
        }


class EngNameGroupSchema(ma.ModelSchema):
    names = Nested(EngNameSchema, many=True)
    class Meta:
        model = DimEngNameGroup


class UniversityDataSchema(ma.Schema):
    university_data = Nested(DimUniversity)
    name = fields.Method('get_json', data_key='@university')

    def get_json(self, obj):
        return {
            'name': obj.university.name,
            'id': obj.university.id
        }


class UniversityGroupSchema(ma.ModelSchema):
    universities = Nested(UniversityDataSchema, many=True)
    class Meta:
        model = DimUniversityGroup


class ResearcherSchema(ma.ModelSchema):
    email_group = Nested(EmailGroupSchema, exclude=('researcher',))
    th_name_group = Nested(ThaiNameGroupSchema, exclude=('researcher',))
    en_name_group = Nested(EngNameGroupSchema, exclude=('researcher',))
    university_group = Nested(UniversityGroupSchema, exclude=('researcher',))
    class Meta:
        model = FactResearcher

researcher_schema = ResearcherSchema()


class ResearcherResource(Resource):
    def get(self, id):
        researcher = FactResearcher.query.get(id)
        if researcher is None:
            return {'message': 'Researcher with ID {} not found.'.format(id)}, HTTPStatus.NOT_FOUND
        else:
            return {'data': researcher_schema.dump(researcher)}, HTTPStatus.OK
