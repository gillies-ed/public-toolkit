from datetime import date as _Date
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Distance schemas
# ---------------------------------------------------------------------------

class DistanceBase(BaseModel):
    city: str
    round_trip_miles: float


class DistanceCreate(DistanceBase):
    pass


class DistanceUpdate(BaseModel):
    city: str | None = None
    round_trip_miles: float | None = None


class DistanceOut(DistanceBase):
    id: int

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Interview date schemas (defined before ApplicationOut which references it)
# ---------------------------------------------------------------------------

class InterviewDateCreate(BaseModel):
    interview_date: _Date


class InterviewDateOut(BaseModel):
    id: int
    application_id: int
    interview_date: _Date

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Interview skills schemas
# ---------------------------------------------------------------------------

class SkillCreate(BaseModel):
    skill: str


class SkillOut(BaseModel):
    id: int
    application_id: int
    skill: str

    model_config = {"from_attributes": True}


class SkillFrequency(BaseModel):
    skill: str
    count: int


class AdvertSkillFrequency(BaseModel):
    skill: str
    count: int


# ---------------------------------------------------------------------------
# Contact log schemas
# ---------------------------------------------------------------------------

class ReachOutTypeOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class ContactLogBase(BaseModel):
    date: _Date | None = None
    name: str | None = None
    reach_out_type: str | None = None
    response: str | None = None
    notes: str | None = None


class ContactLogCreate(ContactLogBase):
    name: str


class ContactLogUpdate(ContactLogBase):
    pass


class ContactLogOut(ContactLogBase):
    id: int

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Application schemas
# ---------------------------------------------------------------------------

class ApplicationBase(BaseModel):
    date: _Date | None = None
    company: str | None = None
    agency_name: str | None = None
    agency_or_direct: str | None = None
    applied_or_contacted: str | None = None
    position: str | None = None
    job_type: str | None = None
    wage_max: int | None = None
    expected_wage: int | None = None
    day_rate: int | None = None
    contract_length: str | None = None
    location: str | None = None
    office_days: int | None = None
    round_trip_miles: float | None = None
    source: str | None = None
    last_update: _Date | None = None
    status: str | None = None
    next_stage: str | None = None
    next_stage_updated: _Date | None = None
    agency_qualified: bool | None = None
    company_responded: bool | None = None
    notes: str | None = None
    job_url: str | None = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(ApplicationBase):
    pass


class ApplicationOut(ApplicationBase):
    id: int
    interview_dates: list[InterviewDateOut] = []

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Extraction schemas
# ---------------------------------------------------------------------------

class ExtractUrlRequest(BaseModel):
    url: str


class ExtractTextRequest(BaseModel):
    text: str


class ExtractedFields(BaseModel):
    company: str | None = None
    position: str | None = None
    wage_max: int | None = None
    location: str | None = None
    office_days: int | None = None
    agency_name: str | None = None
    agency_or_direct: str | None = None


# ---------------------------------------------------------------------------
# Target companies schemas
# ---------------------------------------------------------------------------

class TargetCompanyBase(BaseModel):
    name: str | None = None
    location: str | None = None
    distance_miles: float | None = None
    category: str | None = None
    careers_url: str | None = None
    last_checked: _Date | None = None
    notes: str | None = None


class TargetCompanyCreate(TargetCompanyBase):
    name: str


class TargetCompanyUpdate(TargetCompanyBase):
    pass


class TargetCompanyOut(TargetCompanyBase):
    id: int

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Stats schema
# ---------------------------------------------------------------------------

class WeekBucket(BaseModel):
    week: str
    perm_count: int
    contract_count: int
    agency_contact_count: int
    company_contact_count: int


class StatsOut(BaseModel):
    total: int
    active: int
    interviews: int
    offers: int
    rejections: int
    no_responses: int
    perm_total: int
    perm_active: int
    perm_interviews: int
    perm_offers: int
    perm_rejections: int
    perm_no_responses: int
    contract_total: int
    contract_active: int
    contract_interviews: int
    contract_offers: int
    contract_rejections: int
    contract_no_responses: int
    by_status: dict[str, int]
    by_status_perm: dict[str, int]
    by_status_contract: dict[str, int]
    by_source: dict[str, int]
    weekly: list[WeekBucket]
