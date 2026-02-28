"""Enterprise legacy system simulation models.

Three systems modeled after real municipal tools:
1. IBM Maximo (Enterprise Asset Management)
2. Tyler Technologies Incode (Court Case Management)
3. e-Builder / Trimble Unity Construct (Capital Improvement Program)

All data is SYNTHETIC. Table/column names approximate real schemas
for training purposes but contain no proprietary information.
"""

import enum
from datetime import date, datetime
from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum, Float, Integer,
    String, Text,
)
from sqlalchemy.sql import func
from app.db.session import Base


# ============================================================
#  IBM MAXIMO — Enterprise Asset Management
# ============================================================

class MaximoWOStatus(str, enum.Enum):
    WAPPR = "WAPPR"       # Waiting Approval
    APPR = "APPR"         # Approved
    INPRG = "INPRG"       # In Progress
    COMP = "COMP"         # Complete
    CLOSE = "CLOSE"       # Closed
    CAN = "CAN"           # Cancelled
    WMATL = "WMATL"       # Waiting Material
    WSCH = "WSCH"         # Waiting Schedule


class MaximoAssetStatus(str, enum.Enum):
    OPERATING = "OPERATING"
    NOT_READY = "NOT READY"
    DECOMMISSIONED = "DECOMMISSIONED"
    BROKEN = "BROKEN"


class MaximoPMStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DRAFT = "DRAFT"


class MaximoWorkOrder(Base):
    __tablename__ = "mx_workorder"
    wonum = Column(String(20), primary_key=True)
    description = Column(String(200), nullable=False)
    longdescription = Column(Text, nullable=True)
    status = Column(Enum(MaximoWOStatus), default=MaximoWOStatus.WAPPR, index=True)
    statusdate = Column(DateTime, server_default=func.now())
    worktype = Column(String(10), nullable=True)
    assetnum = Column(String(30), nullable=True, index=True)
    location = Column(String(30), nullable=True, index=True)
    siteid = Column(String(10), default="CCTX")
    orgid = Column(String(10), default="CCORG")
    reportdate = Column(DateTime, server_default=func.now())
    targstartdate = Column(DateTime, nullable=True)
    targcompdate = Column(DateTime, nullable=True)
    actstart = Column(DateTime, nullable=True)
    actfinish = Column(DateTime, nullable=True)
    priority = Column(Integer, nullable=True)
    wopriority = Column(Integer, nullable=True)
    pmnum = Column(String(20), nullable=True)
    parent = Column(String(20), nullable=True)
    glaccount = Column(String(30), nullable=True)
    estdur = Column(Float, nullable=True)
    actlabhrs = Column(Float, default=0.0)
    actmatcost = Column(Float, default=0.0)
    actlabcost = Column(Float, default=0.0)
    reportedby = Column(String(30), nullable=True)
    supervisor = Column(String(30), nullable=True)
    lead = Column(String(30), nullable=True)
    woacceptscharges = Column(Boolean, default=True)
    crewid = Column(String(20), nullable=True)
    failurecode = Column(String(20), nullable=True)


class MaximoAsset(Base):
    __tablename__ = "mx_asset"
    assetnum = Column(String(30), primary_key=True)
    description = Column(String(200), nullable=False)
    status = Column(Enum(MaximoAssetStatus), default=MaximoAssetStatus.OPERATING, index=True)
    assettype = Column(String(20), nullable=True)
    location = Column(String(30), nullable=True, index=True)
    siteid = Column(String(10), default="CCTX")
    serialnum = Column(String(30), nullable=True)
    vendor = Column(String(30), nullable=True)
    manufacturer = Column(String(30), nullable=True)
    purchaseprice = Column(Float, nullable=True)
    installdate = Column(Date, nullable=True)
    warrantyexpdate = Column(Date, nullable=True)
    totdowntime = Column(Float, default=0.0)
    ytdcost = Column(Float, default=0.0)
    replacecost = Column(Float, nullable=True)
    isrunning = Column(Boolean, default=True)
    parent = Column(String(30), nullable=True)
    groupname = Column(String(20), nullable=True)
    calnum = Column(String(10), nullable=True)


