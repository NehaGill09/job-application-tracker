from datetime import date
import pytest
from app.models import Application
from app.services import parse_date, parse_money, validate_application

def test_parse_values():
    assert parse_date("2026-09-24")==date(2026,9,24)
    assert parse_money("75,000")==75000.0

def test_invalid_date():
    with pytest.raises(ValueError): parse_date("24/09/2026")

def test_validation():
    with pytest.raises(ValueError): validate_application(Application(company="",role="Developer"))
    with pytest.raises(ValueError):
        validate_application(Application(company="Acme",role="Developer",
                                         applied_date=date(2026,9,10),deadline=date(2026,9,1)))
