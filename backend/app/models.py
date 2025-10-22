
from sqlalchemy import Column, String, Date, DateTime, Integer, Numeric, Boolean, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func
import uuid
from .database import Base

def UUIDCol():
    try:
        from sqlalchemy.dialects.postgresql import UUID
        return Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    except Exception:
        return Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

class User(Base):
    __tablename__ = "users"
    id = UUIDCol()
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # sys_admin, file_manager, viewer, sales
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Bank(Base):
    __tablename__ = "banks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    total_amount = Column(Numeric(18,2), default=0)

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = UUIDCol()
    plate = Column(String)
    make = Column(String)
    model = Column(String)
    year = Column(Integer)
    has_haciz = Column(Boolean, default=False)
    haciz_count = Column(Integer, default=0)
    extra = Column(JSON, default={})

class Property(Base):
    __tablename__ = "properties"
    id = UUIDCol()
    address = Column(Text)
    deed_no = Column(String)
    sale_allowed = Column(Boolean, default=False)
    notes = Column(Text)

class File(Base):
    __tablename__ = "files"
    id = UUIDCol()
    sequence_no = Column(Integer)
    debtor_name = Column(String, nullable=False)
    icra_dairesi = Column(String)
    file_no = Column(String)
    notice_date = Column(Date)
    original_debt = Column(Numeric(18,2))
    finalized_date = Column(Date)
    info = Column(Text)
    payment_plan = Column(JSON, default={})
    claimant = Column(String)
    has_vehicle = Column(Boolean, default=False)
    vehicle_id = Column(String, ForeignKey("vehicles.id"))
    sgk_info = Column(Text)
    bank_writings = Column(JSON, default={})
    swap_info = Column(JSON, default={})
    bank_id = Column(Integer, ForeignKey("banks.id"))
    property_id = Column(String, ForeignKey("properties.id"))
    post_mail = Column(Boolean, default=False)
    cheque_info = Column(JSON, default={})
    payments = Column(JSON, default=[])
    sales_team = Column(String)
    status = Column(String, default="open")  # open, closed, forgiven, etc.
    closed_reason = Column(String)  # tahsil, feragat, etc.
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Attachment(Base):
    __tablename__ = "attachments"
    id = UUIDCol()
    file_id = Column(String, ForeignKey("files.id", ondelete="CASCADE"))
    filename = Column(String)
    stored_path = Column(String)
    uploaded_by = Column(String, ForeignKey("users.id"))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