class MaximoLocation(Base):
    __tablename__ = "mx_locations"
    location = Column(String(30), primary_key=True)
    description = Column(String(200), nullable=False)
    type = Column(String(20), nullable=True)
    siteid = Column(String(10), default="CCTX")
    status = Column(String(20), default="OPERATING")
    streetaddress = Column(String(100), nullable=True)
    cityname = Column(String(50), default="Corpus Christi")
    stateprovince = Column(String(2), default="TX")


class MaximoPM(Base):
    __tablename__ = "mx_pm"
    pmnum = Column(String(20), primary_key=True)
    description = Column(String(200), nullable=False)
    status = Column(Enum(MaximoPMStatus), default=MaximoPMStatus.ACTIVE, index=True)
    siteid = Column(String(10), default="CCTX")
    assetnum = Column(String(30), nullable=True)
    location = Column(String(30), nullable=True)
    frequency = Column(Integer, nullable=True)
    frequnit = Column(String(10), nullable=True)
    nextdate = Column(Date, nullable=True)
    lastcompdate = Column(Date, nullable=True)
    wonum = Column(String(20), nullable=True)
    leadtime = Column(Float, nullable=True)
    priority = Column(Integer, nullable=True)
    jpnum = Column(String(20), nullable=True)


class MaximoServiceRequest(Base):
    __tablename__ = "mx_sr"
    ticketid = Column(String(20), primary_key=True)
    description = Column(String(200), nullable=False)
    status = Column(String(20), default="NEW", index=True)
    reportdate = Column(DateTime, server_default=func.now())
    reportedby = Column(String(30), nullable=True)
    affectedperson = Column(String(30), nullable=True)
    assetnum = Column(String(30), nullable=True)
    location = Column(String(30), nullable=True)
    siteid = Column(String(10), default="CCTX")
    classstructureid = Column(String(20), nullable=True)
    urgency = Column(Integer, nullable=True)
    ownergroup = Column(String(20), nullable=True)
    owner = Column(String(30), nullable=True)


class MaximoCronTask(Base):
    __tablename__ = "mx_crontaskdef"
    crontaskname = Column(String(30), primary_key=True)
    description = Column(String(200), nullable=False)
    classname = Column(String(200), nullable=True)
    schedule = Column(String(50), nullable=True)
    active = Column(Boolean, default=True)
    runasstartup = Column(Boolean, default=False)
    lastrun = Column(DateTime, nullable=True)
    nextrun = Column(DateTime, nullable=True)
    instancename = Column(String(30), default="PMWOGEN01")
    hasld = Column(Boolean, default=False)


class MaximoIntMessage(Base):
    __tablename__ = "mx_maxintmsgtrk"
    msgid = Column(Integer, primary_key=True, autoincrement=True)
    extsysname = Column(String(30), nullable=False)
    ifacename = Column(String(30), nullable=False)
    messagetype = Column(String(20), nullable=True)
    status = Column(String(20), default="ERROR", index=True)
    msgerror = Column(Text, nullable=True)
    msgdata = Column(Text, nullable=True)
    createdate = Column(DateTime, server_default=func.now())


# ============================================================
#  TYLER TECHNOLOGIES INCODE — Court Case Management
# ============================================================

class IncodeCaseStatus(str, enum.Enum):
    OPEN = "OPEN"
    DISPOSED = "DISPOSED"
    DISMISSED = "DISMISSED"
    DEFERRED = "DEFERRED"
    WARRANT = "WARRANT"
    FTA = "FTA"
    PAID = "PAID"
    APPEAL = "APPEAL"


