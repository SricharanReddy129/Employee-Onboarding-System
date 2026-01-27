from pydantic import BaseModel
from typing import List
from datetime import date

class BulkJoinRequest(BaseModel):
    user_emails_list: List[str]
    joining_date: date

