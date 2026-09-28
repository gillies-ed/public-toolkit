"""
Daily job: mark applications as 'No Response' when they go stale.

Two rules:
1. Applied + Awaiting Response with no update within 10 working days of the
   application date — catches retroactively-logged applications immediately.
2. Any active status where next_stage hasn't changed within the threshold since
   it was last updated (10 working days perm / 5 working days contract).
"""
from datetime import date, timedelta

from database import SessionLocal
from models import Application

_TERMINAL_STATUSES = {
    "Rejected", "Withdrawn", "Closed", "Offer Received", "No Response"
}


def _add_working_days(start: date, days: int) -> date:
    d = start
    added = 0
    while added < days:
        d += timedelta(days=1)
        if d.weekday() < 5:
            added += 1
    return d


def run_stale_check() -> int:
    """Mark stale applications as 'No Response'. Returns the count updated."""
    today = date.today()
    updated_count = 0

    db = SessionLocal()
    try:
        apps = (
            db.query(Application)
            .filter(Application.status.notin_(list(_TERMINAL_STATUSES)))
            .all()
        )

        for app in apps:
            already_updated = False

            # Rule 1: Applied + Awaiting Response — 10 working days from application date
            if (
                app.status == "Applied"
                and app.next_stage == "Awaiting Response"
                and app.date is not None
                and today >= _add_working_days(app.date, 10)
            ):
                app.status = "No Response"
                app.last_update = today
                updated_count += 1
                already_updated = True

            # Rule 2: any active status stale since next_stage was last touched
            if not already_updated and app.next_stage_updated is not None:
                threshold = 5 if app.job_type == "Contract" else 10
                if today >= _add_working_days(app.next_stage_updated, threshold):
                    app.status = "No Response"
                    app.last_update = today
                    updated_count += 1

        if updated_count:
            db.commit()
    finally:
        db.close()

    return updated_count
