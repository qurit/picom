import os
from collections import Counter
from itertools import chain

from sqlalchemy.orm import Session
from sqlalchemy import asc
from fastapi import APIRouter, Depends
from typing import List

from api import session
from api.schemas import dicom, pipeline
from api.models.dicom import DicomNode, DicomPatient, DicomStudy, DicomSeries


router = APIRouter()

# getting treeview nodes at each level


@router.get("/received-series")
def get_received_series(db: Session = Depends(session)):
    dicom_series = db.query(DicomSeries.date_received).order_by(
        asc(DicomSeries.date_received)).all()
    dicom_series_to_count = list(chain(*dicom_series))
    dicom_series_to_count = map(lambda x: x.date(), dicom_series_to_count)
    dicom_series_to_count = list(dicom_series_to_count)
    return Counter(dicom_series_to_count)


@router.get("/series-breakdown/{dicom_type}/{dicom_id}")
def get_series_breakdown(dicom_type: str, dicom_id: int, db: Session = Depends(session)):
    print(dicom_type)
    print(dicom_id)

    # dicom_patient = db.query(DicomNode.id, DicomPatient.dicom_node_id, DicomStudy.dicom_patient_id,
    #                          DicomSeries.dicom_study_id).join(DicomNode, DicomPatient, DicomStudy, DicomSeries).all()

    # dicom_patient = db.query(DicomNode, DicomPatient, DicomStudy, DicomSeries).filter(DicomNode.id == DicomPatient.dicom_node_id).filter(
    #     DicomPatient.id == DicomStudy.dicom_patient_id).filter(DicomStudy.id == DicomSeries.dicom_study_id).filter(DicomNode.id == 2).all()

    dicom_series = db.query(DicomSeries.modality).filter(
        DicomPatient.id == DicomStudy.dicom_patient_id).filter(DicomStudy.id == DicomSeries.dicom_study_id).filter(DicomPatient.id == 1).all()
    # print(dicom_patient)

    # dicom_series = db.query(DicomSeries.modality).order_by(
    # asc(DicomSeries.modality)).all()
    dicom_series_to_count = list(chain(*dicom_series))
    return Counter(dicom_series_to_count)
    # return dicom_patient


@router.get("/stats")
def get_dicom_stats(db: Session = Depends(session)):
    stats = {
        "dicom_node_counts": db.query(DicomNode).count(),
        "dicom_patient_counts": db.query(DicomPatient).count(),
        "dicom_study_counts": db.query(DicomStudy).count(),
        "dicom_series_counts": db.query(DicomSeries).count()
    }
    return stats


@ router.get("/nodes", response_model=List[dicom.DicomNode])
def get_all_dicom_nodes(db: Session = Depends(session)):
    return db.query(DicomNode).all()


@ router.get("/nodes/{dicom_node_id}/patients", response_model=List[dicom.DicomPatient])
def get_node_patients(dicom_node_id: int, db: Session = Depends(session)):
    return db.query(DicomPatient).filter_by(dicom_node_id=dicom_node_id).all()


@ router.get("/nodes/{dicom_node_id}/patient/{patient_id}/studies", response_model=List[dicom.DicomStudy])
def get_patient_studies(dicom_node_id: int, patient_id: int, db: Session = Depends(session)):
    return db.query(DicomStudy).filter_by(dicom_patient_id=patient_id).all()


@ router.get("/patient/{patient_id}/study/{study_id}/series", response_model=List[dicom.DicomSeries])
def get_study_series(patient_id: int, study_id: int, db: Session = Depends(session)):
    return db.query(DicomSeries).filter_by(dicom_study_id=study_id).all()

# deleting nodes and substuff


@ router.delete("/node/{dicom_node_id}/", response_model=dicom.DicomNode)
def delete_node(dicom_node_id: int, db: Session = Depends(session)):
    return db.query(DicomNode).get(dicom_node_id).delete(db)


@ router.delete("/patient/{patient_id}/", response_model=dicom.DicomPatient)
def delete_patient(patient_id: int, db: Session = Depends(session)):
    return db.query(DicomPatient).get(patient_id).delete(db)


@ router.delete("/study/{study_id}/", response_model=dicom.DicomStudy)
def delete_study(study_id: int, db: Session = Depends(session)):
    return db.query(DicomStudy).get(study_id).delete(db)


@ router.delete("/series/{series_id}", response_model=dicom.DicomSeries)
def delete_series(series_id: int, db: Session = Depends(session)):
    return db.query(DicomSeries).get(series_id).delete(db)

# the send to container code stuff


@ router.put("/node/{dicom_node_id}")
def send_dicom_node(dicom_node_id: int, pipeline_id: pipeline.PipelineId, db: Session = Depends(session)):
    print(dicom_node_id)
    print(pipeline_id)
    dicom_node = db.query(DicomNode).get(dicom_node_id)
    return(dicom_node.abs_path)


@ router.put("/node/{dicom_node_id}/{dicom_patient_id}")
def send_dicom_patient(dicom_node_id: int, dicom_patient_id: int, pipeline_id: pipeline.PipelineId, db: Session = Depends(session)):
    dicom_patient = db.query(DicomPatient).get(dicom_patient_id)
    return(dicom_patient.abs_path)


@ router.put("/node/{dicom_node_id}/{dicom_patient_id}/{dicom_study_id}")
def send_dicom_study(dicom_node_id: int, dicom_patient_id: int, dicom_study_id: int, pipeline_id: pipeline.PipelineId, db: Session = Depends(session)):
    dicom_study = db.query(DicomStudy).get(dicom_study_id)
    return(dicom_study.abs_path)


@ router.put("/node/{dicom_node_id}/{dicom_patient_id}/{dicom_study_id}/{dicom_series_id}")
def send_dicom_series(dicom_node_id: int, dicom_patient_id: int, dicom_study_id: int, dicom_series_id: int, pipeline_id: pipeline.PipelineId, db: Session = Depends(session)):
    dicom_series = db.query(DicomSeries).get(dicom_series_id)
    return(dicom_series.abs_path)
