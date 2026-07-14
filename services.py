from datetime import datetime, timedelta

def calculate_streak(user_id: UUID, habit_id: UUID, db: Session) -> int:
    """Calculate current streak for a user's habit"""
    logs = db.query(HabitLog).filter(
        HabitLog.user_id == user_id,
        HabitLog.habit_id == habit_id
    ).order_by(HabitLog.date.desc()).all()
    
    streak = 0
    today = datetime.utcnow().date()
    
    for log in logs:
        log_date = log.date.date() if hasattr(log.date, 'date') else log.date
        if log_date == today - timedelta(days=streak) and log.completed:
            streak += 1
        else:
            break
    
    return streak

def calculate_completion_rate(user_id: UUID, squad_id: UUID, db: Session) -> float:
    """Calculate completion rate for a user in a squad over the last 7 days"""
    habits = db.query(Habit).filter(Habit.squad_id == squad_id).all()
    if not habits:
        return 0.0
    
    total_required = len(habits) * 7  # 7 days * number of habits
    completed = 0
    
    for day in range(7):
        date = datetime.utcnow().date() - timedelta(days=day)
        for habit in habits:
            log = db.query(HabitLog).filter(
                HabitLog.habit_id == habit.id,
                HabitLog.user_id == user_id,
                HabitLog.date == date
            ).first()
            if log and log.completed:
                completed += 1
    
    return (completed / total_required) * 100 if total_required > 0 else 0