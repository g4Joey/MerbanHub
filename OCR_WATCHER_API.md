# OCR Watcher API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints


### 1. Search Files

**GET** `/search?q=<query>`

- **Description:** Search for files by name or keyword in the indexed folders.
- **Query Parameters:**
  - `q` (string, required): The search term (e.g., part of filename, client name, or account number).
- **Response:**

```json
{
  "results": [
    {
      "filename": "AKUA_BISSI_34007802837.pdf",
      "status": "fully_indexed",
      "path": "fully_indexed/AKUA_BISSI_34007802837.pdf"
    },
    ...
  ]
}
```

### 2. Upload File

**POST** `/upload`

- **Description:** Upload a file to the `incoming-scan` directory for OCR processing.
- **Form Data:**
  - `file` (required): The file to upload (PDF, PNG, JPG, JPEG).
- **Response:**

```json
{
  "success": true,
  "filename": "yourfile.pdf",
  "path": "incoming-scan/yourfile.pdf"
}
```

- **Example using curl:**
  ```sh
  curl -F "file=@path/to/yourfile.pdf" http://localhost:8000/upload
  ```

- **Example using JavaScript (fetch):**
  ```js
  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  fetch('http://localhost:8000/upload', {
    method: 'POST',
    body: formData
  })
    .then(res => res.json())
    .then(data => console.log(data));
  ```


### 3. How to Use

- Make a GET request to `/search` with the `q` parameter.
- Make a POST request to `/upload` with a file.

See examples above for both endpoints.

## Notes

- The API is CORS-enabled, so it can be called from browser-based apps.
- The service automatically watches the scan folder and processes new files.
- Results include the filename, status (fully_indexed, partially_indexed, pending), and file path.
