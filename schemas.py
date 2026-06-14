# ============================================================
# schemas.py
# This file defines what data looks like when it enters
# and leaves our API.
# Pydantic automatically validates all incoming data.
# If data is wrong, FastAPI returns an error automatically.
# ============================================================

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ════════════════════════════════════════════════════════════
# USER SCHEMAS
# ════════════════════════════════════════════════════════════

# UserCreate — data we RECEIVE when someone registers
# This is what the user sends to us
class UserCreate(BaseModel):
    # full_name is required — cannot be empty
    full_name: str
    # EmailStr automatically validates email format
    # e.g. "test@gmail.com" is valid, "test" is not
    email: EmailStr
    # password is required
    password: str
    # role is optional — defaults to "jobseeker"
    # Optional means the user doesn't have to send it
    role: Optional[str] = "jobseeker"


# UserOut — data we SEND back when returning a user
# Notice: password is NOT here — we never send passwords back!
class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    # This tells Pydantic to read data from SQLAlchemy models
    # Without this, Pydantic cannot read SQLAlchemy objects
    class Config:
        from_attributes = True


# UserLogin — data we RECEIVE when someone logs in
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ════════════════════════════════════════════════════════════
# JOB SCHEMAS
# ════════════════════════════════════════════════════════════

# JobCreate — data we RECEIVE when an employer posts a job
class JobCreate(BaseModel):
    title: str
    company: str
    # Location should be specific to Sierra Leone
    # e.g. "Freetown, Sierra Leone" or "Bo, Sierra Leone"
    location: str
    description: str
    # These are optional — employer may not always provide them
    requirements: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: Optional[str] = "Full-time"


# JobUpdate — data we RECEIVE when updating a job (PATCH)
# All fields are optional because employer may only
# want to update ONE field, not everything
class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: Optional[str] = None
    is_active: Optional[bool] = None


# JobOut — data we SEND back when returning a job
class JobOut(BaseModel):
    id: int
    title: str
    company: str
    location: str
    description: str
    requirements: Optional[str]
    salary_range: Optional[str]
    job_type: Optional[str]
    is_active: bool
    employer_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════
# APPLICATION SCHEMAS
# ════════════════════════════════════════════════════════════

# ApplicationCreate — data we RECEIVE when someone applies
class ApplicationCreate(BaseModel):
    # Which job they are applying for
    job_id: int
    # Cover letter is optional
    cover_letter: Optional[str] = None


# ApplicationUpdate — data we RECEIVE when updating status
class ApplicationUpdate(BaseModel):
    # Only the status can be updated
    status: str


# ApplicationOut — data we SEND back when returning application
class ApplicationOut(BaseModel):
    id: int
    job_id: int
    applicant_id: int
    cover_letter: Optional[str]
    status: str
    applied_at: datetime

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════
# AUTH SCHEMAS
# ════════════════════════════════════════════════════════════

# Token — what we send back after successful login
# access_token is the JWT token
# token_type is always "bearer"
class Token(BaseModel):
    access_token: str
    token_type: str


# TokenData — data stored inside the JWT token
# We store the user's email inside the token
class TokenData(BaseModel):
    email: Optional[str] = None


# ════════════════════════════════════════════════════════════
# STATS SCHEMA
# ════════════════════════════════════════════════════════════

# StatsOut — data we send back for the stats endpoint
class StatsOut(BaseModel):
    total_jobs: int
    active_jobs: int
    total_applications: int
    total_users: int