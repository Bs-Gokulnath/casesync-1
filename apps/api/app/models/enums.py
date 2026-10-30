import enum


class UserRole(str, enum.Enum):
    SYSTEM_ADMIN = "system_admin"
    SENIOR_MANAGEMENT = "senior_management"
    BUREAU_OFFICER = "bureau_officer"
    REGIONAL_OFFICER = "regional_officer"
    AUDITOR = "auditor"


class ComplaintSource(str, enum.Enum):
    PORTAL = "portal"
    EMAIL = "email"
    LETTER = "letter"
    PHONE = "phone"
    WALK_IN = "walk_in"
    OTHER = "other"


class ComplaintPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplaintStatus(str, enum.Enum):
    RECEIVED = "received"
    UNDER_REVIEW = "under_review"
    UNDER_PROCESS = "under_process"
    PENDING_INFORMATION = "pending_information"
    TRANSFERRED = "transferred"
    ESCALATED = "escalated"
    DISPOSED = "disposed"


class CaseActionType(str, enum.Enum):
    TRANSFER = "transfer"
    ESCALATE = "escalate"
    DISPOSE = "dispose"
    REOPEN = "reopen"
    NOTE = "note"
    ASSIGN = "assign"


class CaseRelationshipType(str, enum.Enum):
    RELATED = "related"
    DUPLICATE = "duplicate"


class OverlapAlertStatus(str, enum.Enum):
    OPEN = "open"
    CONFIRMED = "confirmed"
    DISMISSED = "dismissed"
    RESOLVED = "resolved"


class NotificationType(str, enum.Enum):
    OVERLAP_ALERT = "overlap_alert"
    ASSIGNMENT = "assignment"
    DEADLINE_WARNING = "deadline_warning"
    OVERDUE = "overdue"
    TRANSFER = "transfer"
    ESCALATION = "escalation"
