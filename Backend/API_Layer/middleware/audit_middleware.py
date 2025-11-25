# Backend/API_Layer/middleware/audit_middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, StreamingResponse
from ...DAL.utils.dependencies import get_db
from ...DAL.dao.auditlogs_dao import AuditTrails
import json
import uuid
from typing import Optional
import io

class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

        # Endpoints that should not be audited
        self.open_endpoints = [
            "/docs", "/openapi.json", "/redoc",
            "/login", "/health", "/offerresponse"
        ]
        
        # Entity mapping for common patterns
        self.entity_mappings = {
            "offerletters": {
                "table": "offer_letter_details", 
                "id_field": "user_uuid",
                "alternate_id_fields": ["offer_uuid"]  # Additional ID fields to check
            },
            "countries": {"table": "countries", "id_field": "country_uuid"},
            "users": {"table": "users", "id_field": "user_id"},
            "products": {"table": "products", "id_field": "product_id"},
            # Add your entities here
        }

    def extract_entity_info(self, path: str, req_body: dict, method: str):
        """Extract entity name and ID from request"""
        path_parts = path.strip("/").split("/")
        entity_name = path_parts[0] if path_parts else "unknown"
        
        # Check if it's a bulk operation
        is_bulk = any(keyword in path.lower() for keyword in ["bulk", "batch"])
        
        # Try to get entity ID from various sources
        entity_id = None
        
        # Skip ID extraction for bulk operations
        if is_bulk:
            return entity_name, "BULK_OPERATION"
        
        # 1. From path (e.g., /countries/123 or /offerletters/offer/123)
        if len(path_parts) > 1:
            # Handle nested paths like /offerletters/offer/{uuid}
            if len(path_parts) > 2 and path_parts[2]:
                entity_id = path_parts[2]
            elif path_parts[1] and path_parts[1] not in ["create", "pending"]:
                entity_id = path_parts[1]
        
        # 2. From request body
        if not entity_id and req_body:
            # Check mapped ID field
            if entity_name in self.entity_mappings:
                id_field = self.entity_mappings[entity_name]["id_field"]
                entity_id = req_body.get(id_field)
            
            # Fallback to common ID fields
            if not entity_id:
                entity_id = (
                    req_body.get("id") or 
                    req_body.get("uuid") or 
                    req_body.get("offer_uuid") or
                    req_body.get(f"{entity_name}_id") or
                    req_body.get(f"{entity_name}_uuid")
                )
        
        return entity_name, entity_id

    def get_operation_type(self, method: str) -> str:
        """Map HTTP method to operation type"""
        return {
            "POST": "CREATE",
            "PUT": "UPDATE",
            "PATCH": "UPDATE",
            "DELETE": "DELETE"
        }.get(method, "UNKNOWN")

    async def get_data(self, db, entity_name: str, entity_id: str) -> Optional[dict]:
        """Fetch old data before update/delete"""
        if not entity_id or entity_name not in self.entity_mappings:
            return None
        
        try:
            table_name = self.entity_mappings[entity_name]["table"]
            id_field = self.entity_mappings[entity_name]["id_field"]
            
            # Use parameterized query to prevent SQL injection
            from sqlalchemy import text
            query = text(f"SELECT * FROM {table_name} WHERE {id_field} = :id")
            result = await db.execute(query, {"id": entity_id})
            row = result.mappings().first()
            
            if row:
                # Convert to dict and handle non-serializable types
                return {k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v 
                        for k, v in dict(row).items()}
        except Exception as e:
            print(f"Error fetching old data: {e}")
        
        return None
    def _get_ip_address(*args, **kwargs) -> Optional[str]:
        request = kwargs.get("request")
        if request and hasattr(request, 'client') and request.client:
            return request.client.host
        return None

    async def dispatch(self, request: Request, call_next):
        print("Audit Middleware Entering...")
        path = request.url.path
        method = request.method

        # Skip audit for certain methods and endpoints
        if method in ["GET", "OPTIONS"] or any(path.startswith(p) for p in self.open_endpoints):
            print(f"Skipping Audit: path={path}, method={method}")
            return await call_next(request)

        # Extract user info
        payload = getattr(request.state, "user", None)
        user_id = payload.get("user_id") if payload else "anonymous"

        # Get request body
        try:
            body = await request.body()
            req_body = json.loads(body) if body else {}
            # Reset body for downstream consumers
            request._body = body
        except:
            req_body = {}

        # Extract entity information
        entity_name, entity_id = self.extract_entity_info(path, req_body, method)
        operation = self.get_operation_type(method)

        ip_address_from_request = self._get_ip_address(request = request)

        print("Ip address", ip_address_from_request)

        # Get IP address (handle proxies)
        ip_address = (
            request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or
            request.headers.get("X-Real-IP") or
            request.client.host if request.client else "unknown"
        )
        
        host = request.headers.get("host", "unknown")

        # Fetch old data BEFORE processing request (for UPDATE/DELETE)
        old_data = None
        if operation in ["UPDATE", "DELETE"] and entity_id:
            async for db in get_db():
                old_data = await self.get_data(db, entity_name, entity_id)
                break

        # Process the request
        response = await call_next(request)

        # Capture response body without consuming it
        new_data = None
        response_body = b""
        
        async for chunk in response.body_iterator:
            response_body += chunk
        
        try:
            new_data = json.loads(response_body.decode())
        except:
            new_data = None

        # For CREATE operations, fetch the newly created data if we have an ID in response
        new_entity_data = None
        if new_data:
            # Try to get the new entity ID from response
            new_entity_id = (
                new_data.get("offer_id") or 
                new_data.get("id") or 
                new_data.get("uuid") or
                new_data.get(f"{entity_name}_id")
            )
            
            if new_entity_id:
                async for db in get_db():
                    new_entity_data = await self.get_data(db, entity_name, new_entity_id)
                    break

        # Create new response with captured body
        response = Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )
        # my_dict = {
        #     "entity_name": entity_name,
        #     "entity_id": entity_id,
        #     "operation": operation,
        #     "user_id": user_id,
        #     "old_data": old_data,
        #     "new_data": new_data,
        #     "ip address": ip_address,
        #     'host': host,
        #     'new_entity_data': new_entity_data
        # }
        # print("Audit Logs:", my_dict)

        # Log audit trail (only if response is successful)
        if 200 <= response.status_code < 300:
            try:
                async for db in get_db():
                    audit = AuditTrails(db)
                    
                    # For CREATE operations, use the fetched entity data as new_data
                    final_new_data = new_entity_data if new_entity_data else new_data
                    
                    await audit.create_audit_log(
                        entity_name=entity_name,
                        entity_id=str(entity_id or "N/A"),
                        operation=operation,
                        user_id=str(user_id),
                        old_data=old_data,
                        new_data=final_new_data,
                        ip_address=ip_address,
                        host=host,
                        endpoint=path
                    )
                    break
            except Exception as e:
                print(f"Audit logging failed: {e}")
                # Don't fail the request if audit logging fails

        return response