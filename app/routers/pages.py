from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/schedule", response_class=HTMLResponse)
async def schedule_page(request: Request):
    return templates.TemplateResponse("schedule.html", {"request": request})

@router.get("/odontogram", response_class=HTMLResponse)
async def odontogram_page(request: Request):
    return templates.TemplateResponse("odontogram.html", {"request": request})

@router.get("/patients", response_class=HTMLResponse)
async def patients_page(request: Request):
    return templates.TemplateResponse("patients.html", {"request": request})

@router.get("/payments", response_class=HTMLResponse)
async def payments_page(request: Request):
    return templates.TemplateResponse("payments.html", {"request": request})

@router.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request})
