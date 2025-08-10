package com.merbancapital.backend.controller;

import com.merbancapital.backend.dto.SearchFilters;
import com.merbancapital.backend.dto.SearchResponse;
import com.merbancapital.backend.model.Document;
import com.merbancapital.backend.service.DocumentService;
import org.springframework.core.io.Resource;
import org.springframework.http.*;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.util.List;

@RestController
@RequestMapping("/api/documents")
@CrossOrigin(origins = "*")
public class DocumentController {

    private final DocumentService documentService;

    public DocumentController(DocumentService documentService) {
        this.documentService = documentService;
    }

    /**
     * 1) Search documents with filters.
     *    Admins see all; users see only their department’s documents.
     */
    @PostMapping("/search")
    @PreAuthorize("hasRole('ADMIN') or hasRole('USER')")
    public ResponseEntity<SearchResponse> searchDocuments(@RequestBody SearchFilters filters) {
        // service should enforce department scoping internally for USER role
        SearchResponse resp = documentService.search(filters);
        return ResponseEntity.ok(resp);
    }

    /**
     * 2) Get document details by id.
     *    USERS allowed only if doc.departmentId == principal.departmentId.
     */
    @GetMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN') or (hasRole('USER') and @securityService.canAccessDocument(principal, #id))")
    public ResponseEntity<Document> getDocumentDetails(@PathVariable Long id) {
        Document doc = documentService.getById(id);
        return ResponseEntity.ok(doc);
    }

    /**
     * 3) Download file stream.
     *    Same role rules as detail access.
     */
    @GetMapping("/{id}/download")
    @PreAuthorize("hasRole('ADMIN') or (hasRole('USER') and @securityService.canAccessDocument(principal, #id))")
    public ResponseEntity<Resource> downloadDocument(@PathVariable Long id) throws IOException {
        Resource file = documentService.loadAsResource(id);
        String filename = file.getFilename();
        return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_OCTET_STREAM)
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + filename + "\"")
                .body(file);
    }

    /**
     * 4a) List all departments for dropdown.
     *     Admin sees all; users also see all departments (UI may disable others).
     */
    @GetMapping("/filters/departments")
    @PreAuthorize("hasRole('ADMIN') or hasRole('USER')")
    public ResponseEntity<List<String>> listDepartments() {
        return ResponseEntity.ok(documentService.getAllDepartments());
    }

    /**
     * 4b) Search clients by prefix.
     */
    @GetMapping("/filters/clients")
    @PreAuthorize("hasRole('ADMIN') or hasRole('USER')")
    public ResponseEntity<List<String>> searchClients(
            @RequestParam("q") String query,
            @RequestParam(value = "limit", defaultValue = "10") int limit) {
        return ResponseEntity.ok(documentService.findClients(query, limit));
    }

    /**
     * 4c) List file extensions & counts.
     */
    @GetMapping("/filters/file-extensions")
    @PreAuthorize("hasRole('ADMIN') or hasRole('USER')")
    public ResponseEntity<List<DocumentService.ExtensionCount>> listFileExtensions() {
        return ResponseEntity.ok(documentService.getExtensionCounts());
    }
}
