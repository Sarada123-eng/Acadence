from app.models.attendance_logs import AttendanceLog
from app.models.classroom import Classroom
from app.models.student import Student
from app.models.student_email_otp import StudentEmailOtpChallenge
from app.models.subject import Subject
from app.models.teacher import Teacher

__all__ = [
    "AttendanceLog",
    "Classroom",
    "Student",
    "StudentEmailOtpChallenge",
    "Subject",
    "Teacher",
]