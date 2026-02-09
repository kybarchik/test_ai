from app.domain.enums import ApprovalStatus, ApprovalStepStatus, DocumentStatus


def can_transition_document_status(current: DocumentStatus, target: DocumentStatus) -> bool:
    """Проверить допустимость перехода статуса документа."""
    transitions = {
        DocumentStatus.DRAFT: {DocumentStatus.APPROVAL},
        DocumentStatus.APPROVAL: {
            DocumentStatus.APPROVED,
            DocumentStatus.REVISION_REQUIRED,
            DocumentStatus.CANCELED,
        },
        DocumentStatus.REVISION_REQUIRED: {DocumentStatus.APPROVAL},
        DocumentStatus.APPROVED: set(),
        DocumentStatus.CANCELED: {DocumentStatus.DRAFT},
    }
    return target in transitions.get(current, set())


def can_transition_approval_status(current: ApprovalStatus, target: ApprovalStatus) -> bool:
    """Проверить допустимость перехода статуса согласования."""
    transitions = {
        ApprovalStatus.PENDING: {ApprovalStatus.APPROVED, ApprovalStatus.REJECTED},
        ApprovalStatus.APPROVED: set(),
        ApprovalStatus.REJECTED: set(),
    }
    return target in transitions.get(current, set())


def can_transition_step_status(current: ApprovalStepStatus, target: ApprovalStepStatus) -> bool:
    """Проверить допустимость перехода статуса шага согласования."""
    transitions = {
        ApprovalStepStatus.PENDING: {ApprovalStepStatus.APPROVED, ApprovalStepStatus.REJECTED},
        ApprovalStepStatus.APPROVED: set(),
        ApprovalStepStatus.REJECTED: set(),
    }
    return target in transitions.get(current, set())
