EduMaster-Dj

Production-oriented Django + DRF e-learning platform: PostgreSQL, Redis, Celery, MinIO (S3-compatible storage), fully containerized with Docker Compose.

About the Project

EduMaster is a full-featured backend for an online course platform. It supports a role-based user system (STUDENT, TEACHER, PARENT, SUPERADMIN, ADMIN) and covers the full learning cycle: course and lesson management, assignments with deadlines, multiple-choice quizzes with scoring, course payments, and automatically generated, QR-verifiable certificates.

Key architectural decisions:

Repository + Service layer separating data access from business logic
Split object storage: a public MinIO bucket (course covers, certificates, QR codes) and a private bucket (lesson videos/PDFs, student submissions) served through short-lived presigned URLs, guarded by payment/ownership checks
Async processing via Celery: certificate generation, assignment deadline reminders, and email notifications run outside the request/response cycle, dispatched safely via transaction.on_commit
Cache versioning (Redis INCR-based) instead of pattern-based cache deletion, avoiding costly SCAN operations on invalidation
Tech Stack
Python 3.12+ / Django 5.2 / Django REST Framework — core backend and REST API
PostgreSQL 16+ — primary relational database
Redis 7+ — Celery broker/result backend and Django cache layer
Celery + Celery Beat — asynchronous tasks and scheduled jobs (deadline reminders, certificate emails)
MinIO — S3-compatible object storage, split into public and private buckets with a scoped service account (least-privilege access, no root credentials used by the app)
drf-yasg — OpenAPI schema generation, Swagger UI and ReDoc
Docker & Docker Compose — fully containerized local and production stack
structlog — structured JSON logging to stdout
Pillow, qrcode — certificate image and QR code generation
GitHub Actions — CI pipeline (lint, tests, dependency security check, Docker image build)
Installation
Requirements
Python 3.12+
PostgreSQL 16+
Redis 7+
Docker & Docker Compose (recommended)
Git

Management Commands 
python manage.py export_users   
IF YOU RUN THIS COMMAND, YOU WILL GET A LIST OF ALL USERS WITH QUANTITY IN A .csv FILE.   path --> userapp/management/commands/export_users.py

python manage.py export_courses
IF YOU RUN THIS COMMAND, YOU WILL GET A LIST OF ALL COURSES WITH QUANTITY IN A .csv FILE. path --> edumasterapp/management/commands/export_courses.py


From this link you can learn how to render ER Diagram  
https://www.youtube.com/watch?v=qzrE7cfc_3Q            
LEARN AND SHARE WITH OTHER DEVELOPERS !                


https://unfoldadmin.com/ Used Admin Panel django-unfold with Modern UI Interface

http://localhost:8000/swagger/ Registered Django administrators can access Swagger.

http://localhost:8000/edumaster/admin-panel/ url of admin panel


### Authentication

| Method          | Endpoint                              | Description                      |
| --------------- | ------------------------------------- | -------------------------------- |
| `POST`          | `/api/v1/auth/users/register/`        | Register a new user              |
| `POST`          | `/api/v1/auth/users/login/`           | Obtain JWT access/refresh tokens |
| `POST`          | `/api/v1/auth/users/logout/`          | Invalidate token                 |
| `POST`          | `/api/v1/auth/users/refresh`          | Refresh access token             |
| `PUT/PATCH`     | `/api/v1/auth/users/change-password/` | Change password                  |
| `GET/PUT/PATCH` | `/api/v1/auth/users/profile/me`       | Current user profile             |

### Courses

| Method      | Endpoint               | Description      |
| ----------- | ---------------------- | ---------------- |
| `GET`       | `/api/v1/course/`      | List all courses |
| `POST`      | `/api/v1/course/`      | Create a course  |
| `GET`       | `/api/v1/course/{id}/` | Course details   |
| `PUT/PATCH` | `/api/v1/course/{id}/` | Update a course  |
| `DELETE`    | `/api/v1/course/{id}/` | Delete a course  |

### Lessons

| Method      | Endpoint               | Description     |
| ----------- | ---------------------- | --------------- |
| `POST`      | `/api/v1/lesson/`      | Create a lesson |
| `GET`       | `/api/v1/lesson/{id}/` | Lesson details  |
| `PUT/PATCH` | `/api/v1/lesson/{id}/` | Update a lesson |
| `DELETE`    | `/api/v1/lesson/{id}/` | Delete a lesson |

### Assignments

| Method      | Endpoint                           | Description                                  |
| ----------- | ---------------------------------- | -------------------------------------------- |
| `GET/POST`  | `/api/v1/assignment/`              | List / create assignments                    |
| `GET`       | `/api/v1/assignment/{id}/`         | Assignment details                           |
| `PUT/PATCH` | `/api/v1/assignment/{id}/`         | Update an assignment                         |
| `DELETE`    | `/api/v1/assignment/{id}/`         | Delete an assignment                         |
| `GET/POST`  | `/api/v1/assignment/student/`      | List / submit student assignment submissions |
| `PUT/PATCH` | `/api/v1/assignment/student/{id}/` | Update own submission (STUDENT)              |
| `PUT/PATCH` | `/api/v1/assignment/teacher/{id}/` | Grade a submission (TEACHER)                 |

### Quizzes

| Method      | Endpoint                 | Description           |
| ----------- | ------------------------ | --------------------- |
| `GET/POST`  | `/api/v1/quiz/`          | List / create quizzes |
| `GET`       | `/api/v1/quiz/{id}/`     | Quiz details          |
| `PUT/PATCH` | `/api/v1/quiz/{id}/`     | Update a quiz         |
| `DELETE`    | `/api/v1/quiz/{id}/`     | Delete a quiz         |
| `POST`      | `/api/v1/question/`      | Create a question     |
| `GET`       | `/api/v1/question/{id}/` | Question details      |
| `PUT/PATCH` | `/api/v1/question/{id}/` | Update a question     |
| `DELETE`    | `/api/v1/question/{id}/` | Delete a question     |

### Taking a Quiz

| Method | Endpoint                                 | Description                       |
| ------ | ---------------------------------------- | --------------------------------- |
| `GET`  | `/api/v1/quiz-test/{quiz_id}/`           | Get test details                  |
| `GET`  | `/api/v1/quiz-test/{quiz_id}/questions/` | Get the list of test questions    |
| `POST` | `/api/v1/quiz-test/{quiz_id}/start/`     | Start the test (starts the timer) |
| `POST` | `/api/v1/quiz-test/{quiz_id}/submit/`    | Submit answers and get results    |
| `GET`  | `/api/v1/quiz-test/{quiz_id}/history/`   | History of test attempts          |

### Payments

| Method     | Endpoint                | Description             |
| ---------- | ----------------------- | ----------------------- |
| `GET/POST` | `/api/v1/payment/`      | List / create a payment |
| `GET`      | `/api/v1/payment/{id}/` | Payment details         |

### Certificates

| Method | Endpoint                                    | Description                               |
| ------ | ------------------------------------------- | ----------------------------------------- |
| `GET`  | `/api/v1/certificate/`                      | List certificates                         |
| `GET`  | `/api/v1/certificate/{certificate_number}/` | Certificate details / public verification |

### Parent

| Method | Endpoint                          | Description                                                            |
| ------ | --------------------------------- | ---------------------------------------------------------------------- |
| `GET`  | `/api/v1/parent/children-report/` | Aggregated report on parent's children (courses, grades, certificates) |


