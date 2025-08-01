# Robust Database Setup for MerbanHub OCR System

## Why Use a Database?

While the OCR system can organize files in folders, a database is essential for:

- Fast and flexible search by client name, account number, or date
- Preventing duplicates and ensuring data integrity
- Enabling dashboards, reporting, and future integrations
- Scaling to thousands of documents without slowdowns

## Recommended Table Schema (MySQL Example)

```sql
CREATE TABLE scanned_documents (
  id INT AUTO_INCREMENT PRIMARY KEY,
  client_name VARCHAR(255) NOT NULL,
  account_number VARCHAR(100) NOT NULL,
  filename VARCHAR(255) NOT NULL,
  filepath TEXT NOT NULL,
  indexed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  -- Composite unique constraint for robust deduplication
  UNIQUE KEY uniq_doc (account_number, client_name, indexed_at)
);
```

- `client_name`, `account_number`: Extracted by OCR, used for file renaming and searching.
- `filename`: Includes client name, account number, and timestamp for uniqueness (e.g., `JaneDoe_ACC1234_2025-07-29_153012.pdf`).
- `filepath`: Full location of the renamed file (e.g., `fully_indexed/JaneDoe_ACC1234_2025-07-29_153012.pdf`).
- `indexed_at`: Timestamp auto-recorded when the row is inserted.

## Data Consistency & Integrity

- The composite unique constraint prevents duplicate records for the same client/account/timestamp.
- The OCR watcher should handle database errors gracefully (e.g., skip or log duplicate insert attempts).
- Always include a timestamp or unique string in filenames to avoid accidental overwrites.

## Security Best Practices

- Store database credentials in environment variables or a `.env` file (never hard-coded).
- Use least-privilege database users (e.g., only allow insert/select, not DROP).
- Do not store sensitive data (like passwords) in the scanned_documents table.

## Backup & Recovery

- Regularly back up your MySQL database using `mysqldump` or a managed backup solution.

Example backup command:

```sh
mysqldump -u merbanhub_user -p merbanhub_db > backup_$(date +%F).sql
```

To restore:

```sh
mysql -u merbanhub_user -p merbanhub_db < backup_2025-07-29.sql
```

## Example Queries

- **Find all documents for a client:**

```sql
SELECT * FROM scanned_documents WHERE client_name = 'JaneDoe';
```

- **Find all documents for an account number:**

```sql
SELECT * FROM scanned_documents WHERE account_number = 'ACC1234';
```

- **Find documents in a date range:**

```sql
SELECT * FROM scanned_documents WHERE indexed_at BETWEEN '2025-07-01' AND '2025-07-31';
```

## Example Python Insert (with duplicate handling)

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
    try:
        cursor.execute(sql, (client_name, account_number, filename, filepath, datetime.now()))
        conn.commit()
    except mysql.connector.IntegrityError:
        print(f"[WARNING] Duplicate entry for filename: {filename}. Skipping insert.")
    finally:
        cursor.close()
        conn.close()
```

## Summary Table Example

| Field         | Example Value                |
|---------------|-----------------------------|
| client_name   | JaneDoe                     |
| account_number| ACC1234                     |
| filename      | JaneDoe_ACC1234_2025-07-29_153012.pdf |
| filepath      | fully_indexed/JaneDoe_ACC1234_2025-07-29_153012.pdf |
| indexed_at    | 2025-07-29 15:30:12         |

---

This setup ensures your OCR system is robust, scalable, and ready for advanced search, reporting, and integration needs.
# Robust Database Setup for MerbanHub OCR System

## Why Use a Database?
While the OCR system can organize files in folders, a database is essential for:
- Fast and flexible search by client name, account number, or date
- Preventing duplicates and ensuring data integrity
- Enabling dashboards, reporting, and future integrations
- Scaling to thousands of documents without slowdowns

## Recommended Table Schema (MySQL Example)

```sql
CREATE TABLE scanned_documents (
  id INT AUTO_INCREMENT PRIMARY KEY,
  client_name VARCHAR(255) NOT NULL,
  account_number VARCHAR(100) NOT NULL,
  filename VARCHAR(255) NOT NULL,
  filepath TEXT NOT NULL,
  indexed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  -- Composite unique constraint for robust deduplication
  UNIQUE KEY uniq_doc (account_number, client_name, indexed_at)
);
```

- `client_name`, `account_number`: Extracted by OCR, used for file renaming and searching.
- `filename`: Includes client name, account number, and timestamp for uniqueness (e.g., `JaneDoe_ACC1234_2025-07-29_153012.pdf`).
- `filepath`: Full location of the renamed file (e.g., `fully_indexed/JaneDoe_ACC1234_2025-07-29_153012.pdf`).
- `indexed_at`: Timestamp auto-recorded when the row is inserted.

## Data Consistency & Integrity
- The composite unique constraint prevents duplicate records for the same client/account/timestamp.
- The OCR watcher should handle database errors gracefully (e.g., skip or log duplicate insert attempts).
- Always include a timestamp or unique string in filenames to avoid accidental overwrites.

## Security Best Practices
- Store database credentials in environment variables or a `.env` file (never hard-coded).
- Use least-privilege database users (e.g., only allow insert/select, not DROP).
- Do not store sensitive data (like passwords) in the scanned_documents table.

## Backup & Recovery
- Regularly back up your MySQL database using `mysqldump` or a managed backup solution.
- Example backup command:
  ```sh
  mysqldump -u merbanhub_user -p merbanhub_db > backup_$(date +%F).sql
  ```
- To restore:
  ```sh
  mysql -u merbanhub_user -p merbanhub_db < backup_2025-07-29.sql
  ```

## Example Queries
- **Find all documents for a client:**
  ```sql
  SELECT * FROM scanned_documents WHERE client_name = 'JaneDoe';
  ```
- **Find all documents for an account number:**
  ```sql
  SELECT * FROM scanned_documents WHERE account_number = 'ACC1234';
  ```
- **Find documents in a date range:**
  ```sql
  SELECT * FROM scanned_documents WHERE indexed_at BETWEEN '2025-07-01' AND '2025-07-31';
  ```

## Example Python Insert (with duplicate handling)
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
    try:
        cursor.execute(sql, (client_name, account_number, filename, filepath, datetime.now()))
        conn.commit()
    except mysql.connector.IntegrityError:
        print(f"[WARNING] Duplicate entry for filename: {filename}. Skipping insert.")
    finally:
        cursor.close()
        conn.close()
```

## Summary Table Example
| Field         | Example Value                |
|---------------|-----------------------------|
| client_name   | JaneDoe                     |
| account_number| ACC1234                     |
| filename      | JaneDoe_ACC1234_2025-07-29_153012.pdf |
| filepath      | fully_indexed/JaneDoe_ACC1234_2025-07-29_153012.pdf |
| indexed_at    | 2025-07-29 15:30:12         |

---
This setup ensures your OCR system is robust, scalable, and ready for advanced search, reporting, and integration needs.
