from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class BulkJoinRequest(BaseModel):
    user_emails_list: List[str]
    joining_date: date
    location: str
    reporting_time: str
    custom_message: Optional[str] = None


