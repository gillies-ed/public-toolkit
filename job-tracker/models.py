from datetime import date, datetime
from sqlalchemy import Integer, String, Float, Date, DateTime, Text, ForeignKey, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    date: Mapped[date | None] = mapped_column(Date, nullable=True)
    company: Mapped[str | None] = mapped_column(String, nullable=True)
    agency_name: Mapped[str | None] = mapped_column(String, nullable=True)
    agency_or_direct: Mapped[str | None] = mapped_column(String, nullable=True)   # Agency | Direct
    applied_or_contacted: Mapped[str | None] = mapped_column(String, nullable=True)  # Applied | Contacted
    position: Mapped[str] = mapped_column(String, nullable=False)
    job_type: Mapped[str | None] = mapped_column(String, nullable=True)   # Permanent | Contract
    wage_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expected_wage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    day_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    contract_length: Mapped[str | None] = mapped_column(String, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    office_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    round_trip_miles: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str | None] = mapped_column(String, nullable=True)
    last_update: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)
    next_stage: Mapped[str | None] = mapped_column(String, nullable=True)
    next_stage_updated: Mapped[date | None] = mapped_column(Date, nullable=True)
    agency_qualified: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    company_responded: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    job_url: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    skills: Mapped[list["InterviewSkill"]] = relationship("InterviewSkill", back_populates="application", cascade="all, delete-orphan")
    interview_dates: Mapped[list["InterviewDate"]] = relationship("InterviewDate", back_populates="application", cascade="all, delete-orphan", order_by="InterviewDate.interview_date")


class InterviewDate(Base):
    __tablename__ = "interview_dates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("applications.id"), nullable=False)
    interview_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    application: Mapped["Application"] = relationship("Application", back_populates="interview_dates")


class InterviewSkill(Base):
    __tablename__ = "interview_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("applications.id"), nullable=False)
    skill: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    application: Mapped["Application"] = relationship("Application", back_populates="skills")


class Distance(Base):
    __tablename__ = "distances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    city: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    round_trip_miles: Mapped[float] = mapped_column(Float, nullable=False)


class AdvertSkill(Base):
    """One row per sighting of a skill in a job advert. Count by grouping skill name."""
    __tablename__ = "advert_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    skill: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class TargetCompany(Base):
    __tablename__ = "target_companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    distance_miles: Mapped[float | None] = mapped_column(Float, nullable=True)
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    careers_url: Mapped[str | None] = mapped_column(String, nullable=True)
    last_checked: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ReachOutType(Base):
    __tablename__ = "reach_out_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)


class ContactLog(Base):
    __tablename__ = "contact_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    date: Mapped[date | None] = mapped_column(Date, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    reach_out_type: Mapped[str | None] = mapped_column(String, nullable=True)
    response: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
