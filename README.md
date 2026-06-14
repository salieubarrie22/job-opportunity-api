# Job Opportunity API 🇸🇱

A RESTful API for youth employment listings in Sierra Leone.

**PROG315 – Object-Oriented Programming 2 | Group Project**

Limkokwing University of Creative Technology, Sierra Leone | Semester 4, 2026

---

## SDG Alignment

**SDG 8 – Decent Work and Economic Growth**

This platform helps bridge the gap between Sierra Leonean youth and employment opportunities by providing a digital job board where employers can post vacancies and job seekers can apply online.

---

## Features

- JWT Authentication with OAuth2
- Role-Based Access Control (jobseeker, employer, admin)
- Full CRUD for job listings
- Job application management
- Async programming with async/await
- Auto Documentation — Swagger UI and ReDoc
- Open Source — MIT License
- SDG 8 aligned — Sierra Leone context

---

## Tech Stack

- Framework: FastAPI
- Database: PostgreSQL
- ORM: SQLAlchemy
- Validation: Pydantic v2
- Authentication: OAuth2 + JWT
- Security: bcrypt password hashing
- Documentation: Swagger UI and ReDoc

---

## Project Structure

- main.py — FastAPI app and all routes
- models.py — SQLAlchemy ORM models
- schemas.py — Pydantic request and response schemas
- database.py — DB engine and session dependency
- auth.py — JWT, password hashing, RBAC
- requirements.txt — Python dependencies
- README.md — Project documentation

---

## Setup and Installation

### 1. Clone the repository
git clone https://github.com/saliebarrie22/job-opportunity-api.git
cd job-opportunity-api

### 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Configure environment variables
Create a .env file with:
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost/jobapi_db
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

### 5. Run the application
uvicorn main:app --reload

### 6. Open API Documentation
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc



## API Endpoints

### Authentication
- POST /auth/register — Register new user
- POST /auth/login — Login and get JWT token

### Users
- GET /users/me — Get my profile
- GET /users — Get all users (Admin only)
- DELETE /users/{id} — Delete user (Admin only)

### Jobs
- POST /jobs — Post a job listing (Employer only)
- GET /jobs — Browse all active jobs
- GET /jobs/{id} — Get single job
- PATCH /jobs/{id} — Update job (Employer only)
- DELETE /jobs/{id} — Delete job (Employer only)

### Applications
- POST /applications — Apply for job (Jobseeker only)
- GET /applications/my — View my applications
- GET /applications/{id} — Get single application
- PATCH /applications/{id}/status — Update status (Employer only)
- DELETE /applications/{id} — Withdraw application

### Stats
- GET /stats — Platform statistics


## Group Members and Contributions

- Mohamed Salieu Barrie — Database setup and models
- Samuel Noah Turay — Authentication system
- Peter Kalie Mansaray — Jobs API routes
- Hannah Alfinah Kargbo — Applications API and documentation

## Sierra Leone Relevance

Sierra Leone faces significant youth unemployment challenges. This API provides a digital platform specifically designed for local employers to post job vacancies and Sierra Leonean youth to find employment opportunities. The platform is free and open source so NGOs and organizations can deploy it at no cost.



## License

This project is licensed under the MIT License — free to use, modify, and distribute.
