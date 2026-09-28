from datetime import date, timedelta
from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Application
from schemas import StatsOut, WeekBucket

router = APIRouter(prefix="/api/stats", tags=["stats"])

_ACTIVE_STATUSES = {"Applied", "Phone Screen", "First Interview", "Second Interview", "Technical Test"}
_INTERVIEW_STATUSES = {"First Interview", "Second Interview", "Technical Test", "Final Interview"}
_OFFER_STATUSES = {"Offer Received"}
_REJECTION_STATUSES = {"Rejected", "Withdrawn", "Closed"}
_NO_RESPONSE_STATUSES = {"No Response"}


@router.get("", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db)):
    apps = db.query(Application).options(joinedload(Application.interview_dates)).all()

    perm = [a for a in apps if a.job_type != "Contract"]
    contract = [a for a in apps if a.job_type == "Contract"]

    def _had_interview(a: Application) -> bool:
        return a.status in _INTERVIEW_STATUSES or bool(a.interview_dates)

    total = len(apps)
    active = sum(1 for a in apps if a.status in _ACTIVE_STATUSES)
    interviews = sum(1 for a in apps if _had_interview(a))
    offers = sum(1 for a in apps if a.status in _OFFER_STATUSES)
    rejections = sum(1 for a in apps if a.status in _REJECTION_STATUSES)
    no_responses = sum(1 for a in apps if a.status in _NO_RESPONSE_STATUSES)

    perm_total = len(perm)
    perm_active = sum(1 for a in perm if a.status in _ACTIVE_STATUSES)
    perm_interviews = sum(1 for a in perm if _had_interview(a))
    perm_offers = sum(1 for a in perm if a.status in _OFFER_STATUSES)
    perm_rejections = sum(1 for a in perm if a.status in _REJECTION_STATUSES)
    perm_no_responses = sum(1 for a in perm if a.status in _NO_RESPONSE_STATUSES)

    contract_total = len(contract)
    contract_active = sum(1 for a in contract if a.status in _ACTIVE_STATUSES)
    contract_interviews = sum(1 for a in contract if _had_interview(a))
    contract_offers = sum(1 for a in contract if a.status in _OFFER_STATUSES)
    contract_rejections = sum(1 for a in contract if a.status in _REJECTION_STATUSES)
    contract_no_responses = sum(1 for a in contract if a.status in _NO_RESPONSE_STATUSES)

    by_status: dict[str, int] = defaultdict(int)
    by_status_perm: dict[str, int] = defaultdict(int)
    by_status_contract: dict[str, int] = defaultdict(int)
    by_source: dict[str, int] = defaultdict(int)
    for a in apps:
        if a.status:
            by_status[a.status] += 1
            if a.job_type == "Contract":
                by_status_contract[a.status] += 1
            else:
                by_status_perm[a.status] += 1
        if a.source:
            by_source[a.source] += 1

    # Weekly buckets — last 12 weeks (Monday-based)
    today = date.today()
    current_monday = today - timedelta(days=today.weekday())
    weekly_perm: dict[date, int] = defaultdict(int)
    weekly_contract: dict[date, int] = defaultdict(int)
    weekly_agency_contact: dict[date, int] = defaultdict(int)
    weekly_company_contact: dict[date, int] = defaultdict(int)
    for a in apps:
        if a.date:
            week_start = a.date - timedelta(days=a.date.weekday())
            if a.job_type == "Contract":
                weekly_contract[week_start] += 1
            else:
                weekly_perm[week_start] += 1
            if a.applied_or_contacted == "Contacted":
                if a.agency_or_direct == "Agency":
                    weekly_agency_contact[week_start] += 1
                elif a.agency_or_direct == "Direct":
                    weekly_company_contact[week_start] += 1

    weekly: list[WeekBucket] = []
    for i in range(11, -1, -1):
        week_start = current_monday - timedelta(weeks=i)
        weekly.append(WeekBucket(
            week=week_start.strftime("%d %b"),
            perm_count=weekly_perm.get(week_start, 0),
            contract_count=weekly_contract.get(week_start, 0),
            agency_contact_count=weekly_agency_contact.get(week_start, 0),
            company_contact_count=weekly_company_contact.get(week_start, 0),
        ))

    return StatsOut(
        total=total,
        active=active,
        interviews=interviews,
        offers=offers,
        rejections=rejections,
        no_responses=no_responses,
        perm_total=perm_total,
        perm_active=perm_active,
        perm_interviews=perm_interviews,
        perm_offers=perm_offers,
        perm_rejections=perm_rejections,
        perm_no_responses=perm_no_responses,
        contract_total=contract_total,
        contract_active=contract_active,
        contract_interviews=contract_interviews,
        contract_offers=contract_offers,
        contract_rejections=contract_rejections,
        contract_no_responses=contract_no_responses,
        by_status=dict(by_status),
        by_status_perm=dict(by_status_perm),
        by_status_contract=dict(by_status_contract),
        by_source=dict(by_source),
        weekly=weekly,
    )
