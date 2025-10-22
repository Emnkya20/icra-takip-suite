
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .config import JWT_SECRET, JWT_ALGO, ADMIN_EMAIL, ADMIN_PASSWORD
from .database import SessionLocal
from . import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(sub: str, expires_minutes: int = 120):
    to_encode = {"sub": sub, "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGO)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def hash_password(pw):
    return pwd_context.hash(pw)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(status_code=401, detail="Kimlik doğrulama başarısız")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == sub).first()
    if not user:
        raise credentials_exception
    return user

def require_roles(user: models.User, roles: list[str]):
    if user.role not in roles:
        raise HTTPException(status_code=403, detail="Yetkiniz yok")

def seed_admin(db: Session):
    # create default admin and seed banks
    admin = db.query(models.User).filter(models.User.email == ADMIN_EMAIL).first()
    if not admin:
        admin = models.User(email=ADMIN_EMAIL, full_name="System Admin", password_hash=hash_password(ADMIN_PASSWORD), role="sys_admin")
        db.add(admin)
    # seed banks
    bank_names = [
        "Ziraat Bankası","Vakıfbank","Türkiye İş Bankası","Garanti BBVA","Akbank","Yapı Kredi",
        "DenizBank","QNB Finansbank","TEB","ING Türkiye","Halkbank","Şekerbank","Fibabanka","HSBC Türkiye"
    ]
    for n in bank_names:
        if not db.query(models.Bank).filter(models.Bank.name==n).first():
            db.add(models.Bank(name=n, total_amount=0))
    db.commit()
