from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from ..utils.jwt_validator import validate_jwt


class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # Add paths you want to skip
        self.open_endpoints = ["/docs", "/openapi.json", "/redoc"]

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        print(f"[JWTMiddleware] 🚀 Incoming request path: {path}")

        # Skip validation for open endpoints
        if any(path.startswith(ep) for ep in self.open_endpoints):
            print(f"[JWTMiddleware] 🟢 Skipping JWT validation for open endpoint: {path}")
            return await call_next(request)

        # Extract Authorization header
        auth_header = request.headers.get("Authorization")
        print(f"[JWTMiddleware] 🔍 Authorization header: {auth_header}")

        # Check if token is present
        if not auth_header or not auth_header.startswith("Bearer "):
            print("[JWTMiddleware] ❌ Missing or invalid Authorization header")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or invalid Authorization header"},
            )

        token = auth_header.split("Bearer ")[1].strip()
        print(f"[JWTMiddleware] 🔑 Extracted token: {token[:20]}...")  # print only partial for safety

        try:
            print("[JWTMiddleware] 🧠 Validating token...")
            # Call the validation function
            payload = validate_jwt(token)
            print(f"[JWTMiddleware] ✅ Token validated successfully. Payload")

            # Optionally attach decoded payload to request.state for downstream use
            request.state.user = payload

            print("[JWTMiddleware] ↩️ Passing control to the next middleware/endpoint")
            response = await call_next(request)
            print(f"[JWTMiddleware] 🏁 Response status: token data")
            return response

        except HTTPException as e:
            print(f"[JWTMiddleware] ⚠️ Validation failed: {e.detail}")
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

        except Exception as e:
            print(f"[JWTMiddleware] 💥 Unexpected internal error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": f"Internal server error: {str(e)}"},
            )
