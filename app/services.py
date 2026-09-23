from datetime import date, datetime
from typing import Optional
from .models import Application, STATUSES

def parse_date(value: str) -> Optional[date]:
    value=value.strip()
    if not value: return None
    try: return datetime.strptime(value,"%Y-%m-%d").date()
    except ValueError as exc: raise ValueError("Dates must use YYYY-MM-DD format.") from exc

def parse_money(value: str) -> Optional[float]:
    value=value.strip().replace(",","")
    if not value: return None
    try: amount=float(value)
    except ValueError as exc: raise ValueError("Salary must be a valid number.") from exc
    if amount<0: raise ValueError("Salary cannot be negative.")
    return amount

def row_to_application(row):
    d=lambda k: parse_date(row[k]) if row[k] else None
    return Application(id=row["id"],company=row["company"],role=row["role"],location=row["location"],
        job_url=row["job_url"],status=row["status"],applied_date=d("applied_date"),
        deadline=d("deadline"),interview_date=d("interview_date"),salary_min=row["salary_min"],
        salary_max=row["salary_max"],notes=row["notes"],contact=row["contact"],
        created_at=row["created_at"],updated_at=row["updated_at"])

def validate_application(app: Application):
    if not app.company.strip(): raise ValueError("Company is required.")
    if not app.role.strip(): raise ValueError("Job title / role is required.")
    if app.status not in STATUSES: raise ValueError("Invalid application status.")
    if app.deadline and app.applied_date and app.deadline<app.applied_date:
        raise ValueError("Deadline cannot be before the applied date.")
    if app.salary_min is not None and app.salary_max is not None and app.salary_max<app.salary_min:
        raise ValueError("Maximum salary cannot be below minimum salary.")
