from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from .API_Layer.middleware.db_session_middleware import DBSessionMiddleware
from .DAL.utils.database import engine
from .API_Layer.routes import offer_routes
from .DAL.models import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Employee Onboarding System API")

# Add DB session middleware
app.add_middleware(DBSessionMiddleware)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Employee Onboarding System API",
        version="1.0.0",
        description="API documentation for the Employee Onboarding System",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema
app.openapi = custom_openapi

app.include_router(master_routes.router, prefix="/offers", tags=["Offers"])