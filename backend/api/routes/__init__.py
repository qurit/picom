from fastapi import Depends

from api import app, session, schemas
from api.auth import token_auth

from . import pipeline, container, user, dicom, application_entity, auth, test, settings

# Auth Routes
app.include_router(test.router, tags=['Test'], prefix='/test')
app.include_router(auth.router, tags=['Auth'], prefix='/auth')

# All Secure Except for create_local_user
app.include_router(user.router, tags=['User'], prefix='/user')

# Secure Routes
app.include_router(pipeline.router, tags=['Pipeline'], prefix='/pipeline', dependencies=[Depends(token_auth)])
app.include_router(container.router, tags=['Container'], prefix='/container', dependencies=[Depends(token_auth)])
app.include_router(dicom.router, tags=['Dicom'], prefix='/dicom', dependencies=[Depends(token_auth)])
app.include_router(application_entity.router, tags=['Application Entity'], prefix='/ae', dependencies=[Depends(token_auth)])
app.include_router(settings.router, tags=['Settings'], prefix='/settings', dependencies=[Depends(token_auth)])
