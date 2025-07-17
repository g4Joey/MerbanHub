# MerbanHub

## OCR & Document Indexing System for UMB Capital

---

## Table of Contents

1. [Overview](#overview)
2. [Folder Structure](#folder-structure)
3. [Prerequisites](#prerequisites)
4. [Service Setup](#service-setup)
   - [OCR Service (Node.js)](#ocr-service-nodejs)
   - [Java API (Spring Boot)](#java-api-spring-boot)
   - [Django API (Python)](#django-api-python)
   - [Frontend (React/Next.js)](#frontend-reactnextjs)
   - [Database (MySQL)](#database-mysql)
5. [Running Locally](#running-locally)
6. [Development Workflow](#development-workflow)
7. [Contributing](#contributing)
8. [License](#license)

---

## Overview

MerbanHub is a prototype OCR and document‑indexing system built for UMB Capital.
It watches a shared scan folder, runs OCR, parses metadata, renames files, indexes records in MySQL, and exposes APIs and a React dashboard for search and monitoring.

---

## Folder Structure

```
backend-java-springboot/
backend-python-django/
frontend-react/merbanhub/
database/
ocr_service/
```

| Directory                | Owner               | Purpose                                      |
|--------------------------|---------------------|----------------------------------------------|
| `backend-java-springboot`| Kenny               | REST API for logs, documents, healthcheck    |
| `backend-python-django`  | Kojo                | (Optional) admin UI, file‐upload API         |
| `frontend-react`         | Eddie & Lucius      | React/Next.js UI & data fetching             |
| `database`               | Ruth & Angela       | MySQL schema, migrations, seed data          |
| `ocr_service`            | Lucius & Kojo       | Folder watcher, OCR, metadata parsing, index |

---

## Prerequisites

- **Docker & Docker Compose**
- **Node.js ≥16**
- **Java ≥17**
- **Python ≥3.9**
- **MySQL 8** (or use the Docker service below)

### Installing Docker & Docker Compose

1. Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/) for your OS (Windows, Mac, or Linux).
2. Follow the installation instructions and make sure Docker is running.
3. (Optional) Test your installation by running:
   ```sh
   docker --version
   docker-compose --version
   ```

---

## Service Setup

### OCR Service (Node.js)

```bash
cd ocr_service
cp .env.example .env
npm install
npm start           # or: docker-compose up ocr
```

### Java API (Spring Boot)

```bash
cd backend-java-springboot
cp src/main/resources/application.yml.example src/main/resources/application.yml
./mvnw spring-boot:run   # or: docker-compose up java-api
```

### Django API (Python)

```bash
cd backend-python-django
cp .env.example .env
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001   # or: docker-compose up django-api
```

### Frontend (React/Next.js)

```bash
cd frontend-react/merbanhub
cp .env.local.example .env.local
npm install
npm run dev        # or: docker-compose up frontend
```

### Database (MySQL)

- Uses the Docker service defined below

---

## Running Locally

Bring up all services in one go:

```bash
docker-compose up --build
```

**Services:**

- db (MySQL on 3306)
- ocr_service (folder watcher & OCR)
- java-api (Spring Boot on 8080)
- django-api (Django on 8001)
- frontend (React on 3000)

**Verify health:**

- [http://localhost:8080/api/health](http://localhost:8080/api/health)
- [http://localhost:8001/health](http://localhost:8001/health)

---

#### Manual MySQL Setup (if not using Docker)

1. Install MySQL 8.
2. Create the database and user:

   ```sql
   CREATE DATABASE merbanhub_db;
   CREATE USER 'merbanhub_user'@'localhost' IDENTIFIED BY 'yourpassword';
   GRANT ALL PRIVILEGES ON merbanhub_db.* TO 'merbanhub_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. Set your `.env` or connection variables as needed.

---

## Development Workflow

### Sync

```sh
git checkout dev
git pull origin dev
```

### Branch

```sh
git checkout -b feat/your-feature
```

### Code & Commit

```sh
git add .
git commit -m "feat: brief description"
```

### Push & PR

```sh
git push -u origin feat/your-feature
```

→ Open a Pull Request into dev, request reviews, pass CI.

---

## Contributing

- **Branch naming:** `feat/`, `fix/`, `chore/` prefixes
- **Lint:**

  ```sh
  npm run lint
  ```

- **Tests:**

  ```sh
  npm test
  ```

- **Commit messages:** clear, imperative, prefixed by type (`feat:`, `fix:`)
- **Protect dev:** all merges require Pull Requests, approvals, and passing CI.

---

## License

ISC
