from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from Backend.API_Layer.routes import docusign_token_generation_route, employee_experience_routes, hr_onboarding_routes, offer_approval_action_routes, otp_routes, redis_cache_routes
from .API_Layer.routes import (master_routes, offerletter_routes, education_routes, offerresponse_routes, employee_details_routes,
                               identity_routes, employee_upload_routes)
from .API_Layer.middleware.jwt_middleware import JWTMiddleware
from fastapi.middleware.cors import CORSMiddleware
from .API_Layer.middleware.audit_middleware import AuditMiddleware
from Backend.API_Layer.routes import token_verification_router
from Backend.API_Layer.routes import offer_acceptance_request_routes
from Backend.API_Layer.routes import offer_approval_action_routes
from Backend.API_Layer.routes import hr_bulk_join_router

# models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Employee Onboarding System API")
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                    "http://localhost:3000",
                    "https://employeeonbordingforms.netlify.app",
                    "https://nonprovidentially-xiphisternal-junior.ngrok-free.dev",
                    "https://api.54.206.95.128.sslip.io"],
    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
    max_age=3600,
)

# Add Audit Middleware globally
app.add_middleware(AuditMiddleware)
# Add JWT middleware globally
app.add_middleware(JWTMiddleware)

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
app.include_router(master_routes.router, prefix="/masters", tags=["Master (Countries, Education Levels, Contacts)"])
app.include_router(education_routes.router, prefix="/education", tags=["Education Documents"])
app.include_router(offerresponse_routes.router, prefix="/offerresponse", tags=["Offer Response"])
app.include_router(employee_details_routes.router, prefix="/employee-details", tags=["Employee Details"])
app.include_router(identity_routes.router, prefix="/identity", tags=["Identity Details"])
app.include_router(employee_experience_routes.router, prefix="/experience", tags=["Employee Experience"])
app.include_router(employee_upload_routes.router, prefix="/employee-upload", tags=["Employee Uploads"])
app.include_router(otp_routes.router, prefix="/otp", tags=["Otp Verification"])
app.include_router(token_verification_router.router, prefix="/token-verification", tags=["Token Verification"])
app.include_router(offer_acceptance_request_routes.router, prefix="/offer-approval-requests", tags=["Offer Approval Requests"])
app.include_router(offer_approval_action_routes.router, prefix="/offer-approval", tags=["Offer Approval"])
app.include_router(hr_onboarding_routes.router, prefix="/hr", tags=["HR Onboarding"])
app.include_router(docusign_token_generation_route.router, prefix="/docusign", tags=["DocuSign Token Generation"])
app.include_router(hr_bulk_join_router.router, prefix="/hr", tags=["HR Bulk Join"])