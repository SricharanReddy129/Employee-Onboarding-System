from pydantic import BaseModel

class HRVerificationRequest(BaseModel):
    user_uuid: str
    status: str   # VERIFIED or REJECTED