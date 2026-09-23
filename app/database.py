import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

from .models import Application, STATUSES

class Database:
    def __init__(self, path: str | Path = "job_tracker.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._init()

    def _init(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL, role TEXT NOT NULL, location TEXT DEFAULT '',
            job_url TEXT DEFAULT '', status TEXT NOT NULL DEFAULT 'Saved',
            applied_date TEXT, deadline TEXT, interview_date TEXT,
            salary_min REAL, salary_max REAL, notes TEXT DEFAULT '',
            contact TEXT DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_app_status ON applications(status);
        CREATE INDEX IF NOT EXISTS idx_app_deadline ON applications(deadline);
        CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        """)
        self.conn.commit()

    @staticmethod
    def _d(value: Optional[date]) -> Optional[str]:
        return value.isoformat() if value else None

    def add(self, app: Application) -> int:
        now = datetime.now().isoformat(timespec="seconds")
        cur = self.conn.execute("""INSERT INTO applications
        (company,role,location,job_url,status,applied_date,deadline,interview_date,
         salary_min,salary_max,notes,contact,created_at,updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (app.company.strip(),app.role.strip(),app.location.strip(),app.job_url.strip(),app.status,
         self._d(app.applied_date),self._d(app.deadline),self._d(app.interview_date),
         app.salary_min,app.salary_max,app.notes.strip(),app.contact.strip(),now,now))
        self.conn.commit()
        return int(cur.lastrowid)

    def update(self, app: Application):
        if app.id is None: raise ValueError("Application ID is required")
        self.conn.execute("""UPDATE applications SET company=?,role=?,location=?,job_url=?,status=?,
        applied_date=?,deadline=?,interview_date=?,salary_min=?,salary_max=?,notes=?,contact=?,updated_at=?
        WHERE id=?""",
        (app.company.strip(),app.role.strip(),app.location.strip(),app.job_url.strip(),app.status,
         self._d(app.applied_date),self._d(app.deadline),self._d(app.interview_date),
         app.salary_min,app.salary_max,app.notes.strip(),app.contact.strip(),
         datetime.now().isoformat(timespec="seconds"),app.id))
        self.conn.commit()

    def delete(self, app_id: int):
        self.conn.execute("DELETE FROM applications WHERE id=?", (app_id,))
        self.conn.commit()

    def get(self, app_id: int):
        return self.conn.execute("SELECT * FROM applications WHERE id=?", (app_id,)).fetchone()

    def list(self, search="", status="All", sort="updated_at DESC"):
        allowed={"updated_at DESC","deadline ASC","applied_date DESC","company ASC","status ASC"}
        sort=sort if sort in allowed else "updated_at DESC"
        clauses=[]; params=[]
        if search.strip():
            q=f"%{search.strip()}%"
            clauses.append("(company LIKE ? OR role LIKE ? OR location LIKE ? OR contact LIKE ? OR notes LIKE ?)")
            params.extend([q]*5)
        if status!="All":
            clauses.append("status=?"); params.append(status)
        where=(" WHERE "+" AND ".join(clauses)) if clauses else ""
        return self.conn.execute(f"SELECT * FROM applications{where} ORDER BY {sort}",params).fetchall()

    def stats(self):
        rows=self.conn.execute("SELECT status,COUNT(*) count FROM applications GROUP BY status").fetchall()
        counts={s:0 for s in STATUSES}; counts.update({r["status"]:r["count"] for r in rows})
        total=sum(counts.values())
        return {"total":total,"active":total-counts["Rejected"],
                "interviews":counts["Interview"]+counts["Offer"],"offers":counts["Offer"],"counts":counts}

    def upcoming(self, days=14):
        today=date.today(); end=today+timedelta(days=days)
        return self.conn.execute("""SELECT * FROM applications
        WHERE (deadline BETWEEN ? AND ?) OR (interview_date BETWEEN ? AND ?)
        ORDER BY COALESCE(interview_date,deadline)""",
        (today.isoformat(),end.isoformat(),today.isoformat(),end.isoformat())).fetchall()

    def due_count(self):
        today=date.today().isoformat()
        return self.conn.execute("""SELECT COUNT(*) FROM applications
        WHERE (deadline < ? AND status NOT IN ('Offer','Rejected')) OR interview_date = ?""",
        (today,today)).fetchone()[0]

    def close(self): self.conn.close()
