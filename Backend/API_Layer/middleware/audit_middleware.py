# Backend/API_Layer/middleware/audit_middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, StreamingResponse
from ...DAL.utils.dependencies import get_db
from ...DAL.dao.auditlogs_dao import AuditTrails
from ..utils.audit_utils import AuditUtils
import json
import uuid
from typing import Optional
import io

class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

        # Endpoints that should not be audited
        self.open_endpoints = [
            "/docs", "/openapi.json",
            "/redoc","/login", "/health",
        ]
        self.entity_mappings = AuditUtils().entity_mappings
        


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
        entity_name, entity_id = AuditUtils().extract_entity_info(path, req_body, method)
        operation = AuditUtils().get_operation_type(method)

        ip_address_from_request = AuditUtils()._get_ip_address(request = request)
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
        print("Old data", entity_id, entity_name)
        if operation in ["UPDATE", "DELETE"] and entity_id:
            async for db in get_db():
                old_data = await AuditUtils().get_data(db, entity_name, entity_id)
                break
        print("after loop", old_data)
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
        print("New data before loop", new_data)
        new_entity_data = None
        if new_data and operation == "CREATE":
            # Try to get the new entity ID from response
            new_entity_id = (
                new_data.get("offer_uuid") or 
                new_data.get("user_uuid") or 
                new_data.get("uuid") or
                new_data.get(f"{entity_name}_id") or
                new_data.get("personal_uuid") or
                new_data.get("pandadoc_draft_id") or
                new_data.get("address_uuid") or
                new_data.get("identity_type_uuid")
            )
            print("New before loop", new_entity_data)
            print("New data", new_data)
            print("entity name", entity_name)
            print("entity id", entity_id)
            if new_entity_id:
                async for db in get_db():
                    new_entity_data = await AuditUtils().get_data(db, entity_name, new_entity_id)
                    break
        if operation in ["UPDATE", "DELETE"] and entity_id:
            async for db in get_db():
                new_entity_data = await AuditUtils().get_data(db, entity_name, entity_id)
                break
        print("after loop", new_entity_data)
        # Create new response with captured body
        response = Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )
        table_name = self.entity_mappings[entity_name]["table"]
        # my_dict = {
        #     "entity_name": table_name,
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
                        entity_name=table_name,
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