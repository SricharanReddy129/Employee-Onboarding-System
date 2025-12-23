from pydantic import BaseModel

class OfferApproveActionRequest(BaseModel):
    user_uuid: str
    action: str  # e.g., "approve" or "reject"
    comments: str | None = None