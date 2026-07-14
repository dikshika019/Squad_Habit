from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@router.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )

@router.get("/habits")
async def habits_page(
    request: Request
):
    return templates.TemplateResponse(
        "habits.html",
        {
            "request": request
        }
    )

@router.get("/leaderboard")
async def leader_board(
    request: Request
):
    return templates.TemplateResponse(
        "leaderboard.html",
        {
            "request": request
        }
    )
@router.get("/at_risk")
async def leader_board(
    request: Request
):
    return templates.TemplateResponse(
        "at_risk.html",
        {
            "request": request
        }
    )