from flask import request
from flask_restx import Resource, Namespace, fields
from api import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from api.models.application_entity import ApplicationEntity 
from api.models.dicom_patient import DicomPatient 
from api.models.dicom_store_event import DicomStoreEvent 
from api.models.dicom_study import DicomStudy 
from api.models.dicom_series import DicomSeries 

api = Namespace('Application Entity', description='Dicom data related to the application entity')
application_entity_model = api.model('Application Entity', {'id': fields.Integer, 'title': fields.String})

# Application Entity 
@api.route('/application-entity', methods=['GET', 'POST', 'DELETE'])
class ApplicationEntityRoute(Resource):
    def get(self):
        return {'application_entities': ApplicationEntity.Schema(many=True).dump(ApplicationEntity.query.all())}
        
    def delete(self):
        data = request.get_json()
        ApplicationEntity.query.filter(ApplicationEntity.id == data.get('id')).delete()
        db.session.commit()
        return "Application Entity deleted"

    @api.expect(application_entity_model)
    def post(self):
        data = request.get_json()
        newApplicationEntity = ApplicationEntity(title=data.get('title'))
        db.session.add(newApplicationEntity)
        db.session.commit()
        return "Application Entity added"

@api.route('/application-entity/<id>', methods=['GET', 'PUT', 'DELETE'])
class ApplicationEntityRoute(Resource):
    def get(self, id):
        return {'application-entity': ApplicationEntity.Schema(many=False).dump(ApplicationEntity.query.filter(ApplicationEntity.id == id).first())}

    def put(self, id):
        data = request.get_json()
        newApplicationEntity = ApplicationEntity.query.filter(ApplicationEntity.id == id).first()
        newApplicationEntity.title = data.get('title')
        db.session.commit()
        return "Application Entity updated"

    def delete(self, id):
        ApplicationEntity.query.filter(ApplicationEntity.id == id).delete()
        db.session.commit()
        return "Application Entity deleted"

# # Dicom Store Event
# # belongs to an application entity
@api.route('/store-event', methods=['GET'])
class StoreEventRoute(Resource):

    def get(self):
        return {'store_event': DicomStoreEvent.Schema(many=True).dump(DicomStoreEvent.query.all())}

# # Dicom Patient
# # belongs to a store event
@api.route('/patient', methods=['GET'])
class DicomPatientRoute(Resource):

    def get(self):
        return {'dicom-patient': DicomPatient.Schema(many=True).dump(DicomPatient.query.all())}

# # Dicom Study
# # belongs to a patient
@api.route('/study', methods=['GET'])
class DicomStudyRoute(Resource):

    def get(self):
        return {'study': DicomStudy.Schema(many=True).dump(DicomStudy.query.all())}

# # Dicom series
# # belongs to a study
@api.route('/series', methods=['GET'])
class DicomSeriesRoute(Resource):

    def get(self):
        return {'series': DicomSeries.Schema(many=True).dump(DicomSeries.query.all())}
