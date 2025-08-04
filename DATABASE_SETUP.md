# Database Setup Instructions

This guide explains how to set up the MySQL database for the MerbanHub OCR system.

## Quick Setup

### 1. Install MySQL
- Download and install MySQL 8.0+ from https://dev.mysql.com/downloads/mysql/
- Or use Docker: `docker run -d --name mysql-ocr -e MYSQL_ROOT_PASSWORD=root -p 3306:3306 mysql:8.0`

### 2. Create Database and User
```sql
-- Connect as root
mysql -u root -p

-- Create database
CREATE DATABASE IF NOT EXISTS merbanhub_ocr;

-- Create user (replace with your preferred credentials)
CREATE USER 'merbanhub_user'@'localhost' IDENTIFIED BY 'yourpassword';
GRANT ALL PRIVILEGES ON merbanhub_ocr.* TO 'merbanhub_user'@'localhost';
FLUSH PRIVILEGES;

-- Use the database
USE merbanhub_ocr;
```

### 3. Create Tables
Run the SQL script:
```bash
mysql -u merbanhub_user -p merbanhub_ocr < database_setup.sql
```

Or execute manually:
```sql
-- Create scanned_documents table
CREATE TABLE scanned_documents (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  client_name     VARCHAR(255) NOT NULL,
  account_number  VARCHAR(100) NOT NULL,
  filename        VARCHAR(255) NOT NULL UNIQUE,
  filepath        TEXT NOT NULL,
  indexed_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  -- Indexes for performance
  INDEX idx_client_account (client_name, account_number),
  INDEX idx_filename (filename),
  INDEX idx_indexed_at (indexed_at)
);
```

### 4. Configure Environment
Copy `.env.example` to `.env` and update the database settings:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=merbanhub_user
DB_PASSWORD=yourpassword
DB_NAME=merbanhub_ocr
```

### 5. Test Connection
The OCR application will automatically test the database connection on startup and create the table if it doesn't exist.

## Table Structure

### scanned_documents
Stores metadata for all successfully processed documents.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT AUTO_INCREMENT | Primary key |
| `client_name` | VARCHAR(255) | Extracted client name (e.g., "JOHN_DOE") |
| `account_number` | VARCHAR(100) | Extracted account number (e.g., "123456789") |
| `filename` | VARCHAR(255) UNIQUE | New filename after processing |
| `filepath` | TEXT | Full path to processed file |
| `indexed_at` | TIMESTAMP | When the record was created |

### Indexes
- `idx_client_account`: Composite index on (client_name, account_number) for fast searches
- `idx_filename`: Index on filename for unique constraint and lookups
- `idx_indexed_at`: Index on timestamp for date-based queries

## Usage Examples

### Search by Client Name
```sql
SELECT * FROM scanned_documents 
WHERE client_name LIKE '%JOHN%' 
ORDER BY indexed_at DESC;
```

### Search by Account Number
```sql
SELECT * FROM scanned_documents 
WHERE account_number = '123456789';
```

### Get Recent Documents
```sql
SELECT * FROM scanned_documents 
ORDER BY indexed_at DESC 
LIMIT 10;
```

### Count Documents by Client
```sql
SELECT client_name, COUNT(*) as document_count 
FROM scanned_documents 
GROUP BY client_name 
ORDER BY document_count DESC;
```

## Troubleshooting

### Connection Issues
1. Check MySQL service is running: `systemctl status mysql` (Linux) or Services (Windows)
2. Verify credentials in `.env` file
3. Test connection: `mysql -u merbanhub_user -p -h localhost merbanhub_ocr`

### Permission Issues
```sql
-- Grant all privileges again
GRANT ALL PRIVILEGES ON merbanhub_ocr.* TO 'merbanhub_user'@'localhost';
FLUSH PRIVILEGES;
```

### Table Already Exists
The application will create tables automatically if they don't exist. To recreate:
```sql
DROP TABLE IF EXISTS scanned_documents;
-- Then run the CREATE TABLE statement again
```

## Docker Compose Setup

For development, you can use the provided docker-compose.yml:

```bash
# Start MySQL with Docker Compose
docker-compose up -d db

# Connect to MySQL container
docker exec -it <container_name> mysql -u root -p

# Run setup commands...
```

The database will be accessible on `localhost:3306` with the credentials from your `.env` file.