class IncodeCitation(Base):
    __tablename__ = "ic_citation"
    citation_number = Column(String(20), primary_key=True)
    violation_code = Column(String(20), nullable=False)
    violation_desc = Column(String(200), nullable=False)
    defendant_id = Column(Integer, nullable=True, index=True)
    officer_id = Column(String(20), nullable=True)
    officer_name = Column(String(100), nullable=True)
    violation_date = Column(Date, nullable=False)
    violation_location = Column(String(200), nullable=True)
    vehicle_plate = Column(String(15), nullable=True)
    vehicle_state = Column(String(2), nullable=True)
    import_status = Column(String(20), default="IMPORTED")
    import_batch = Column(String(20), nullable=True)
    import_date = Column(DateTime, nullable=True)
    import_error = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class IncodeDefendant(Base):
    __tablename__ = "ic_defendant"
    defendant_id = Column(Integer, primary_key=True, autoincrement=True)
    last_name = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    dl_number = Column(String(20), nullable=True)
    dl_state = Column(String(2), nullable=True)
    address_line1 = Column(String(100), nullable=True)
    city = Column(String(50), nullable=True)
    state = Column(String(2), nullable=True)
    zip_code = Column(String(10), nullable=True)


class IncodeCaseRecord(Base):
    __tablename__ = "ic_case"
    case_number = Column(String(20), primary_key=True)
    citation_number = Column(String(20), nullable=True, index=True)
    defendant_id = Column(Integer, nullable=True, index=True)
    status = Column(Enum(IncodeCaseStatus), default=IncodeCaseStatus.OPEN, index=True)
    violation_code = Column(String(20), nullable=True)
    violation_desc = Column(String(200), nullable=True)
    court_date = Column(Date, nullable=True)
    courtroom = Column(String(10), nullable=True)
    judge_id = Column(String(20), nullable=True)
    judge_name = Column(String(100), nullable=True)
    disposition_code = Column(String(20), nullable=True)
    disposition_date = Column(Date, nullable=True)
    fine_amount = Column(Float, default=0.0)
    court_costs = Column(Float, default=0.0)
    total_due = Column(Float, default=0.0)
    total_paid = Column(Float, default=0.0)
    balance_due = Column(Float, default=0.0)
    warrant_issued = Column(Boolean, default=False)
    warrant_number = Column(String(20), nullable=True)
    filing_date = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class IncodePayment(Base):
    __tablename__ = "ic_payment"
    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    case_number = Column(String(20), nullable=False, index=True)
    defendant_id = Column(Integer, nullable=True)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(20), nullable=True)
    payment_source = Column(String(20), nullable=True)
    receipt_number = Column(String(20), nullable=True)
    reference_number = Column(String(30), nullable=True)
    payment_date = Column(DateTime, server_default=func.now())
    posted = Column(Boolean, default=True)
    posted_date = Column(DateTime, nullable=True)
    gl_account = Column(String(30), nullable=True)
    batch_id = Column(String(20), nullable=True)
    gateway_txn_id = Column(String(50), nullable=True)
    reconciled = Column(Boolean, default=False)


class IncodeWarrant(Base):
    __tablename__ = "ic_warrant"
    warrant_number = Column(String(20), primary_key=True)
    case_number = Column(String(20), nullable=False, index=True)
    defendant_id = Column(Integer, nullable=True)
    warrant_type = Column(String(20), default="CAPIAS")
    status = Column(String(20), default="ACTIVE", index=True)
    issue_date = Column(Date, nullable=False)
    served_date = Column(Date, nullable=True)
    recalled_date = Column(Date, nullable=True)
    bond_amount = Column(Float, nullable=True)
    tcic_status = Column(String(20), nullable=True)
    ncic_status = Column(String(20), nullable=True)
    last_upload = Column(DateTime, nullable=True)
    upload_error = Column(Text, nullable=True)


class IncodeDocket(Base):
    __tablename__ = "ic_docket"
    docket_id = Column(Integer, primary_key=True, autoincrement=True)
    docket_date = Column(Date, nullable=False, index=True)
    courtroom = Column(String(10), nullable=False)
    judge_id = Column(String(20), nullable=True)
    judge_name = Column(String(100), nullable=True)
    case_count = Column(Integer, default=0)
    generated_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="DRAFT")
    pdf_path = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)


