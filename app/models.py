from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Application:
    id: Optional[int] = None
    company: str = ""
    role: str = ""
    location: str = ""
    job_url: str = ""
    status: str = "Saved"
    applied_date: Optional[date] = None
    deadline: Optional[date] = None
    interview_date: Optional[date] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    notes: str = ""
    contact: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

STATUSES = ("Saved", "Applied", "Screening", "Interview", "Offer", "Rejected")
