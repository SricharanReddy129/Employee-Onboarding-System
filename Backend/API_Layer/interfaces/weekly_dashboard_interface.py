from pydantic import BaseModel
from typing import List


class Summary(BaseModel):
    selected: int
    offersMade: int
    joined: int
    dropOffs: int
    pending: int


class MonthlyJoining(BaseModel):
    week: str
    count: int


class WeeklyJoining(BaseModel):
    day: str
    count: int


class Candidate(BaseModel):
    name: str
    role: str
    department: str
    joiningDate: str
    status: str


class Activity(BaseModel):
    message: str
    type: str
    time: str


class DashboardResponse(BaseModel):
    summary: Summary
    monthlyJoinings: List[MonthlyJoining]
    weeklyJoinings: List[WeeklyJoining]
    joinedCandidates: List[Candidate]
    activities: List[Activity]