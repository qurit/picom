import os

from sqlalchemy import *
from sqlalchemy.orm import relationship

from api.models.pipeline import PipelineNode

from . import Base


class ApplicationEntity(Base):
    host = Column(String)
    port = Column(Integer)
    ae_title = Column(String)