# ============================================================
#  E-BUILDER / TRIMBLE — Capital Improvement Program
# ============================================================

class EBuilderProjectStatus(str, enum.Enum):
    PLANNING = "PLANNING"
    DESIGN = "DESIGN"
    BIDDING = "BIDDING"
    CONSTRUCTION = "CONSTRUCTION"
    CLOSEOUT = "CLOSEOUT"
    COMPLETE = "COMPLETE"
    ON_HOLD = "ON HOLD"


class EBuilderProject(Base):
    __tablename__ = "eb_project"
    project_id = Column(String(20), primary_key=True)
    project_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(EBuilderProjectStatus), default=EBuilderProjectStatus.PLANNING, index=True)
    department = Column(String(50), nullable=True)
    project_manager = Column(String(100), nullable=True)
    contractor = Column(String(100), nullable=True)
    fund_source = Column(String(50), nullable=True)
    budget_total = Column(Float, default=0.0)
    committed_cost = Column(Float, default=0.0)
    actual_cost = Column(Float, default=0.0)
    budget_remaining = Column(Float, default=0.0)
    start_date = Column(Date, nullable=True)
    planned_end_date = Column(Date, nullable=True)
    actual_end_date = Column(Date, nullable=True)
    percent_complete = Column(Float, default=0.0)
    schedule_variance_days = Column(Integer, default=0)
    location_address = Column(String(200), nullable=True)
    ward = Column(String(10), nullable=True)


class EBuilderCostItem(Base):
    __tablename__ = "eb_cost_item"
    cost_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String(20), nullable=False, index=True)
    cost_code = Column(String(20), nullable=False)
    description = Column(String(200), nullable=False)
    category = Column(String(50), nullable=True)
    budgeted = Column(Float, default=0.0)
    committed = Column(Float, default=0.0)
    actual = Column(Float, default=0.0)
    variance = Column(Float, default=0.0)
    vendor = Column(String(100), nullable=True)
    invoice_number = Column(String(30), nullable=True)
    invoice_date = Column(Date, nullable=True)
    gl_account = Column(String(30), nullable=True)
    posted_to_finance = Column(Boolean, default=False)


class EBuilderDocument(Base):
    __tablename__ = "eb_document"
    doc_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String(20), nullable=False, index=True)
    doc_type = Column(String(30), nullable=False)
    title = Column(String(200), nullable=False)
    filename = Column(String(200), nullable=True)
    version = Column(Integer, default=1)
    status = Column(String(20), default="DRAFT")
    uploaded_by = Column(String(100), nullable=True)
    uploaded_at = Column(DateTime, server_default=func.now())
    sync_status = Column(String(20), default="PENDING")
    sync_error = Column(Text, nullable=True)
    sharepoint_url = Column(String(300), nullable=True)


class EBuilderRFI(Base):
    __tablename__ = "eb_rfi"
    rfi_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String(20), nullable=False, index=True)
    rfi_number = Column(String(20), nullable=False)
    subject = Column(String(200), nullable=False)
    question = Column(Text, nullable=True)
    answer = Column(Text, nullable=True)
    status = Column(String(20), default="OPEN", index=True)
    submitted_by = Column(String(100), nullable=True)
    assigned_to = Column(String(100), nullable=True)
    submitted_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    closed_date = Column(Date, nullable=True)
    days_open = Column(Integer, default=0)
    cost_impact = Column(Boolean, default=False)
    schedule_impact = Column(Boolean, default=False)


class EBuilderChangeOrder(Base):
    __tablename__ = "eb_change_order"
    co_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String(20), nullable=False, index=True)
    co_number = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default="PENDING", index=True)
    amount = Column(Float, default=0.0)
    days_added = Column(Integer, default=0)
    requested_by = Column(String(100), nullable=True)
    approved_by = Column(String(100), nullable=True)
    requested_date = Column(Date, nullable=True)
    approved_date = Column(Date, nullable=True)
    reason_code = Column(String(20), nullable=True)
