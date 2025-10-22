
from pydantic import BaseModel, Field
from typing import Optional, List, Any

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    role: str

class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str
    role: str

class FileCreate(BaseModel):
    sequence_no: Optional[int] = None
    debtor_name: str
    icra_dairesi: Optional[str] = None
    file_no: Optional[str] = None
    notice_date: Optional[str] = None
    original_debt: Optional[float] = None
    finalized_date: Optional[str] = None
    info: Optional[str] = None
    payment_plan: Optional[Any] = {}
    claimant: Optional[str] = None
    has_vehicle: Optional[bool] = False
    vehicle_id: Optional[str] = None
    sgk_info: Optional[str] = None
    bank_writings: Optional[Any] = {}
    swap_info: Optional[Any] = {}
    bank_id: Optional[int] = None
    property_id: Optional[str] = None
    post_mail: Optional[bool] = False
    cheque_info: Optional[Any] = {}
    payments: Optional[Any] = []
    sales_team: Optional[str] = None
    status: Optional[str] = "open"
    closed_reason: Optional[str] = None

class FileOut(BaseModel):
    id: str
    debtor_name: str
    file_no: Optional[str] = None
    original_debt: Optional[float] = None
    status: Optional[str] = None
    sequence_no: Optional[int] = None

class BulkDeleteRequest(BaseModel):
    ids: List[str]
