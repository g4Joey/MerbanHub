# MerbanHub

[![Build Status](https://github.com/g4Joey/MerbanHub/actions/workflows/ci.yml/badge.svg)](https://github.com/g4Joey/MerbanHub/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/g4Joey/MerbanHub)](./LICENSE)

## OCR & Document Indexing System for UMB Capital

---

## Table of Contents

1. [Overview](#overview)
2. [Folder Structure](#folder-structure)
3. [Prerequisites](#prerequisites)
4. [Service Setup](#service-setup)
   - [OCR Service (Python)](#ocr-service-python)
   - [Java API (Spring Boot)](#java-api-spring-boot)
   - [Django API (Python)](#django-api-python)
   - [Frontend (React/Next.js)](#frontend-reactnextjs)
   - [Database (MySQL)](#database-mysql)
5. [Running Locally](#running-locally)
6. [Development Workflow](#development-workflow)
7. [Contributing](#contributing)
8. [Troubleshooting](#troubleshooting)
9. [License](#license)

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
- **Java ≥17**
- **Python ≥3.9**
- **Node.js ≥16** (for React frontend)
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


### OCR Service (Python)

```bash
cd ocr_service
cp .env.example .env
pip install -r requirements.txt
python ocr_watcher.py           # or: docker-compose up ocr
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


> **Note:** Node.js is only required for developing and building the React frontend. The OCR service is Python-based.

- **Lint:**

  ```sh
  npm run lint
  ```

- **Tests:**

  ```sh
  npm test
  ```

### Database (MySQL)

- Uses the Docker service defined below
- See detailed database setup and schema in [README_DB.md](./database/README_DB.md)
- See [Scanned Documents Table Structure](#scanned-documents-table-structure) for schema and usage

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

## Scanned Documents Table Structure

All successfully OCR-processed documents are stored in the `scanned_documents` table. This table powers the frontend search page, allowing staff to filter or find documents by client name or account number.

### Table Schema (MySQL Example)

```sql
CREATE TABLE scanned_documents (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  client_name     VARCHAR(255) NOT NULL,
  account_number  VARCHAR(100) NOT NULL,
  filename        VARCHAR(255) NOT NULL UNIQUE,
  filepath        TEXT NOT NULL,
  indexed_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_client_account (client_name, account_number)
);
```

- `client_name`, `account_number`: Extracted by OCR, used for file renaming and searching.
- `filename`: New filename after renaming.
- `filepath`: Full location of the renamed file (e.g., `fully_indexed/john_doe_12345.pdf`).
- `indexed_at`: Timestamp auto-recorded when the row is inserted.

### How the OCR System Uses the Database

- After a file is successfully indexed (moved to `fully_indexed`), the OCR system inserts a row into `scanned_documents` with the extracted metadata and file path.
- The frontend queries this table to allow staff to search/filter by client name or account number.

### Example Python Insert (using `mysql-connector-python`)

```python
import mysql.connector
from datetime import datetime

def insert_scanned_document(client_name, account_number, filename, filepath):
    conn = mysql.connector.connect(
        host='localhost', user='ocr_user', password='yourpassword', database='ocr_db'
    )
    cursor = conn.cursor()
    sql = '''INSERT INTO scanned_documents (client_name, account_number, filename, filepath, indexed_at)
             VALUES (%s, %s, %s, %s, %s)'''
    cursor.execute(sql, (client_name, account_number, filename, filepath, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()
```

### Indexing & Performance

- The table is indexed by `(client_name, account_number)` for fast search.
- Duplicate checks should be performed before insert (e.g., check if a file with the same name/path exists).

---

## Data Flow Overview

1. **Watcher:** Detects new PDF in `incoming-scan/`, runs OCR, extracts `client_name` & `account_number`, renames/moves file to `fully_indexed/`.
2. **Database Insert:** Inserts metadata into `scanned_documents`.
3. **Frontend Search:** React app queries the backend, which runs SQL against `scanned_documents` and returns results for the UI.

---

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

- **Commit messages:** clear, imperative, prefixed by type (`feat:`, `fix:`)
- **Protect dev:** all merges require Pull Requests, approvals, and passing CI.

---

## Troubleshooting

- **Docker won’t start**
  - Make sure Docker Desktop is running and you have enough memory allocated.
- **Database connection refused**
  - Check your `.env` file and ensure MySQL is running on port 3306.
- **Frontend won’t build**
  - Make sure you have Node.js ≥16 and have run `npm install` in the frontend directory.
- **OCR service errors**
  - Ensure all Python dependencies are installed and Tesseract is available in your PATH.
- **Permission denied on file moves**
  - Run your terminal as administrator or check folder permissions.

For more help, see the [Issues](https://github.com/g4Joey/MerbanHub/issues) page or contact a maintainer.

---

## Honor Statement

## License

This repository and its source code are proprietary and the exclusive property of the MerbanHub Team. All Rights Reserved.

Unauthorized use, copying, modification, or distribution of any part of this codebase is strictly prohibited without prior written permission from the copyright holders. For inquiries, contact the repository owner or maintainers.

---

## Honor Statement

We, the contributors to MerbanHub, pledge that all work in this repository is original or properly attributed. We commit to upholding academic and professional integrity by not submitting plagiarized or uncredited work. All external code, libraries, or resources used are clearly cited in the documentation or code comments.

---


