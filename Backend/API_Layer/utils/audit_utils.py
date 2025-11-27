# Backend/API_Layer/utils/audit_utils.py
from typing import Optional
class AuditUtils:
    def __init__(self):

        # Endpoints that should not be audited
        self.open_endpoints = [
            "/docs", "/openapi.json",
            "/redoc", "/login", "/health"
        ]
        
        # Entity mapping for common patterns
        self.entity_mappings = {
            "offerletters": {
                "table": "offer_letter_details",
                "id_field": "user_uuid",
                "alternate_id_fields": ["offer_uuid", "pandadoc_draft_id"]   # optional alternate key
            },
            "masters-country": {
                "table": "countries",
                "id_field": "country_uuid"
            },
            "masters-education-level": {
                "table": "education_level",
                "id_field": "education_uuid"
            },
            "masters-mapping": {
                "table": "country_education_document_mapping",
                "id_field": "mapping_uuid"
            },
            "masters-contacts": {
                "table": "contacts",
                "id_field": "contact_uuid"
            },
            "education": {
                "table": "employee_education_document",
                "id_field": "document_uuid"
            },
            "employee-details": {
                "table": "personal_details",
                "id_field": "personal_uuid"
            }
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
                    req_body.get("user_uuid") or 
                    req_body.get("uuid") or 
                    req_body.get("offer_uuid") or
                    req_body.get("personal_uuid") or
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