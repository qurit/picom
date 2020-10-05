from typing import List

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from api import session
from api.models.pipeline import Pipeline, PipelineLink, PipelineContainer
from api.schemas import pipeline as schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.Pipeline])
def get_all_pipelines(db: Session = Depends(session)):
    return db.query(Pipeline).all()


@router.post("/", response_model=schemas.Pipeline)
def create_pipeline(pipeline: schemas.PipelineCreate, db: Session = Depends(session)):
    print("got here")
    print(pipeline)
    return Pipeline(**pipeline.dict()).save(db)


@router.get("/{pipeline_id}", response_model=schemas.PipelineFull)
def get_pipeline(pipeline_id: int, db: Session = Depends(session)):
    return db.query(Pipeline).get(pipeline_id)


@router.delete("/{pipeline_id}", response_model=schemas.Pipeline)
def delete_pipeline(pipeline_id: int, db: Session = Depends(session)):
    return db.query(Pipeline).get(pipeline_id).delete(db)


@router.post("/{pipeline_id}/containers", response_model=schemas.PipelineContainer)
def create_pipeline_container(container: schemas.PipelineContainerCreate, db: Session = Depends(session)):
    return PipelineContainer(**container.dict()).save(db)

# for testing


@router.get("/{pipeline_id}/containers")
def get_pipeline_containers(db: Session = Depends(session)):
    return db.query(PipelineContainer).all()


@router.post("/{pipeline_id}/links", response_model=schemas.PipelineLink)
def create_pipeline_link(link: schemas.PipelineLinkCreate, db: Session = Depends(session)):
    return PipelineLink(**link.dict()).save(db)
