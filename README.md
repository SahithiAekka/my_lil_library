# Containerized Library App

This repository contains a multi-containerized library application, developed as a series of Flask microservices, a PostgreSQL database, and orchestrated using Docker Compose for local development. This README documents

Phase 1: Local MVP (Coding + Containers) of the project.

---

Project Overview

This project aims to build a scalable and resilient library application following a microservices architecture, progressively deploying it to AWS.

Project Phases Summary

| Phase                   | Tools/Services                                                | Reason for Choice                                            |
| :---------------------- | :------------------------------------------------------------ | :----------------------------------------------------------- |
|1 – Local MVP       | Flask, PostgreSQL, Docker, Docker Compose, Python, Flask-SQLAlchemy, PyJWT, Werkzeug | Foundation for microservices, local containerization, data persistence, rapid development. |
|2 – AWS Basics       | Amazon ECR, ECS Fargate, ALB, Aurora Postgres, Secrets Manager/SSM | Cloud-native deployment, serverless containers, managed database, load balancing, secure credential management. |
|3 – Infrastructure as Code (IaC) | CloudFormation/Terraform/CDK, GitHub                 | Reproducible infrastructure, version control for infrastructure, professional deployment. |
|4 – CI/CD Automation| GitHub Actions, AWS CodePipeline                              | Automated build, test, and deployment pipeline for efficient updates. |
|5 – Monitoring + Scaling | CloudWatch Logs/Alarms, ECS Auto Scaling, AWS X-Ray (Optional) | Observability, performance monitoring, automatic scalability, service tracing. |
|6 – “Wow Factor” Features (Optional)** | Recommendation Service (e.g., ML), Search Service (OpenSearch), Notifications (SNS/SES) | Advanced features demonstrating specialized AWS knowledge and enhancing user experience. |

---
Phase 1: Local MVP (Coding + Containers)

Goal
To build a functional, multi-containerized library application running locally, using Flask microservices and a PostgreSQL database orchestrated with Docker Compose.

Architecture
The application consists of three independent Flask microservices, each responsible for a specific domain, and a PostgreSQL database for persistent storage:

`books-service` (Port 5000): Manages all CRUD (Create, Read, Update, Delete) operations for books in the library. It can also check the availability of a book by querying the `borrow-service`.
`user-service` (Port 5001): Handles user registration, login, and manages user data. It implements interim password hashing for security before external authentication (like Amazon Cognito) is integrated.
`borrow-service` (Port 5002):Manages the borrowing and returning of books. It tracks which user has borrowed which book and its return status.
`db` (PostgreSQL, Port 5432): The relational database used to store all application data (books, users, borrows). Data is persisted using Docker volumes.

All services communicate over a Docker internal network, and their respective Docker images are built from `Dockerfile`s within each service directory.

Local Setup Instructions

Follow these steps to get the application running on your local machine:

