from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


_DEFAULT_REACH_OUT_TYPES = ["LinkedIn", "Email", "Phone", "InMail", "Referral", "Other"]


def _seed_reach_out_types():
    from models import ReachOutType
    db = SessionLocal()
    try:
        if db.query(ReachOutType).count() == 0:
            for name in _DEFAULT_REACH_OUT_TYPES:
                db.add(ReachOutType(name=name))
            db.commit()
    finally:
        db.close()


def _migrate_db():
    """Add columns introduced after initial schema creation."""
    new_columns = [
        ("job_type", "VARCHAR"),
        ("expected_wage", "INTEGER"),
        ("day_rate", "INTEGER"),
        ("contract_length", "VARCHAR"),
        ("agency_qualified", "BOOLEAN"),
        ("company_responded", "BOOLEAN"),
    ]
    with engine.connect() as conn:
        for col, col_type in new_columns:
            try:
                conn.execute(__import__("sqlalchemy").text(
                    f"ALTER TABLE applications ADD COLUMN {col} {col_type}"
                ))
                conn.commit()
            except Exception:
                pass  # column already exists


def init_db():
    from models import Application, Distance, AdvertSkill, ReachOutType, ContactLog, TargetCompany  # noqa: F401
    Base.metadata.create_all(bind=engine)
    _migrate_db()
    _seed_reach_out_types()
