from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
import asyncio

from database import engine, get_db, Base
from models import User, Job, Application
from schemas import (
    UserCreate, UserOut,
    JobCreate, JobUpdate, JobOut,
    ApplicationCreate, ApplicationUpdate, ApplicationOut,
    Token, StatsOut
)
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_active_user,
    require_role,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Job Opportunity API",
    description="A RESTful API for youth employment listings in Sierra Leone. SDG 8 - Decent Work and Economic Growth",
    version="1.0.0"
)

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to the Job Opportunity API!",
        "country": "Sierra Leone",
        "sdg": "SDG 8 - Decent Work and Economic Growth",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "1.0.0"
    }

@app.post("/auth/register",
          response_model=UserOut,
          status_code=status.HTTP_201_CREATED,
          tags=["Authentication"])
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(
            User.email == user_data.email
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered."
            )
        valid_roles = ["jobseeker", "employer", "admin"]
        if user_data.role not in valid_roles:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role. Choose from: {valid_roles}"
            )
        new_user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            password=hash_password(user_data.password),
            role=user_data.role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/auth/login",
          response_model=Token,
          tags=["Authentication"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == form_data.username
    ).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Your account has been deactivated."
        )
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/users/me",
         response_model=UserOut,
         tags=["Users"])
def get_my_profile(
    current_user: User = Depends(get_current_active_user)
):
    return current_user

@app.get("/users",
         response_model=List[UserOut],
         tags=["Users"])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    return db.query(User).all()

@app.delete("/users/{user_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            tags=["Users"])
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    db.delete(user)
    db.commit()

@app.post("/jobs",
          response_model=JobOut,
          status_code=status.HTTP_201_CREATED,
          tags=["Jobs"])
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("employer"))
):
    new_job = Job(
        title=job_data.title,
        company=job_data.company,
        location=job_data.location,
        description=job_data.description,
        requirements=job_data.requirements,
        salary_range=job_data.salary_range,
        job_type=job_data.job_type,
        employer_id=current_user.id
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@app.get("/jobs",
         response_model=List[JobOut],
         tags=["Jobs"])
def get_all_jobs(
    location: str = None,
    job_type: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Job).filter(Job.is_active == True)
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if job_type:
        query = query.filter(Job.job_type.ilike(f"%{job_type}%"))
    return query.all()

@app.get("/jobs/{job_id}",
         response_model=JobOut,
         tags=["Jobs"])
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job

@app.patch("/jobs/{job_id}",
           response_model=JobOut,
           tags=["Jobs"])
def update_job(
    job_id: int,
    updates: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.employer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorised.")
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    return job

@app.delete("/jobs/{job_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            tags=["Jobs"])
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.employer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorised.")
    db.delete(job)
    db.commit()

@app.post("/applications",
          response_model=ApplicationOut,
          status_code=status.HTTP_201_CREATED,
          tags=["Applications"])
def apply_for_job(
    app_data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("jobseeker"))
):
    job = db.query(Job).filter(
        Job.id == app_data.job_id,
        Job.is_active == True
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    already_applied = db.query(Application).filter(
        Application.job_id == app_data.job_id,
        Application.applicant_id == current_user.id
    ).first()
    if already_applied:
        raise HTTPException(status_code=400, detail="Already applied.")
    new_application = Application(
        job_id=app_data.job_id,
        applicant_id=current_user.id,
        cover_letter=app_data.cover_letter
    )
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    return new_application

@app.get("/applications/my",
         response_model=List[ApplicationOut],
         tags=["Applications"])
def get_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(Application).filter(
        Application.applicant_id == current_user.id
    ).all()

@app.get("/applications/{application_id}",
         response_model=ApplicationOut,
         tags=["Applications"])
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    application = db.query(Application).filter(
        Application.id == application_id
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Not found.")
    if application.applicant_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorised.")
    return application

@app.patch("/applications/{application_id}/status",
           response_model=ApplicationOut,
           tags=["Applications"])
def update_application_status(
    application_id: int,
    update_data: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("employer"))
):
    valid_statuses = ["pending", "reviewed", "accepted", "rejected"]
    if update_data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status.")
    application = db.query(Application).filter(
        Application.id == application_id
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Not found.")
    application.status = update_data.status
    db.commit()
    db.refresh(application)
    return application

@app.delete("/applications/{application_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            tags=["Applications"])
def withdraw_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    application = db.query(Application).filter(
        Application.id == application_id
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Not found.")
    if application.applicant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorised.")
    db.delete(application)
    db.commit()

async def fetch_stats_async(db: Session) -> dict:
    await asyncio.sleep(0)
    return {
        "total_jobs": db.query(Job).count(),
        "active_jobs": db.query(Job).filter(Job.is_active == True).count(),
        "total_applications": db.query(Application).count(),
        "total_users": db.query(User).count()
    }

@app.get("/stats",
         response_model=StatsOut,
         tags=["Stats"])
async def get_stats(db: Session = Depends(get_db)):
    return await fetch_stats_async(db)