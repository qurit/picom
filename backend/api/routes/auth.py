from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from api import session
from api.models.user import User, UserLocal
from api.schemas.user import Token

router = APIRouter()


class LoginException(HTTPException):
    def __init__(self, status_code=401, detail="Incorrect username or password", **kwargs):
        super().__init__(status_code, detail, **kwargs)


@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(session)):
    user = User.query(db).filter_by(username=form_data.username).first()
    if not user:
        #TODO: try ldap
        raise LoginException()

    if ldap := user.ldap_user:
        #TODO: implement ldap authentication
        raise LoginException()
    elif (local := user.local_user) and not local.verify_password(form_data.password):
        raise LoginException()

    return Token(access_token=user.generate_token())
