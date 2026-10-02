from datetime import datetime, timezone
from fastapi import HTTPException
from sqlmodel import Session
from app.models import ResultSubmission, User, WorkflowEvent
from app.models.enums import ResultStatus, UserRole, WorkflowAction
from app.services.audit import log_audit
from app.services.notifications import notify, notify_role


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def transition(session: Session, submission: ResultSubmission, actor: User, new_status: ResultStatus, action: WorkflowAction, comment: str | None = None) -> None:
    old = submission.status
    allowed = {
        (ResultStatus.DRAFT, ResultStatus.SUBMITTED): UserRole.LECTURER,
        (ResultStatus.RETURNED, ResultStatus.SUBMITTED): UserRole.LECTURER,
        (ResultStatus.SUBMITTED, ResultStatus.UNDER_VERIFICATION): UserRole.EXAMINATION_OFFICER,
        (ResultStatus.UNDER_VERIFICATION, ResultStatus.VERIFIED): UserRole.EXAMINATION_OFFICER,
        (ResultStatus.UNDER_VERIFICATION, ResultStatus.RETURNED): UserRole.EXAMINATION_OFFICER,
        (ResultStatus.VERIFIED, ResultStatus.REJECTED): UserRole.HOD,
        (ResultStatus.HOD_APPROVED, ResultStatus.REJECTED): UserRole.DEAN,
        (ResultStatus.VERIFIED, ResultStatus.HOD_APPROVED): UserRole.HOD,
        (ResultStatus.VERIFIED, ResultStatus.RETURNED): UserRole.HOD,
        (ResultStatus.HOD_APPROVED, ResultStatus.DEAN_APPROVED): UserRole.DEAN,
        (ResultStatus.HOD_APPROVED, ResultStatus.RETURNED): UserRole.DEAN,
        (ResultStatus.DEAN_APPROVED, ResultStatus.FORWARDED): UserRole.DEAN,
        (ResultStatus.FORWARDED, ResultStatus.RECEIVED): UserRole.ACADEMIC_PLANNING,
    }
    expected_role = allowed.get((old, new_status))
    if expected_role != actor.role:
        raise HTTPException(status_code=409, detail="This result is no longer available for this action.")
    if new_status in {ResultStatus.RETURNED, ResultStatus.REJECTED} and not comment:
        raise HTTPException(status_code=422, detail="A reason is required when returning a result.")

    submission.status = new_status
    submission.updated_at = utcnow()
    if new_status == ResultStatus.SUBMITTED:
        submission.submitted_at = utcnow()
    session.add(submission)
    session.add(WorkflowEvent(
        submission_id=submission.id,
        actor_id=actor.id,
        action=action.value,
        previous_status=old,
        new_status=new_status,
        comment=comment,
    ))
    log_audit(session, user=actor, action=action.value, submission_id=submission.id,
              previous_status=old.value, new_status=new_status.value, comment=comment)

    if new_status == ResultStatus.SUBMITTED:
        notify_role(session, UserRole.EXAMINATION_OFFICER, "Result requires verification", f"{submission.reference} is ready for verification.", submission.id, department_id=submission.department_id)
    elif new_status == ResultStatus.UNDER_VERIFICATION:
        notify(session, submission.lecturer_id, "Result is under verification", f"{submission.reference} has entered verification.", submission.id)
    elif new_status in {ResultStatus.RETURNED, ResultStatus.REJECTED}:
        title = "Result returned for correction" if new_status == ResultStatus.RETURNED else "Result rejected"
        notify(session, submission.lecturer_id, title, comment or f"{submission.reference} was updated.", submission.id)
    elif new_status == ResultStatus.VERIFIED:
        notify_role(session, UserRole.HOD, "Result awaiting HOD approval", f"{submission.reference} has been verified.", submission.id, department_id=submission.department_id)
    elif new_status == ResultStatus.HOD_APPROVED:
        notify_role(session, UserRole.DEAN, "Result awaiting Dean approval", f"{submission.reference} was approved by the HOD.", submission.id, faculty_id=submission.faculty_id)
    elif new_status == ResultStatus.DEAN_APPROVED:
        notify_role(session, UserRole.ACADEMIC_PLANNING, "Result forwarded for receipt", f"{submission.reference} is awaiting Academic Planning Unit receipt.", submission.id)
    elif new_status == ResultStatus.FORWARDED:
        notify(session, submission.lecturer_id, "Result forwarded", f"{submission.reference} has completed institutional approvals and was forwarded.", submission.id)
    elif new_status == ResultStatus.RECEIVED:
        notify(session, submission.lecturer_id, "Result received", f"{submission.reference} was received by Academic Planning Unit.", submission.id)
