from pydantic import BaseModel

class OfferRequestCreateResponse(BaseModel):
    user_uuid: str
    request_by: int
    action_taker_id: int
    