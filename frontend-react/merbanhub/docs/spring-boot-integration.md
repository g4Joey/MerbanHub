# Spring Boot Backend Integration Guide

## Overview
This document outlines the API contracts and integration points between the React frontend and Spring Boot backend for the Lucius document search system.

## API Endpoints

### 1. Document Search
**Endpoint:** `POST /api/documents/search`

**Request Body:**
\`\`\`json
{
  "clientName": "string (optional)",
  "accountNumber": "string (optional)", 
  "department": "string (optional)",
  "fundDateStart": "2024-01-01 (optional)",
  "fundDateEnd": "2024-12-31 (optional)",
  "fileExtensions": ["pdf", "docx"] (optional),
  "dateModifiedStart": "2024-01-01 (optional)",
  "dateModifiedEnd": "2024-12-31 (optional)",
  "fileSizeMin": 0 (optional),
  "fileSizeMax": 100000 (optional),
  "ocrConfidenceMin": 80 (optional),
  "indexStatus": "Indexed" (optional),
  "fullTextSearch": "search terms" (optional),
  "page": 1,
  "pageSize": 20,
  "sortBy": "dateModified",
  "sortOrder": "desc"
}
\`\`\`

**Response:**
\`\`\`json
{
  "documents": [
    {
      "id": "string",
      "fileName": "string",
      "clientName": "string", 
      "accountNumber": "string",
      "department": "string",
      "fundDate": "2024-01-15",
      "fileExtension": "pdf",
      "dateModified": "2024-01-20T10:30:00Z",
      "fileSize": 2048000,
      "ocrConfidence": 95,
      "indexStatus": "Indexed",
      "filePath": "string",
      "snippet": "string (optional)"
    }
  ],
  "total": 150,
  "page": 1,
  "pageSize": 20,
  "totalPages": 8
}
\`\`\`

### 2. Document Details
**Endpoint:** `GET /api/documents/{id}`

**Response:**
\`\`\`json
{
  "id": "string",
  "fileName": "string",
  "clientName": "string",
  "accountNumber": "string", 
  "department": "string",
  "fundDate": "2024-01-15",
  "fileExtension": "pdf",
  "dateModified": "2024-01-20T10:30:00Z",
  "fileSize": 2048000,
  "ocrConfidence": 95,
  "indexStatus": "Indexed",
  "filePath": "string",
  "fullText": "string (optional)",
  "metadata": {
    "author": "string",
    "createdDate": "2024-01-15T09:00:00Z",
    "lastModified": "2024-01-20T10:30:00Z",
    "version": "1.0",
    "tags": ["tag1", "tag2"]
  }
}
\`\`\`

### 3. Document Download
**Endpoint:** `GET /api/documents/{id}/download`

**Response:** Binary file stream with appropriate headers:
- `Content-Type`: Based on file type
- `Content-Disposition`: `attachment; filename="document.pdf"`
- `Content-Length`: File size in bytes

### 4. Filter Options

#### Departments
**Endpoint:** `GET /api/filters/departments`
**Response:**
\`\`\`json
{
  "departments": [
    "Accounting",
    "Legal",
    "Operations", 
    "Compliance",
    "Risk Management",
    "Investment",
    "Client Services"
  ]
}
\`\`\`

#### Client Search
**Endpoint:** `GET /api/filters/clients?q={query}&limit={limit}`
**Response:**
\`\`\`json
{
  "clients": [
    "Acme Corporation",
    "Beta Industries"
  ]
}
\`\`\`

#### File Extensions
**Endpoint:** `GET /api/filters/file-extensions`
**Response:**
\`\`\`json
{
  "extensions": [
    {
      "value": "pdf",
      "label": "PDF Document", 
      "count": 1250
    },
    {
      "value": "docx",
      "label": "Word Document",
      "count": 890
    }
  ]
}
\`\`\`

## Implementation Notes

### Search Logic
- **Client Name**: Use case-insensitive LIKE query (`LOWER(client_name) LIKE LOWER('%{query}%')`)
- **Account Number**: Exact match
- **Department**: Exact match
- **Date Ranges**: Use BETWEEN queries for fund_date and date_modified
- **File Extensions**: Use IN clause for multiple extensions
- **File Size**: Convert KB to bytes for database queries
- **OCR Confidence**: Use >= comparison
- **Full Text Search**: Implement using database full-text search capabilities

### Security Considerations
- Implement proper authentication/authorization
- Validate all input parameters
- Log document access for audit trails
- Implement rate limiting for search endpoints
- Sanitize file downloads to prevent path traversal attacks

### Performance Recommendations
- Index frequently searched columns (client_name, account_number, department, fund_date, date_modified)
- Implement database query optimization for complex filters
- Consider caching for filter options (departments, file extensions)
- Implement pagination at database level
- Use database-specific full-text search features for better performance

### Error Handling
Return appropriate HTTP status codes:
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied
- `404 Not Found`: Document not found
- `500 Internal Server Error`: Server errors

### CORS Configuration
Configure CORS to allow requests from the frontend domain:
\`\`\`java
@CrossOrigin(origins = "http://localhost:3000") // Development
@CrossOrigin(origins = "https://your-frontend-domain.com") // Production