Prerequisites
[Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running.
A terminal (e.g., PowerShell on Windows, Bash/Zsh on Linux/macOS).

1.Clone the Repository

```bash
# Replace with your actual repository URL if this is hosted
git clone <your-repository-url>
cd my_lib_app
```

2.Configure Environment Variables
Create a `.env` file in the root of the `my_lib_app` directory. This file will hold sensitive credentials and configuration.

```dotenv
POSTGRES_DB=library_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_postgres_password # REPLACE THIS WITH A STRONG, UNIQUE PASSWORD
SECRET_KEY=your_user_service_secret_key # REPLACE THIS WITH A STRONG, RANDOM SECRET KEY FOR JWT
```

Important:_ Replace the placeholder values with actual strong, unique passwords/keys. Do NOT commit this file to version control.

3.Run the Application with Docker Compose
Navigate to the `my_lib_app` directory in your terminal and execute:

```bash
docker-compose down --volumes # Ensures a clean start, removing old containers/data
docker-compose build --no-cache # Forces a fresh build of all service images
docker-compose up # Starts all services using the freshly built images
```

This command will:
Remove any previous Docker Compose setup (containers, networks, volumes).
Build the Docker images for `books-service`, `user-service`, and `borrow-service` from scratch, installing all Python dependencies.
Create and start the PostgreSQL database container.
Create and start the microservice containers, linking them on a `docker-compose` managed network.
You will see logs from all services streaming in your terminal. Wait for all services to indicate they are running (e.g., `* Running on http://...`).

4.Verification/Testing

Once all services are running (keep `docker-compose up` running in one terminal), open a new terminal window in the `my_lib_app` directory to run these `curl` commands:

User Service (Port 5001)
Register a new user:
    ```powershell
    curl.exe -X POST -H "Content-Type: application/json" -d "{""username"": ""sahithiaekka"", ""password"": ""talktome"", ""first_name"": ""Sahithi"", ""last_name"": ""Aekka""}" http://127.0.0.1:5001/register
    ```
    _Expected Success:_ `{"data":{...},"message":"User registered successfully"}`
Log in with the user:
    ```powershell
    curl.exe -X POST -H "Content-Type: application/json" -d "{""username"": ""sahithiaekka"", ""password"": ""talktome""}" http://127.0.0.1:5001/login
    ```
    _Expected Success:_ `{"message":"Login successful","token":"...","user":{...}}`
Get all users:
    ```powershell
    curl http://127.0.0.1:5001/users
    ```
    _Expected Success:_ `[{"created_at":"...","first_name":"Sahithi","last_name":"Aekka","username":"sahithiaekka"}]` (or `{"message":"No users yet!"}` if empty)

Books Service (Port 5000)
Get all books (initially empty):
    ```powershell
    curl http://127.0.0.1:5000/books
    ```
       _Expected:_ `[]`
Add a new book:
    ```powershell
    curl.exe -X POST -H "Content-Type: application/json" -d "{""title"": ""The Hitchhiker's Guide to the Galaxy"", ""author"": ""Douglas Adams"", ""genre"": ""Science Fiction"", ""available"": true}" http://127.0.0.1:5000/books
    ```
       _Expected Success:_ `{"author":"Douglas Adams", "available":true, "genre":"Science Fiction", "id":1, "title":"The Hitchhiker's Guide to the Galaxy"}`

Borrow Service (Port 5002)
Get all borrows (initially empty):**
    ```powershell
    curl http://127.0.0.1:5002/borrows
    ```
       _Expected:_ `[]`
Borrow a book (using the user and book created above):**
    ```powershell
    curl.exe -X POST -H "Content-Type: application/json" -d "{""username"": ""sahithiaekka"", ""book_id"": 1}" http://127.0.0.1:5002/borrowbook
    ```
       _Expected Success:_ `{"book_id":1,"borrow_date":"...","id":1,"returned":false,"username":"sahithiaekka"}`
Check book availability (from books-service - should now be false if borrowed):**
    ```powershell
    curl http://127.0.0.1:5000/books/1
    ```
       _Expected:_ `{"author":"Douglas Adams", "available":false, "genre":"Science Fiction", "id":1, "title":"The Hitchhiker's Guide to the Galaxy"}`

5.Stop the Application
To stop all running containers and remove the Docker Compose setup:
In the terminal running `docker-compose up`, press `Ctrl+C`.
Then, to remove containers and the network (but keep the `db_data` volume for persistence):
    ```bash
    docker-compose down
    ```
   To remove containers, network, AND the `db_data` volume (which will delete your database data):
    ```bash
    docker-compose down --volumes
    ```

Key Technologies Used in Phase 1
Backend: Python 3.9, Flask
Database: PostgreSQL, Flask-SQLAlchemy, Psycopg2-binary
Authentication: PyJWT, Werkzeug (for password hashing)
Containerization: Docker, Docker Compose
Environment Management: Python-dotenv

---
