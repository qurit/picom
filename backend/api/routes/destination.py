import os

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from typing import List

from api import session
from api.schemas import application_entity
from api.models.application_entity import ApplicationEntity
from api.auth import token_auth


router = APIRouter()


@router.get("/", response_model=List[application_entity.ApplicationEntity])
def get_all_ae(db: Session = Depends(session)):
    """ Get all application entities"""
    return db.query(ApplicationEntity).all()


@router.post("/",  response_model=application_entity.ApplicationEntity)
def create_ae(ae: application_entity.CreateApplicationEntity, db: Session = Depends(session)):
    """ Create a new application entity"""
    new_ae = ApplicationEntity(
        host=ae.host, port=.port, ae_title=ae.host + " " + str(ae.port))
    new_ae.save(db)
    return new_ae
