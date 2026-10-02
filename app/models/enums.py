from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    LECTURER = "lecturer"
    EXAMINATION_OFFICER = "examination_officer"
    HOD = "hod"
    DEAN = "dean"
    ACADEMIC_PLANNING = "academic_planning"


class Semester(StrEnum):
    FIRST = "First Semester"
    SECOND = "Second Semester"


class ResultStatus(StrEnum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    UNDER_VERIFICATION = "Under Verification"
    RETURNED = "Returned for Correction"
    VERIFIED = "Verified"
    HOD_APPROVED = "HOD Approved"
    DEAN_APPROVED = "Dean Approved"
    FORWARDED = "Forwarded"
    RECEIVED = "Received"
    REJECTED = "Rejected"


class WorkflowAction(StrEnum):
    UPLOADED = "Result uploaded"
    SUBMITTED = "Result submitted"
    START_VERIFICATION = "Verification started"
    VERIFIED = "Result verified"
    RETURNED = "Result returned"
    HOD_APPROVED = "Result approved by HOD"
    DEAN_APPROVED = "Result approved by Dean"
    FORWARDED = "Result forwarded"
    RECEIVED = "Receipt confirmed"
    REJECTED = "Result rejected"
