from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user
from models import User, Squad, SquadMember, Habit, HabitLog
from schemas import LeaderboardMember

router = APIRouter()


@router.get(
    "/{squad_id}",
    response_model=list[LeaderboardMember]
)
async def leaderboard(
    squad_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    today = date.today()
    week_start = today - timedelta(days=6)
    squad = db.query(Squad).filter(
        Squad.id == squad_id
    ).first()

    if squad is None:
        return []

    members = db.query(SquadMember).filter(
        SquadMember.squad_id == squad_id
    ).all()

    habits = db.query(Habit).filter(
        Habit.squad_id == squad_id
    ).all()

    total_habits = len(habits)

    result = []

    for member in members:

        user = db.query(User).filter(
            User.id == member.user_id
        ).first()

        if user is None:
            continue

        # -----------------------
        # Current Streak
        # -----------------------

        streak = 0

        for i in range(30):

            check_day = today - timedelta(days=i)

            completed = db.query(HabitLog).filter(
                HabitLog.user_id == member.user_id,
                HabitLog.date == check_day,
                HabitLog.completed == True
            ).count()

            if completed >= total_habits:
                streak += 1
            else:
                break

        # -----------------------
        # Completion Rate
        # -----------------------

        completed_logs = db.query(HabitLog).filter(
            HabitLog.user_id == member.user_id,
            HabitLog.completed == True,
            HabitLog.date >= week_start
        ).count()

        total_possible = total_habits * 7

        completion_rate = 0

        if total_possible > 0:
            completion_rate = round(
                (completed_logs / total_possible) * 100,
                2
            )

        result.append({
            "name": user.name,
            "streak": streak,
            "completion_rate": completion_rate,
            "is_admin": squad.created_by == user.id


        })

    # Sort by streak first, then completion rate
    result.sort(
        key=lambda x: (
            x["streak"],
            x["completion_rate"]
        ),
        reverse=True
    )

    leaderboard = []

    for index, item in enumerate(result):

        leaderboard.append(
            LeaderboardMember(
                rank=index + 1,
                name=item["name"],
                streak=item["streak"],
                completion_rate=item["completion_rate"],
                 is_admin=item["is_admin"]

            )
        )

    return leaderboard