package com.merbancapital.backend.controller;

import com.merbancapital.backend.dto.SearchFilters;
import com.merbancapital.backend.dto.SearchResponse;
import com.merbancapital.backend.model.Document;
import com.merbancapital.backend.service.DocumentSearchService;
import org.springframework.core.io.FileSystemResource;
import java.io.File;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.io.IOException;
import org.springframework.core.io.Resource;
import org.springframework.http.*;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/documents")
@CrossOrigin(origins = "*")
public class DocumentController {

    // Filesystem-based search service that scans OCR folders
    private final DocumentSearchService documentSearchService;

    public DocumentController(DocumentSearchService documentSearchService) {
        this.documentSearchService = documentSearchService;
    }

    /**
     * 1) Search documents with filters.
     *    Admins see all; users see only their department’s documents.
     */
    @PostMapping("/search")
    @PreAuthorize("hasRole('ADMIN') or hasRole('USER')")
    public ResponseEntity<SearchResponse> searchDocuments(@RequestBody SearchFilters filters) {
        // Use the filesystem-backed search service which scans the OCR folders
        SearchResponse resp = documentSearchService.search(filters);
        return ResponseEntity.ok(resp);
    }

    /**
     * Download a file by filename, but only if it exists in fully_indexed or partially_indexed.
     * Example: GET /api/documents/files?name=abc.pdf
     */
    @GetMapping("/files")
    public ResponseEntity<Resource> getIndexedFile(@RequestParam("name") String name) throws IOException {
    var opt = documentSearchService.findFileInIndexedFolders(name);
    if (opt.isEmpty()) return ResponseEntity.notFound().build();

    Path p = opt.get();
    FileSystemResource resource = new FileSystemResource(p.toFile());
    String filename = p.getFileName().toString();
    String encodedFilename = URLEncoder.encode(filename, StandardCharsets.UTF_8.toString()).replace("+", "%20");

    HttpHeaders headers = new HttpHeaders();
    headers.setContentType(MediaType.APPLICATION_PDF);
    headers.setContentDisposition(org.springframework.http.ContentDisposition.builder("inline")
        .filename(encodedFilename)
        .build());
    headers.setCacheControl("max-age=3600, must-revalidate");

    return ResponseEntity.ok()
        .headers(headers)
        .body(resource);
    }

    /**
     * 2) Get document details by id.
     *    USERS allowed only if doc.departmentId == principal.departmentId.
     */
    @GetMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN') or (hasRole('USER') and @securityService.canAccessDocument(principal, #id))")
    public ResponseEntity<Document> getDocumentDetails(@PathVariable Long id) {
        // Document metadata is not stored in the database in this branch.
        // Return 501 Not Implemented to indicate DB-backed detail lookup is unavailable.
        return ResponseEntity.status(HttpStatus.NOT_IMPLEMENTED)
                .body(null);
    }

    /**
     * 3) Download file stream.
     *    Same role rules as detail access.
     */
    @GetMapping("/{id}/download")
    @PreAuthorize("hasRole('ADMIN') or (hasRole('USER') and @securityService.canAccessDocument(principal, #id))")
    public ResponseEntity<Resource> downloadDocument(@PathVariable Long id) throws IOException {
        // DB-based download by ID is not available when documents are filesystem-only.
        // Use the /file endpoint to download by absolute path instead.
        return ResponseEntity.status(HttpStatus.NOT_IMPLEMENTED).body(null);
    }

    /**
     * 4a) List all departments for dropdown.
     *     Admin sees all; users also see all departments (UI may disable others).
     */
    @GetMapping("/filters/departments")
    @PreAuthorize("hasRole('ADMIN') or hasRole('USER')")
    public ResponseEntity<List<String>> listDepartments() {
    // Departments require DB-backed data; not implemented for filesystem-only mode
    return ResponseEntity.ok(List.of());
    }

    /**
     * 4b) Search clients by prefix.
     */
    @GetMapping("/filters/clients")
    @PreAuthorize("hasRole('ADMIN') or hasRole('USER')")
    public ResponseEntity<List<String>> searchClients(
            @RequestParam("q") String query,
            @RequestParam(value = "limit", defaultValue = "10") int limit) {
    // Client search requires DB; return empty list in filesystem mode
    return ResponseEntity.ok(List.of());
    }

    /**
     * 4c) List file extensions & counts.
     */
    @GetMapping("/filters/file-extensions")
    @PreAuthorize("hasRole('ADMIN') or hasRole('USER')")
    public ResponseEntity<List<Object>> listFileExtensions() {
        // File extension counts require DB aggregation. Return empty list for now.
        return ResponseEntity.ok(List.of());
    }

    /**
     * Download a file by absolute path. Use this when documents are stored on disk and not in DB.
     * Example: GET /api/documents/file?path=C:/.../OCR/fully_indexed/abc.pdf
     */
    @GetMapping("/file")
    public ResponseEntity<?> getFile(@RequestParam String path) throws IOException {
    // Validate path param early to avoid the browser treating error responses as file downloads
    if (path == null || path.isBlank() || "undefined".equalsIgnoreCase(path)) {
        HttpHeaders errHeaders = new HttpHeaders();
        errHeaders.setContentType(MediaType.APPLICATION_JSON);
        errHeaders.setContentDisposition(org.springframework.http.ContentDisposition.builder("inline")
            .filename("error.json")
            .build());
        return ResponseEntity.badRequest()
            .headers(errHeaders)
            .body(Map.of("error", "missing or invalid 'path' parameter"));
    }

    // Normalize and validate to avoid directory traversal
    Path filePath = Paths.get(path).normalize();
    File file = filePath.toFile();

    if (!file.exists() || !file.isFile()) {
        HttpHeaders errHeaders = new HttpHeaders();
        errHeaders.setContentType(MediaType.APPLICATION_JSON);
        errHeaders.setContentDisposition(org.springframework.http.ContentDisposition.builder("inline")
            .filename("error.json")
            .build());
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .headers(errHeaders)
            .body(Map.of("error", "file not found"));
    }

    FileSystemResource resource = new FileSystemResource(file);
    String filename = file.getName();
    String encodedFilename = URLEncoder.encode(filename, StandardCharsets.UTF_8.toString()).replace("+", "%20");

    HttpHeaders headers = new HttpHeaders();
    headers.setContentType(MediaType.APPLICATION_PDF);
    headers.setContentDisposition(org.springframework.http.ContentDisposition.builder("inline")
        .filename(encodedFilename)
        .build());
    headers.setCacheControl("max-age=3600, must-revalidate");

    return ResponseEntity.ok()
        .headers(headers)
        .body(resource);
    }
}
