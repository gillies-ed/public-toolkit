import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import init_db
from routers import applications, distances, extract, stats, dropdowns, skills, interview_dates, advert_skills, contact_log, target_companies
from services.stale_checker import run_stale_check

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    # Run once at startup, then daily at 06:00
    run_stale_check()
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_stale_check, "cron", hour=10, minute=0)
    scheduler.start()
    logger.info("Stale-check scheduler started")

    yield

    scheduler.shutdown()


app = FastAPI(title="Job Tracker", lifespan=lifespan)

app.include_router(applications.router)
app.include_router(distances.router)
app.include_router(extract.router)
app.include_router(stats.router)
app.include_router(dropdowns.router)
app.include_router(skills.router)
app.include_router(interview_dates.router)
app.include_router(advert_skills.router)
app.include_router(contact_log.router)
app.include_router(target_companies.router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")


@app.get("/dashboard")
def dashboard():
    return FileResponse("static/dashboard.html")


@app.get("/distances")
def distances_page():
    return FileResponse("static/distances.html")


@app.get("/advert-skills")
def advert_skills_page():
    return FileResponse("static/skills-demand.html")


@app.get("/skills-demand")
def skills_demand_page():
    return FileResponse("static/skills-demand.html")


@app.get("/contact-log")
def contact_log_page():
    return FileResponse("static/contact-log.html")


@app.get("/contract")
def contract_page():
    return FileResponse("static/contract.html")


@app.get("/target-companies")
def target_companies_page():
    return FileResponse("static/target-companies.html")
