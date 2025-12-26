from pydantic import BaseModel

class OfferActionAdminResponse(BaseModel):
    user_uuid: str
    user_first_name: str
    user_last_name: str
    request_id: str
    requested_name: str
    action : str
    message: str