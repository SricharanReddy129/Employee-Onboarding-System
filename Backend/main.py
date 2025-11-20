from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from .API_Layer.routes import master_routes, offerletter_routes, education_routes, offerresponse_routes
from .API_Layer.middleware.jwt_middleware import JWTMiddleware

# models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Employee Onboarding System API")

# Add JWT middleware globally
# app.add_middleware(JWTMiddleware)

# Add DB session middleware
# app.add_middleware(DBSessionMiddleware)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Employee Onboarding System",
        version="0.1.0",
        description="Secure API with JWT & RBAC",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method in ["get", "post", "put", "delete"]:
                openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(offerletter_routes.router, prefix="/offerletters", tags=["Offer Letters"])
app.include_router(master_routes.router, prefix="/masters", tags=["Master (Countries)"])
app.include_router(education_routes.router, prefix="/education", tags=["Education Documents"])
app.include_router(offerresponse_routes.router, prefix="/offerresponse", tags=["Offer Response"])