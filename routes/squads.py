import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import User, Squad, SquadMember, InviteLink
from schemas import SquadCreate, SquadResponse, InviteResponse, SquadMemberResponse


router = APIRouter()


# ------------------------------------
# Create Squad
# ------------------------------------
@router.post("/", response_model=SquadResponse)
async def create_squad(
    squad: SquadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    new_squad = Squad(
        name=squad.name,
        created_by=current_user.id
    )

    db.add(new_squad)
    db.commit()
    db.refresh(new_squad)

    # Creator automatically becomes member
    member = SquadMember(
        squad_id=new_squad.id,
        user_id=current_user.id
    )

    db.add(member)
    db.commit()

    return new_squad


# ------------------------------------
# Get My Squads
# ------------------------------------
@router.get("/", response_model=list[SquadResponse])
async def get_my_squads(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    squads = (
        db.query(Squad)
        .join(SquadMember, Squad.id == SquadMember.squad_id)
        .filter(SquadMember.user_id == current_user.id)
        .all()
    )

    return squads


# ------------------------------------
# Generate Invite Link
# ------------------------------------
@router.post("/{squad_id}/invite", response_model=InviteResponse)
async def generate_invite(
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

    token = str(uuid.uuid4())

    invite = InviteLink(
        squad_id=squad.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )

    db.add(invite)
    db.commit()
    db.refresh(invite)

    return {
        "invite_link":f"https://squadhabits.onrender.com/api/squads/invite/{token}",
        "expires_at": invite.expires_at
    }


# ------------------------------------
# Join Squad From Invite Link
# ------------------------------------
@router.get("/invite/{token}")
async def join_squad(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    invite = db.query(InviteLink).filter(
        InviteLink.token == token
    ).first()

    if invite is None:
        raise HTTPException(
            status_code=404,
            detail="Invalid invite link"
        )

    if invite.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="Invite link expired"
        )

    squad = db.query(Squad).filter(
        Squad.id == invite.squad_id
    ).first()

    if squad is None:
        raise HTTPException(
            status_code=404,
            detail="Squad not found"
        )

    already_member = db.query(SquadMember).filter(
        SquadMember.squad_id == squad.id,
        SquadMember.user_id == current_user.id
    ).first()

    if already_member is None:

        member = SquadMember(
            squad_id=squad.id,
            user_id=current_user.id
        )

        db.add(member)
        db.commit()

    return RedirectResponse(
        url="/dashboard",
        status_code=302
    )


# ------------------------------------
# Get Single Squad
# ------------------------------------
@router.get("/{squad_id}", response_model=SquadResponse)
async def get_squad(
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

    return squad

@router.get("/{squad_id}/members", response_model=list[SquadMemberResponse])
async def get_members(
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

    members = (
        db.query(User)
        .join(SquadMember, SquadMember.user_id == User.id)
        .filter(SquadMember.squad_id == squad_id)
        .all()
    )

    return members