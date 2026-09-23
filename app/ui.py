import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser

from .database import Database
from .models import Application, STATUSES
from .reports import export_csv, export_excel, export_json, export_pdf
from .services import parse_date, parse_money, row_to_application, validate_application

class JobTrackerApp:
    def __init__(self):
        self.db=Database(); self.root=tk.Tk()
        self.root.title("Job Application Tracker Pro"); self.root.geometry("1250x780"); self.root.minsize(1050,680)
        self.selected_id=None
        self.vars={k:tk.StringVar() for k in ["company","role","location","url","status","applied","deadline","interview","salary_min","salary_max","contact","search","filter"]}
        self.vars["status"].set("Applied"); self.vars["filter"].set("All")
        self._style(); self._build()

    def _style(self):
        s=ttk.Style()
        try: s.theme_use("clam")
        except tk.TclError: pass
        s.configure("Title.TLabel",font=("TkDefaultFont",22,"bold"))
        s.configure("CardValue.TLabel",font=("TkDefaultFont",20,"bold"))
        s.configure("Treeview",rowheight=30)
        s.configure("Accent.TButton",font=("TkDefaultFont",10,"bold"))

    def _build(self):
        top=ttk.Frame(self.root,padding=18); top.pack(fill="x")
        ttk.Label(top,text="JOB APPLICATION TRACKER",style="Title.TLabel").pack(side="left")
        ttk.Button(top,text="Export",command=self.export_menu).pack(side="right",padx=5)
        ttk.Button(top,text="Refresh",command=self.refresh).pack(side="right")
        self.notices=ttk.Label(self.root,padding=(18,0)); self.notices.pack(fill="x")
        self.nb=ttk.Notebook(self.root); self.nb.pack(fill="both",expand=True,padx=14,pady=12)
        self.dashboard_tab=ttk.Frame(self.nb,padding=18); self.apps_tab=ttk.Frame(self.nb,padding=12); self.form_tab=ttk.Frame(self.nb,padding=18)
        self.nb.add(self.dashboard_tab,text="Dashboard"); self.nb.add(self.apps_tab,text="Applications"); self.nb.add(self.form_tab,text="Add / Edit")
        self._dashboard(); self._applications(); self._form(); self.refresh()

    def _dashboard(self):
        cards=ttk.Frame(self.dashboard_tab); cards.pack(fill="x"); self.card_values={}
        for key,label in [("total","Applications"),("active","Active"),("interviews","Interviews / Offers"),("offers","Offers")]:
            f=ttk.Frame(cards,padding=18); f.pack(side="left",fill="both",expand=True,padx=5)
            ttk.Label(f,text=label).pack(anchor="w")
            v=ttk.Label(f,text="0",style="CardValue.TLabel"); v.pack(anchor="w",pady=(8,0)); self.card_values[key]=v
        body=ttk.Panedwindow(self.dashboard_tab,orient="horizontal"); body.pack(fill="both",expand=True,pady=20)
        left=ttk.Frame(body,padding=8); right=ttk.Frame(body,padding=8); body.add(left,weight=1); body.add(right,weight=1)
        ttk.Label(left,text="Pipeline",font=("TkDefaultFont",14,"bold")).pack(anchor="w",pady=6)
        self.pipeline=ttk.Treeview(left,columns=("status","count"),show="headings",height=9)
        self.pipeline.heading("status",text="Status"); self.pipeline.heading("count",text="Count"); self.pipeline.column("count",width=80,anchor="center"); self.pipeline.pack(fill="x")
        ttk.Label(right,text="Upcoming deadlines & interviews",font=("TkDefaultFont",14,"bold")).pack(anchor="w",pady=6)
        self.upcoming=ttk.Treeview(right,columns=("date","company","role","type"),show="headings",height=9)
        for c,t in [("date","Date"),("company","Company"),("role","Role"),("type","Type")]:
            self.upcoming.heading(c,text=t)
        self.upcoming.column("date",width=95); self.upcoming.pack(fill="both",expand=True)

    def _applications(self):
        bar=ttk.Frame(self.apps_tab); bar.pack(fill="x",pady=(0,10))
        ttk.Label(bar,text="Search").pack(side="left"); ttk.Entry(bar,textvariable=self.vars["search"],width=32).pack(side="left",padx=6)
        ttk.Label(bar,text="Status").pack(side="left")
        ttk.Combobox(bar,textvariable=self.vars["filter"],values=("All",)+STATUSES,state="readonly",width=14).pack(side="left",padx=6)
        ttk.Button(bar,text="Search",command=self.refresh_table).pack(side="left",padx=3)
        ttk.Button(bar,text="Clear",command=self.clear_search).pack(side="left",padx=3)
        ttk.Button(bar,text="Edit",command=self.edit_selected).pack(side="right",padx=3)
        ttk.Button(bar,text="Delete",command=self.delete_selected).pack(side="right",padx=3)
        cols=("company","role","location","status","applied","deadline","interview","salary")
        self.table=ttk.Treeview(self.apps_tab,columns=cols,show="headings")
        headings={"company":"Company","role":"Role","location":"Location","status":"Status","applied":"Applied","deadline":"Deadline","interview":"Interview","salary":"Salary"}
        for c in cols: self.table.heading(c,text=headings[c]); self.table.column(c,width=120)
        self.table.column("company",width=180); self.table.column("role",width=190); self.table.column("salary",width=130)
        self.table.pack(fill="both",expand=True); self.table.bind("<Double-1>",lambda e:self.edit_selected())

    def _form(self):
        frame=self.form_tab
        fields=[("company","Company *"),("role","Job title / Role *"),("location","Location"),("url","Job URL"),
                ("applied","Applied date"),("deadline","Deadline"),("interview","Interview date"),("salary_min","Salary min"),
                ("salary_max","Salary max"),("contact","Contact")]
        for i,(key,label) in enumerate(fields):
            r=i//2; c=(i%2)*2
            ttk.Label(frame,text=label).grid(row=r,column=c,padx=8,pady=8,sticky="w")
            ttk.Entry(frame,textvariable=self.vars[key],width=38).grid(row=r,column=c+1,padx=8,pady=8,sticky="ew")
        r=(len(fields)+1)//2
        ttk.Label(frame,text="Status").grid(row=r,column=0,padx=8,pady=8,sticky="w")
        ttk.Combobox(frame,textvariable=self.vars["status"],values=STATUSES,state="readonly",width=35).grid(row=r,column=1,padx=8,pady=8,sticky="ew")
        ttk.Label(frame,text="Notes").grid(row=r+1,column=0,padx=8,pady=8,sticky="nw")
        self.notes=tk.Text(frame,height=10,width=80); self.notes.grid(row=r+1,column=1,columnspan=3,padx=8,pady=8,sticky="nsew")
        for c in range(4): frame.columnconfigure(c,weight=1)
        frame.rowconfigure(r+1,weight=1)
        buttons=ttk.Frame(frame); buttons.grid(row=r+2,column=0,columnspan=4,pady=12)
        ttk.Button(buttons,text="Save Application",style="Accent.TButton",command=self.save).pack(side="left",padx=5)
        ttk.Button(buttons,text="Clear Form",command=self.clear_form).pack(side="left",padx=5)
        ttk.Button(buttons,text="Open Job URL",command=self.open_url).pack(side="left",padx=5)

    def refresh(self):
        s=self.db.stats()
        for k in ("total","active","interviews","offers"): self.card_values[k].config(text=str(s[k]))
        for i in self.pipeline.get_children(): self.pipeline.delete(i)
        for status in STATUSES: self.pipeline.insert("", "end",values=(status,s["counts"][status]))
        for i in self.upcoming.get_children(): self.upcoming.delete(i)
        for r in self.db.upcoming(14):
            d=r["interview_date"] or r["deadline"]; typ="Interview" if r["interview_date"] else "Deadline"
            self.upcoming.insert("", "end",values=(d,r["company"],r["role"],typ))
        due=self.db.due_count()
        self.notices.config(text=f"⚠ {due} item(s) need attention." if due else "You're all caught up.")
        self.refresh_table()

    def refresh_table(self):
        for i in self.table.get_children(): self.table.delete(i)
        for r in self.db.list(self.vars["search"].get(),self.vars["filter"].get()):
            salary="" if r["salary_min"] is None and r["salary_max"] is None else f"{r['salary_min'] or ''} - {r['salary_max'] or ''}"
            self.table.insert("", "end",iid=str(r["id"]),values=(r["company"],r["role"],r["location"],r["status"],
                r["applied_date"] or "",r["deadline"] or "",r["interview_date"] or "",salary))

    def clear_search(self):
        self.vars["search"].set(""); self.vars["filter"].set("All"); self.refresh_table()

    def save(self):
        try:
            app=Application(id=self.selected_id,company=self.vars["company"].get(),role=self.vars["role"].get(),
                location=self.vars["location"].get(),job_url=self.vars["url"].get(),status=self.vars["status"].get(),
                applied_date=parse_date(self.vars["applied"].get()),deadline=parse_date(self.vars["deadline"].get()),
                interview_date=parse_date(self.vars["interview"].get()),salary_min=parse_money(self.vars["salary_min"].get()),
                salary_max=parse_money(self.vars["salary_max"].get()),contact=self.vars["contact"].get(),
                notes=self.notes.get("1.0","end").strip())
            validate_application(app)
            if app.id: self.db.update(app); msg="Application updated."
            else: self.db.add(app); msg="Application saved."
            self.clear_form(); self.refresh(); messagebox.showinfo("Saved",msg); self.nb.select(self.apps_tab)
        except ValueError as e: messagebox.showerror("Validation error",str(e))

    def edit_selected(self):
        sel=self.table.selection()
        if not sel: messagebox.showinfo("Select an application","Choose an application first."); return
        app=row_to_application(self.db.get(int(sel[0]))); self.selected_id=app.id
        vals={"company":app.company,"role":app.role,"location":app.location,"url":app.job_url,"status":app.status,
              "applied":app.applied_date.isoformat() if app.applied_date else "","deadline":app.deadline.isoformat() if app.deadline else "",
              "interview":app.interview_date.isoformat() if app.interview_date else "","salary_min":app.salary_min or "",
              "salary_max":app.salary_max or "","contact":app.contact}
        for k,v in vals.items(): self.vars[k].set(str(v))
        self.notes.delete("1.0","end"); self.notes.insert("1.0",app.notes); self.nb.select(self.form_tab)

    def delete_selected(self):
        sel=self.table.selection()
        if sel and messagebox.askyesno("Delete","Delete the selected application?"):
            self.db.delete(int(sel[0])); self.refresh()

    def clear_form(self):
        self.selected_id=None
        for k in self.vars:
            if k not in ("search","filter"): self.vars[k].set("")
        self.vars["status"].set("Applied"); self.notes.delete("1.0","end")

    def open_url(self):
        url=self.vars["url"].get().strip()
        if url: webbrowser.open(url if url.startswith(("http://","https://")) else "https://"+url)

    def export_menu(self):
        choice=messagebox.askyesnocancel("Export",
            "Yes = Excel\nNo = CSV\nCancel = stop")
        if choice is None: return
        ext=".xlsx" if choice else ".csv"
        path=filedialog.asksaveasfilename(defaultextension=ext,
            filetypes=[("Excel","*.xlsx"),("CSV","*.csv")])
        if not path: return
        try:
            (export_excel if choice else export_csv)(
                self.db,path,self.vars["search"].get(),self.vars["filter"].get())
            messagebox.showinfo("Export complete",f"Saved to:\n{path}")
        except Exception as e: messagebox.showerror("Export failed",str(e))

    def export_report(self, kind):
        defaults={"pdf":("PDF report","*.pdf"),"json":("JSON report","*.json")}
        label,pattern=defaults[kind]
        path=filedialog.asksaveasfilename(defaultextension=pattern[1:],filetypes=[(label,pattern)])
        if not path: return
        try:
            (export_pdf if kind=="pdf" else export_json)(self.db,path)
            messagebox.showinfo("Report complete",f"Saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Report failed",str(e))

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW",self.close); self.root.mainloop()

    def close(self):
        self.db.close(); self.root.destroy()
