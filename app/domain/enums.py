from enum import Enum


class DocumentStatus(str, Enum):
    """Статусы документа."""

    DRAFT = "DRAFT"
    APPROVAL = "APPROVAL"
    REVISION_REQUIRED = "REVISION_REQUIRED"
    CANCELED = "CANCELED"
    APPROVED = "APPROVED"


class ApprovalStatus(str, Enum):
    """Статусы согласования."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ApprovalStepStatus(str, Enum):
    """Статусы шага согласования."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
