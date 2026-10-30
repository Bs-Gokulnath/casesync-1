from app.models.enums import UserRole
from app.security.permissions import Permission, role_has_permission


def test_system_admin_has_every_permission() -> None:
    for permission in Permission:
        assert role_has_permission(UserRole.SYSTEM_ADMIN, permission)


def test_auditor_is_fully_read_only() -> None:
    write_permissions = [
        Permission.COMPLAINT_CREATE,
        Permission.COMPLAINT_EDIT,
        Permission.COMPLAINT_TRANSITION,
        Permission.COMPLAINT_DISPOSE,
        Permission.COMPLAINT_REOPEN,
        Permission.OVERLAP_DECIDE,
        Permission.ADMIN_MANAGE,
    ]
    for permission in write_permissions:
        assert not role_has_permission(UserRole.AUDITOR, permission)
    assert role_has_permission(UserRole.AUDITOR, Permission.COMPLAINT_READ)
    assert role_has_permission(UserRole.AUDITOR, Permission.AUDIT_READ)


def test_only_system_admin_can_reopen_a_disposed_case() -> None:
    for role in UserRole:
        expected = role is UserRole.SYSTEM_ADMIN
        assert role_has_permission(role, Permission.COMPLAINT_REOPEN) is expected


def test_regional_officer_cannot_dispose_but_can_escalate() -> None:
    assert not role_has_permission(UserRole.REGIONAL_OFFICER, Permission.COMPLAINT_DISPOSE)
    assert role_has_permission(UserRole.REGIONAL_OFFICER, Permission.COMPLAINT_ESCALATE)


def test_senior_management_can_decide_overlaps_but_not_edit_cases() -> None:
    assert role_has_permission(UserRole.SENIOR_MANAGEMENT, Permission.OVERLAP_DECIDE)
    assert not role_has_permission(UserRole.SENIOR_MANAGEMENT, Permission.COMPLAINT_EDIT)
