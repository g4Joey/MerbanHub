-- MerbanHub OCR Database Setup
-- MySQL Database Schema for Document Management System

-- Create database (uncomment if needed)
-- CREATE DATABASE IF NOT EXISTS merbanhub_ocr;
-- USE merbanhub_ocr;

-- Drop table if exists (for clean setup)
DROP TABLE IF EXISTS scanned_documents;

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

-- Insert sample data for testing (optional)
INSERT INTO scanned_documents (client_name, account_number, filename, filepath) VALUES
('JOHN_DOE', '123456789', 'JOHN_DOE_123456789.pdf', '/fully_indexed/JOHN_DOE_123456789.pdf'),
('JANE_SMITH', '987654321', 'JANE_SMITH_987654321.pdf', '/fully_indexed/JANE_SMITH_987654321.pdf'),
('AKUA_BISSI', '34007802837', 'AKUA_BISSI_34007802837.pdf', '/fully_indexed/AKUA_BISSI_34007802837.pdf');

-- Verify table creation
DESCRIBE scanned_documents;

-- Show sample data
SELECT * FROM scanned_documents;
