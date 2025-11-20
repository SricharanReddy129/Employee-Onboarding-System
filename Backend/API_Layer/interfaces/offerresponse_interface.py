from pydantic import BaseModel
from typing import List, Optional


class PandaDocRecipient(BaseModel):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    completed: Optional[bool] = None
    viewed: Optional[bool] = None


class PandaDocData(BaseModel):
    id: str                     # PandaDoc document ID
    uuid: str                   # Same UUID you stored in DB
    name: Optional[str] = None
    status: str                 # completed / sent / viewed
    recipients: Optional[List[PandaDocRecipient]] = None
    version: Optional[int] = None


class PandaDocWebhookRequest(BaseModel):
    event: str                  # document.completed
    id: Optional[str] = None    # Webhook event ID
    type: Optional[str] = None  # always webhook_event
    date: Optional[str] = None
    data: PandaDocData          # actual document data


class PandaDocWebhookResponse(BaseModel):
    status: str = "ok"