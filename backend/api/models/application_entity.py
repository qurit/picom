import os

from sqlalchemy import *
from sqlalchemy.orm import relationship

from api.models.pipeline import PipelineNode

from . import Base


class ApplicationEntity(Base):
    host = Column(String)
    port = Column(Integer)
    full_name = Column(String)
