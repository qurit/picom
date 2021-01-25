from . import BaseModel, BaseORMModel


class ApplicationEntity(BaseORMModel):
    host: str
    port: int
    ae_title: str


class CreateApplicationEntity(BaseModel):
    host: str
    port: int


class UserApplicationEntity(BaseORMModel):
    ae: ApplicationEntity
