# MerbanHub

OCR and Document Indexing System for UMB Capital

## Project Overview

MerbanHub is a Node.js-based system for Optical Character Recognition (OCR) and document indexing, designed to streamline document management for UMB Capital.

---

## Team Folders & Responsibilities

- **backend-java-springboot/**  
  For Java Spring Boot backend services.  
  _Lead: Kenny_

- **backend-python-django/**  
  For Python Django backend services.  
  _Lead: Kojo_

- **frontend-react/**  
  For React frontend development.  
  _Leads: Eddie, Lucius_

- **database/**  
  For SQL schema and queries.  
  _Leads: Ruth, Angela_

---

## MySQL Setup for Node.js Backend

### 1. Install MySQL Server

- [Download MySQL Community Server](https://dev.mysql.com/downloads/mysql/)
- Install and set up a root password.

### 2. Create a Database

Open your MySQL client or terminal and run:

```sql
CREATE DATABASE merbanhub_db;
CREATE USER 'merbanhub_user'@'localhost' IDENTIFIED BY 'yourpassword';
GRANT ALL PRIVILEGES ON merbanhub_db.* TO 'merbanhub_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Configure Environment Variables

Create a `.env` file in the `backend` folder (or project root) with:

```env
DB_HOST=localhost
DB_USER=merbanhub_user
DB_PASSWORD=yourpassword
DB_NAME=merbanhub_db
DB_PORT=3306
```

### 4. Install Node.js Dependencies

In the backend folder, run:

```sh
npm install mysql2 dotenv
```

### 5. Sample MySQL Connection (Node.js)

```js
// filepath: src/index.js
const mysql = require('mysql2');
require('dotenv').config();

const connection = mysql.createConnection({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  port: process.env.DB_PORT
});

connection.connect((err) => {
  if (err) {
    console.error('Error connecting to MySQL:', err);
    return;
  }
  console.log('Connected to MySQL database!');
});
```

---

## Development Workflow

### 1. Pull Latest Changes

```sh
git checkout dev
git pull origin dev
```

### 2. Create a Feature Branch

```sh
git checkout -b feature/your-feature-name
```

### 3. Make Changes & Commit

```sh
git add .
git commit -m "Describe your changes"
git push origin feature/your-feature-name
```

### 4. Open a Pull Request

- Go to GitHub and open a pull request from your feature branch into `dev`.

---

## Scripts

- `npm run lint` — Lint the codebase
- `npm test` — Run tests
- `npm run check` — Lint and test

---

## Coding Standards

- Use ESLint for code style.
- Write clear commit messages.
- Ensure all tests pass before submitting a pull request.

---

## Contributing

1. Fork the repository (if needed).
2. Create a feature branch from `dev`.
3. Submit a pull request to `dev`.
4. Request a review from a team member.

---

## License

ISC

---

_For questions, contact the project manager or open an issue._

---

## database/

### Setup MySQL

1. Install MySQL 8 on your computer, or use Docker by running:

   ```sh
   docker-compose up db
   ```

2. Create the database (if not created automatically):

   ```sh
   mysql -u merbanhub_user -pyourpassword -e "CREATE DATABASE merbanhub_db;"
   ```

3. (Optional) Use a MySQL client like MySQL Workbench or DBeaver to connect and manage your database.
4. The database will be available at `localhost:3306` with the credentials set in your `.env` file or `docker-compose.yml`.
