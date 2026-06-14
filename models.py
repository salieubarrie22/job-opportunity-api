# ============================================================
# models.py
# This file defines our database tables as Python classes.
# Each class = one table in PostgreSQL.
# SQLAlchemy will automatically create these tables.
# ============================================================

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

# We import Base from database.py
# All our models must inherit from Base
# This tells SQLAlchemy these classes are database tables
from database import Base


# ════════════════════════════════════════════════════════════
# USER MODEL
# This represents the "users" table in PostgreSQL
# Stores all registered users (jobseekers, employers, admins)
# ════════════════════════════════════════════════════════════
class User(Base):
    # This is the actual table name in PostgreSQL
    __tablename__ = "users"

    # Each Column = one column in the table
    # Integer, String, Boolean, DateTime = data types

    # Primary key — unique ID for each user (auto-increments)
    id = Column(Integer, primary_key=True, index=True)

    # Full name of the user — max 100 characters
    full_name = Column(String(100), nullable=False)

    # Email — must be unique, used for login
    email = Column(String(150), unique=True, index=True, nullable=False)

    # Password — stored as a hash, never plain text
    password = Column(String(255), nullable=False)

    # Role — determines what the user can do
    # "jobseeker" = can apply for jobs
    # "employer"  = can post jobs
    # "admin"     = can do everything
    role = Column(String(20), default="jobseeker")

    # is_active — if False, user is banned/disabled
    is_active = Column(Boolean, default=True)

    # created_at — automatically set to current time
    created_at = Column(DateTime, default=datetime.utcnow)

    # RELATIONSHIPS
    # This tells SQLAlchemy that one User can have many Jobs
    # cascade="all, delete-orphan" means if we delete a user,
    # all their jobs are also deleted automatically
    jobs = relationship("Job", back_populates="employer", cascade="all, delete-orphan")

    # One User can have many Applications
    applications = relationship("Application", back_populates="applicant", cascade="all, delete-orphan")

    # This is what prints when we do print(user)
    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>"


# ════════════════════════════════════════════════════════════
# JOB MODEL
# This represents the "jobs" table in PostgreSQL
# Stores all job listings posted by employers
# ════════════════════════════════════════════════════════════
class Job(Base):
    __tablename__ = "jobs"

    # Unique ID for each job
    id = Column(Integer, primary_key=True, index=True)

    # Job title — e.g. "Software Developer"
    title = Column(String(200), nullable=False)

    # Company name — e.g. "Orange Sierra Leone"
    company = Column(String(150), nullable=False)

    # Location — e.g. "Freetown, Sierra Leone"
    location = Column(String(150), nullable=False)

    # Full job description
    description = Column(Text, nullable=False)

    # Job requirements — optional
    requirements = Column(Text, nullable=True)

    # Salary range — e.g. "NLe 2000 - NLe 4000"
    salary_range = Column(String(80), nullable=True)

    # Job type — Full-time, Part-time, Contract, Remote
    job_type = Column(String(50), default="Full-time")

    # is_active — if False, job is closed/expired
    is_active = Column(Boolean, default=True)

    # employer_id — links this job to the user who posted it
    # ForeignKey means this must match an id in the users table
    employer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # When the job was posted
    created_at = Column(DateTime, default=datetime.utcnow)

    # RELATIONSHIPS
    # Links back to the User who posted this job
    employer = relationship("User", back_populates="jobs")

    # One Job can have many Applications
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Job id={self.id} title={self.title} company={self.company}>"


# ════════════════════════════════════════════════════════════
# APPLICATION MODEL
# This represents the "applications" table in PostgreSQL
# Stores all job applications submitted by jobseekers
# ════════════════════════════════════════════════════════════
class Application(Base):
    __tablename__ = "applications"

    # Unique ID for each application
    id = Column(Integer, primary_key=True, index=True)

    # Which job this application is for
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)

    # Which user submitted this application
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Optional cover letter
    cover_letter = Column(Text, nullable=True)

    # Application status — tracks where in the hiring process
    # "pending"  = just submitted, not reviewed yet
    # "reviewed" = employer has seen it
    # "accepted" = congratulations!
    # "rejected" = not selected
    status = Column(String(30), default="pending")

    # When the application was submitted
    applied_at = Column(DateTime, default=datetime.utcnow)

    # RELATIONSHIPS
    # Links back to the Job this application is for
    job = relationship("Job", back_populates="applications")

    # Links back to the User who applied
    applicant = relationship("User", back_populates="applications")

    def __repr__(self):
        return f"<Application id={self.id} job_id={self.job_id} status={self.status}>"