import enum

from app.models.enums import UserRole


class Permission(str, enum.Enum):
    INSTITUTION_READ = "institution:read"
    INSTITUTION_WRITE = "institution:write"
    INSTITUTION_STATUS = "institution:status"

    COMPLAINT_READ = "complaint:read"
    COMPLAINT_CREATE = "complaint:create"
    COMPLAINT_EDIT = "complaint:edit"
    COMPLAINT_TRANSITION = "complaint:transition"
    COMPLAINT_TRANSFER = "complaint:transfer"
    COMPLAINT_ESCALATE = "complaint:escalate"
    COMPLAINT_DISPOSE = "complaint:dispose"
    COMPLAINT_REOPEN = "complaint:reopen"
    COMPLAINT_ASSIGN = "complaint:assign"
    COMPLAINT_RELATE = "complaint:relate"
    DOCUMENT_UPLOAD = "document:upload"
    DOCUMENT_READ = "document:read"

    OVERLAP_READ = "overlap:read"
    OVERLAP_DECIDE = "overlap:decide"

    WORKQUEUE_READ = "workqueue:read"
    NOTIFICATION_READ = "notification:read"

    ANALYTICS_READ = "analytics:read"
    ANALYTICS_EXPORT = "analytics:export"

    ADMIN_MANAGE = "admin:manage"
    AUDIT_READ = "audit:read"


_CASE_HANDLER_PERMISSIONS = {
    Permission.INSTITUTION_READ,
    Permission.INSTITUTION_WRITE,
    Permission.INSTITUTION_STATUS,
    Permission.COMPLAINT_READ,
    Permission.COMPLAINT_CREATE,
    Permission.COMPLAINT_EDIT,
    Permission.COMPLAINT_TRANSITION,
    Permission.COMPLAINT_TRANSFER,
    Permission.COMPLAINT_ESCALATE,
    Permission.COMPLAINT_DISPOSE,
    Permission.COMPLAINT_ASSIGN,
    Permission.COMPLAINT_RELATE,
    Permission.DOCUMENT_UPLOAD,
    Permission.DOCUMENT_READ,
    Permission.OVERLAP_READ,
    Permission.OVERLAP_DECIDE,
    Permission.WORKQUEUE_READ,
    Permission.NOTIFICATION_READ,
    Permission.ANALYTICS_READ,
}

_READ_ONLY_PERMISSIONS = {
    Permission.INSTITUTION_READ,
    Permission.COMPLAINT_READ,
    Permission.DOCUMENT_READ,
    Permission.OVERLAP_READ,
    Permission.NOTIFICATION_READ,
    Permission.ANALYTICS_READ,
    Permission.AUDIT_READ,
}

ROLE_PERMISSIONS: dict[UserRole, frozenset[Permission]] = {
    UserRole.SYSTEM_ADMIN: frozenset(Permission),
    UserRole.SENIOR_MANAGEMENT: frozenset(
        _READ_ONLY_PERMISSIONS | {Permission.OVERLAP_DECIDE, Permission.ANALYTICS_EXPORT}
    ),
    UserRole.BUREAU_OFFICER: frozenset(_CASE_HANDLER_PERMISSIONS),
    UserRole.REGIONAL_OFFICER: frozenset(
        _CASE_HANDLER_PERMISSIONS - {Permission.COMPLAINT_DISPOSE}
    ),
    UserRole.AUDITOR: frozenset(_READ_ONLY_PERMISSIONS),
}


def role_has_permission(role: UserRole, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, frozenset())
