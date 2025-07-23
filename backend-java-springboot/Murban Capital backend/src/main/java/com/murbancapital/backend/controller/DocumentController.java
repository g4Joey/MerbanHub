package com.murbancapital.backend.controller;

import com.murbancapital.backend.dto.SearchFilters;
import com.murbancapital.backend.dto.SearchResponse;
import com.murbancapital.backend.service.DocumentSearchService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/documents")
@CrossOrigin(origins = "http://localhost:3000")  // adjust for production
public class DocumentController {

    @Autowired
    private DocumentSearchService searchService;

    @PostMapping("/search")
    public SearchResponse searchDocuments(@RequestBody SearchFilters filters) {
        return searchService.search(filters);
    }
}
