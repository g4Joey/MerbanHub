package com.murbancapital.backend.controller;

import com.murbancapital.backend.dto.SearchFilters;
import com.murbancapital.backend.dto.SearchResponse;
import com.murbancapital.backend.service.DocumentSearchService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.File;
import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.nio.file.Paths;

@RestController
@RequestMapping("/api/documents")
@CrossOrigin(origins = "*") // adjust for production
public class DocumentController {

    @Autowired
    private DocumentSearchService searchService;

    @PostMapping("/search")
    public SearchResponse searchDocuments(@RequestBody SearchFilters filters) {
        // System.out.println("[BACKEND] Received search request with filters: " +
        // filters);
        System.out.println(searchService.search(filters));
        return searchService.search(filters);
    }

    @GetMapping("/file")
    public ResponseEntity<Resource> getFile(@RequestParam String path) throws IOException {
        // Validate and sanitize the path to prevent directory traversal
        Path filePath = Paths.get(path).normalize();
        File file = filePath.toFile();

        if (!file.exists() || !file.isFile()) {
            return ResponseEntity.notFound().build();
        }

        FileSystemResource resource = new FileSystemResource(file);

        // Get filename for Content-Disposition header
        String filename = file.getName();
        String encodedFilename = URLEncoder.encode(filename, StandardCharsets.UTF_8.toString())
                .replace("+", "%20");

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
