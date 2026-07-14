from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user
from models import Habit, Squad, User
from schemas import HabitCreate, HabitResponse
from datetime import date
from models import HabitLog
from schemas import HabitLogCreate, HabitLogResponse
from datetime import date, timedelta
from schemas import AnalyticsResponse
from models import HabitLog, SquadMember

router = APIRouter()


# ---------------------------------------
# Create Habit
# Only Squad Admin Can Create Habit
# ---------------------------------------
@router.post("/", response_model=HabitResponse)
async def create_habit(
    habit: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    squad = db.query(Squad).filter(
        Squad.id == habit.squad_id
    ).first()

    if squad is None:
        raise HTTPException(
            status_code=404,
            detail="Squad not found"
        )

    if squad.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only squad admin can create habits"
        )

    new_habit = Habit(
        squad_id=habit.squad_id,
        title=habit.title,
        created_by=current_user.id
    )

    db.add(new_habit)
    db.commit()
    db.refresh(new_habit)

    return new_habit


# ---------------------------------------
# Get All Habits Of A Squad
# ---------------------------------------
@router.get("/{squad_id}", response_model=list[HabitResponse])
async def get_habits(
    squad_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    squad = db.query(Squad).filter(
        Squad.id == squad_id
    ).first()

    if squad is None:
        raise HTTPException(
            status_code=404,
            detail="Squad not found"
        )

    habits = db.query(Habit).filter(
        Habit.squad_id == squad_id
    ).all()

    return habits


# ---------------------------------------
# Get Single Habit
# ---------------------------------------
@router.get("/single/{habit_id}", response_model=HabitResponse)
async def get_single_habit(
    habit_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    habit = db.query(Habit).filter(
        Habit.id == habit_id
    ).first()

    if habit is None:
        raise HTTPException(
            status_code=404,
            detail="Habit not found"
        )

    return habit


# ---------------------------------------
# Delete Habit
# Only Squad Admin
# ---------------------------------------
@router.delete("/{habit_id}")
async def delete_habit(
    habit_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    habit = db.query(Habit).filter(
        Habit.id == habit_id
    ).first()

    if habit is None:
        raise HTTPException(
            status_code=404,
            detail="Habit not found"
        )

    squad = db.query(Squad).filter(
        Squad.id == habit.squad_id
    ).first()

    if squad.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only squad admin can delete habits"
        )

    db.delete(habit)
    db.commit()

    return {
        "success": True,
        "message": "Habit deleted successfully"
    }

@router.post("/{habit_id}/mark", response_model=HabitLogResponse)
async def mark_habit(
    habit_id: str,
    data: HabitLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    habit = db.query(Habit).filter(
        Habit.id == habit_id
    ).first()

    if habit is None:
        raise HTTPException(
            status_code=404,
            detail="Habit not found"
        )

    today = date.today()

    existing = db.query(HabitLog).filter(
        HabitLog.habit_id == habit_id,
        HabitLog.user_id == current_user.id,
        HabitLog.date == today
    ).first()

    if existing:
        existing.completed = data.completed
        db.commit()
        db.refresh(existing)
        return existing

    log = HabitLog(
        habit_id=habit_id,
        user_id=current_user.id,
        completed=data.completed,
        date=today
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log

@router.get(
    "/squads/{squad_id}/analytics",
    response_model=AnalyticsResponse
)
async def squad_analytics(
    squad_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    habits = db.query(Habit).filter(
        Habit.squad_id == squad_id
    ).all()

    members = db.query(SquadMember).filter(
        SquadMember.squad_id == squad_id
    ).all()

    total_habits = len(habits)
    total_members = len(members)

    if total_habits == 0 or total_members == 0:

        return AnalyticsResponse(
            current_streak=0,
            completion_rate=0,
            squad_average=0,
            who_broke_chain="No Data",
            missed_days=0
        )

    # ----------------------------
    # This Week
    # ----------------------------

    today = date.today()
    week_start = today - timedelta(days=6)

    logs = db.query(HabitLog).filter(
        HabitLog.date >= week_start,
        HabitLog.date <= today,
        HabitLog.completed == True
    ).all()

    total_possible = total_habits * total_members * 7

    completion_rate = (
        len(logs) / total_possible * 100
    )

    squad_average = completion_rate

    # ----------------------------
    # Who Broke Chain
    # ----------------------------

    worst_name = "Nobody"
    missed_days = 0

    for member in members:

        completed = db.query(HabitLog).filter(
            HabitLog.user_id == member.user_id,
            HabitLog.completed == True,
            HabitLog.date >= week_start
        ).count()

        missed = total_habits * 7 - completed

        if missed > missed_days:

            missed_days = missed

            user = db.query(User).filter(
                User.id == member.user_id
            ).first()

            if user:
                worst_name = user.name

    # ----------------------------
    # Current Streak
    # ----------------------------

    streak = 0

    for i in range(30):

        check_day = today - timedelta(days=i)

        count = db.query(HabitLog).filter(
            HabitLog.date == check_day,
            HabitLog.completed == True
        ).count()

        if count >= total_habits * total_members:
            streak += 1
        else:
            break

    return AnalyticsResponse(
        current_streak=streak,
        completion_rate=round(completion_rate, 2),
        squad_average=round(squad_average, 2),
        who_broke_chain=worst_name,
        missed_days=missed_days
    )