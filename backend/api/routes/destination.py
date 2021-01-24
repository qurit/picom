import os

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from typing import List

from api import session
from api.schemas import destination
from api.models.application_entity import ApplicationEntity
from api.auth import token_auth


router = APIRouter()


@router.get("/", response_model=List[destination.Destination])
def get_all_destinations(db: Session = Depends(session)):
    """ Get all application entities"""
    return db.query(Destination).all()


@router.post("/",  response_model=destination.Destination)
def create_destination(destination: destination.CreateDestination, db: Session = Depends(session)):
    """ Create a new application entity"""
    new_destination = Destination(
        host=destination.host, port=destination.port, full_name=destination.host + " " + str(destination.port))
    new_destination.save(db)
    return new_destination
