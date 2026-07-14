from pydantic import BaseModel
from typing import Optional
from datetime import date


class GoogleUserInfo(BaseModel):
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    verified_email: bool = False


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    profile_picture: Optional[str] = None

    class Config:
        from_attributes = True


class SquadCreate(BaseModel):
    name: str




class SquadCreate(BaseModel):
    name: str


class SquadResponse(BaseModel):
    id: str
    name: str
    created_by: str

    class Config:
        from_attributes = True



class InviteResponse(BaseModel):
    invite_link: str


class SquadMemberResponse(BaseModel):
    id: str
    name: str
    email: str
    profile_picture: Optional[str] = None

    class Config:
        from_attributes = True

class HabitCreate(BaseModel):
    squad_id: str
    title: str


class HabitResponse(BaseModel):
    id: str
    squad_id: str
    title: str
    created_by: str

    class Config:
        from_attributes = True

class HabitLogCreate(BaseModel):
    completed: bool


class HabitLogResponse(BaseModel):
    id: str
    habit_id: str
    user_id: str
    completed: bool
    date: date

    class Config:
        from_attributes = True

class AnalyticsResponse(BaseModel):
    current_streak: int
    completion_rate: float
    squad_average: float
    who_broke_chain: str
    missed_days: int

class LeaderboardMember(BaseModel):
    rank: int
    name: str
    streak: int
    completion_rate: float


class ProgressMember(BaseModel):
    name: str
    completed: int
    total: int
    progress: float


class AtRiskMember(BaseModel):
    name: str


class DashboardResponse(BaseModel):
    leaderboard: list[LeaderboardMember]
    progress: list[ProgressMember]
    at_risk: list[AtRiskMember]

class LeaderboardMember(BaseModel):
    rank: int
    name: str
    streak: int
    completion_rate: float
    is_admin: bool





class AtRiskMember(BaseModel):
    name: str
    total_habits: int
    completed_today: int
    missed_habits: int
    risk_level: str

   