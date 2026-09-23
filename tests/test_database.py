from datetime import date
from app.database import Database
from app.models import Application

def test_crud_and_stats(tmp_path):
    db=Database(tmp_path/"test.db")
    app=Application(company="Acme",role="Python Developer",status="Applied",applied_date=date(2026,9,20))
    app.id=db.add(app)
    assert db.get(app.id)["company"]=="Acme"
    assert db.stats()["total"]==1
    app.status="Interview"; db.update(app)
    assert db.stats()["interviews"]==1
    db.delete(app.id); assert db.stats()["total"]==0
    db.close()

def test_search(tmp_path):
    db=Database(tmp_path/"test.db")
    db.add(Application(company="Acme",role="Backend Engineer"))
    db.add(Application(company="Beta",role="Designer"))
    assert len(db.list("backend"))==1
    assert len(db.list("", "Designer"))==0
    db.close()
