from fastapi import APIRouter

router = APIRouter(prefix="/api/dropdowns", tags=["dropdowns"])

DROPDOWNS = {
    "status": [
        "Applied",
        "Phone Screen",
        "First Interview",
        "Second Interview",
        "Technical Test",
        "Final Interview",
        "Offer Received",
        "Rejected",
        "Withdrawn",
        "No Response",
        "Closed",
    ],
    "next_stage": [
        "Awaiting Response",
        "Phone Screen",
        "First Interview",
        "Second Interview",
        "Technical Test",
        "Final Interview",
        "Reference Check",
        "Offer",
        "None",
    ],
    "job_type": ["Permanent", "Contract"],
    "agency_or_direct": ["Direct", "Agency"],
    "applied_or_contacted": ["Applied", "Contacted"],
    "source": [
        "LinkedIn",
        "Indeed",
        "CV Library",
        "Reed",
        "Jobserve",
        "Recruiter",
        "Company Website",
        "Referral",
        "Other",
    ],
}


@router.get("")
def get_dropdowns() -> dict:
    return DROPDOWNS
