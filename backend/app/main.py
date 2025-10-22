
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import csv, io, os, shutil
from .database import Base, engine, SessionLocal
from . import models, schemas
from .auth import get_db, create_access_token, verify_password, hash_password, get_current_user, require_roles, seed_admin
from .config import UPLOAD_DIR

app = FastAPI(title="İcra Takip API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB
Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_admin(db)

@app.post("/auth/token", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Kullanıcı veya şifre hatalı")
    token = create_access_token(user.email)
    return {"access_token": token}

@app.post("/users", response_model=schemas.UserOut)
def create_user(payload: schemas.UserCreate, current=Depends(get_current_user), db: Session = Depends(get_db)):
    require_roles(current, ["sys_admin"])
    if db.query(models.User).filter(models.User.email==payload.email).first():
        raise HTTPException(status_code=400, detail="Email mevcut")
  pw = payload.password[:72]  # bcrypt sınırı için
u = models.User(
    email=payload.email,
    full_name=payload.full_name,
    password_hash=hash_password(pw),
    role=payload.role
)

    db.add(u); db.commit(); db.refresh(u)
    return {"id": str(u.id), "email": u.email, "full_name": u.full_name, "role": u.role}

@app.get("/dashboard/summary")
def dashboard_summary(current=Depends(get_current_user), db: Session = Depends(get_db)):
    # basit örnek: toplam tahsilat, açık/kapalı sayıları, toplam borç
    files = db.query(models.File).all()
    total_collected = 0
    total_debt = 0
    open_count = 0
    closed_count = 0
    for f in files:
        total_debt += float(f.original_debt or 0)
        if f.status == "open":
            open_count += 1
        else:
            closed_count += 1
        # payments JSON listesinde "amount" alanını topla
        if f.payments:
            try:
                for p in f.payments:
                    total_collected += float(p.get("amount",0))
            except Exception:
                pass
    return {
        "total_collected": round(total_collected,2),
        "total_debt": round(total_debt,2),
        "open_count": open_count,
        "closed_count": closed_count
    }

@app.post("/files", response_model=dict)
def create_file(payload: schemas.FileCreate, current=Depends(get_current_user), db: Session = Depends(get_db)):
    require_roles(current, ["sys_admin","file_manager"])
    f = models.File(
        sequence_no=payload.sequence_no,
        debtor_name=payload.debtor_name,
        icra_dairesi=payload.icra_dairesi,
        file_no=payload.file_no,
        info=payload.info,
        original_debt=payload.original_debt,
        claimant=payload.claimant,
        payment_plan=payload.payment_plan,
        has_vehicle=payload.has_vehicle,
        vehicle_id=payload.vehicle_id,
        sgk_info=payload.sgk_info,
        bank_writings=payload.bank_writings,
        swap_info=payload.swap_info,
        bank_id=payload.bank_id,
        property_id=payload.property_id,
        post_mail=payload.post_mail,
        cheque_info=payload.cheque_info,
        payments=payload.payments,
        sales_team=payload.sales_team,
        status=payload.status,
        closed_reason=payload.closed_reason,
        created_by=str(current.id)
    )
    db.add(f); db.commit(); db.refresh(f)
    return {"id": str(f.id), "status": "created"}

@app.get("/files", response_model=dict)
def list_files(page:int=1, size:int=50, status:str|None=None, current=Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(models.File)
    if status:
        q = q.filter(models.File.status==status)
    total = q.count()
    items = q.order_by(models.File.sequence_no.asc().nulls_last()).offset((page-1)*size).limit(size).all()
    def map_f(x):
        return {"id": str(x.id), "sequence_no": x.sequence_no, "debtor_name": x.debtor_name, "file_no": x.file_no, "original_debt": float(x.original_debt or 0), "status": x.status}
    return {"total": total, "items": [map_f(i) for i in items]}

@app.get("/files/{file_id}", response_model=dict)
def get_file(file_id: str, current=Depends(get_current_user), db: Session = Depends(get_db)):
    f = db.query(models.File).filter(models.File.id==file_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Dosya bulunamadı")
    return {
        "id": str(f.id),
        "sequence_no": f.sequence_no,
        "debtor_name": f.debtor_name,
        "icra_dairesi": f.icra_dairesi,
        "file_no": f.file_no,
        "original_debt": float(f.original_debt or 0),
        "payments": f.payments,
        "status": f.status,
        "closed_reason": f.closed_reason
    }

@app.put("/files/{file_id}", response_model=dict)
def update_file(file_id: str, payload: schemas.FileCreate, current=Depends(get_current_user), db: Session = Depends(get_db)):
    require_roles(current, ["sys_admin","file_manager"])
    f = db.query(models.File).filter(models.File.id==file_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Dosya bulunamadı")
    for k,v in payload.model_dump().items():
        setattr(f, k, v)
    db.commit()
    return {"id": file_id, "status": "updated"}

@app.post("/files/bulk-delete", response_model=dict)
def bulk_delete(body: schemas.BulkDeleteRequest, current=Depends(get_current_user), db: Session = Depends(get_db)):
    require_roles(current, ["sys_admin","file_manager"])
    count = 0
    for fid in body.ids:
        f = db.query(models.File).filter(models.File.id==fid).first()
        if f:
            db.delete(f); count += 1
    db.commit()
    return {"deleted": count}

@app.post("/files/import-csv", response_model=dict)
def import_csv(upload: UploadFile = File(...), current=Depends(get_current_user), db: Session = Depends(get_db)):
    require_roles(current, ["sys_admin","file_manager"])
    content = upload.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    inserted = 0; errors = []
    for i, row in enumerate(reader, start=2):
        try:
            f = models.File(
                sequence_no = int(row.get("sequence_no") or 0) or None,
                debtor_name = row["debtor_name"],
                icra_dairesi = row.get("icra_dairesi"),
                file_no = row.get("file_no"),
                original_debt = float(row.get("original_debt") or 0),
                status = row.get("status") or "open",
                payments = [],
                created_by = str(current.id)
            )
            db.add(f); inserted += 1
        except Exception as e:
            errors.append({"row": i, "error": str(e)})
    db.commit()
    return {"inserted": inserted, "errors": errors}

@app.post("/files/{file_id}/attachments", response_model=dict)
def upload_attachment(file_id: str, upload: UploadFile = File(...), current=Depends(get_current_user), db: Session = Depends(get_db)):
    require_roles(current, ["sys_admin","file_manager"])
    f = db.query(models.File).filter(models.File.id==file_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Dosya bulunamadı")
    dest_dir = os.path.join(UPLOAD_DIR, file_id)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, upload.filename)
    with open(dest, "wb") as out:
        shutil.copyfileobj(upload.file, out)
    att = models.Attachment(file_id=file_id, filename=upload.filename, stored_path=dest, uploaded_by=str(current.id))
    db.add(att); db.commit()
    return {"ok": True, "filename": upload.filename}
