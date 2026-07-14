from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from database import get_db

from models import User
from models import Habit
from models import HabitLog

from schemas import AtRiskMember


router = APIRouter(
    prefix="/at-risk",
    tags=["At Risk"]
)


@router.get("/at_risk", response_model=list[AtRiskMember])
def get_at_risk_members(db: Session = Depends(get_db)):

    users = db.query(User).all()

    at_risk = []

    today = date.today()


    for user in users:

        # Total habits assigned to user
        total_habits = (
            db.query(Habit)
            .filter(Habit.user_id == user.id)
            .count()
        )


        # Completed habits today
        completed_today = (
            db.query(HabitLog)
            .filter(
                HabitLog.user_id == user.id,
                HabitLog.completed_date == today
            )
            .count()
        )


        missed_habits = total_habits - completed_today


        # Risk calculation
        if total_habits == 0:
            risk_level = "No Habits"

        else:
            completion_rate = (
                completed_today / total_habits
            ) * 100


            if completion_rate < 50:
                risk_level = "High"

            elif completion_rate < 80:
                risk_level = "Medium"

            else:
                risk_level = "Low"



        at_risk.append(
            {
                "name": user.name,
                "total_habits": total_habits,
                "completed_today": completed_today,
                "missed_habits": missed_habits,
                "risk_level": risk_level
            }
        )


    return at_risk