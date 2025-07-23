package com.murbancapital.backend.service;

import com.murbancapital.backend.dto.SearchFilters;
import com.murbancapital.backend.dto.SearchResponse;
import com.murbancapital.backend.model.Document;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class DocumentSearchService {

    private List<Document> documents = new ArrayList<>();

    @PostConstruct
    public void loadMockData() {
        // ——————————————————————————————
        // Copy-paste Lucius’s mockDocuments here:
        documents = List.of(
                Document.builder()
                        .id("1")
                        .fileName("Investment_Agreement_2024_Q1.pdf")
                        .clientName("Acme Corporation")
                        .accountNumber("ACC-001-2024")
                        .department("Investment")
                        .fundDate(LocalDate.parse("2024-01-15"))
                        .fileExtension("pdf")
                        .dateModified(LocalDate.parse("2024-01-20"))
                        .fileSize(2048000)
                        .ocrConfidence(95)
                        .indexStatus("Indexed")
                        .snippet("This investment agreement outlines the terms and conditions for the Q1 2024 funding round...")
                        .filePath("/documents/investment/2024/q1/investment_agreement.pdf")
                        .build()
                // … repeat for documents 2–5 …
        );
    }

    public SearchResponse search(SearchFilters f) {
        // Start with the full list
        List<Document> filtered = new ArrayList<>(documents);

        // Apply each filter if present:
        if (f.getClientName() != null && !f.getClientName().isBlank()) {
            String q = f.getClientName().toLowerCase();
            filtered = filtered.stream()
                    .filter(d -> d.getClientName().toLowerCase().contains(q))
                    .collect(Collectors.toList());
        }
        if (f.getAccountNumber() != null) {
            filtered = filtered.stream()
                    .filter(d -> d.getAccountNumber().equals(f.getAccountNumber()))
                    .collect(Collectors.toList());
        }
        if (f.getDepartment() != null) {
            filtered = filtered.stream()
                    .filter(d -> d.getDepartment().equals(f.getDepartment()))
                    .collect(Collectors.toList());
        }
        if (f.getFundDateStart() != null) {
            filtered = filtered.stream()
                    .filter(d -> !d.getFundDate().isBefore(f.getFundDateStart()))
                    .collect(Collectors.toList());
        }
        if (f.getFundDateEnd() != null) {
            filtered = filtered.stream()
                    .filter(d -> !d.getFundDate().isAfter(f.getFundDateEnd()))
                    .collect(Collectors.toList());
        }
        if (f.getFileExtensions() != null && !f.getFileExtensions().isEmpty()) {
            filtered = filtered.stream()
                    .filter(d -> f.getFileExtensions().contains(d.getFileExtension()))
                    .collect(Collectors.toList());
        }
        if (f.getDateModifiedStart() != null) {
            filtered = filtered.stream()
                    .filter(d -> !d.getDateModified().isBefore(f.getDateModifiedStart()))
                    .collect(Collectors.toList());
        }
        if (f.getDateModifiedEnd() != null) {
            filtered = filtered.stream()
                    .filter(d -> !d.getDateModified().isAfter(f.getDateModifiedEnd()))
                    .collect(Collectors.toList());
        }
        if (f.getFileSizeMin() != null) {
            filtered = filtered.stream()
                    .filter(d -> d.getFileSize() >= f.getFileSizeMin() * 1024)
                    .collect(Collectors.toList());
        }
        if (f.getFileSizeMax() != null) {
            filtered = filtered.stream()
                    .filter(d -> d.getFileSize() <= f.getFileSizeMax() * 1024)
                    .collect(Collectors.toList());
        }
        if (f.getOcrConfidenceMin() != null) {
            filtered = filtered.stream()
                    .filter(d -> d.getOcrConfidence() >= f.getOcrConfidenceMin())
                    .collect(Collectors.toList());
        }
        if (f.getIndexStatus() != null) {
            filtered = filtered.stream()
                    .filter(d -> d.getIndexStatus().equals(f.getIndexStatus()))
                    .collect(Collectors.toList());
        }
        if (f.getFullTextSearch() != null && !f.getFullTextSearch().isBlank()) {
            String q = f.getFullTextSearch().toLowerCase();
            filtered = filtered.stream()
                    .filter(d -> d.getFileName().toLowerCase().contains(q)
                            || d.getSnippet().toLowerCase().contains(q))
                    .collect(Collectors.toList());
        }

        // — Pagination & sorting (simple in‑memory)
        int page    = f.getPage()    == null ? 1 : f.getPage();
        int size    = f.getPageSize()== null ? 20 : f.getPageSize();
        int fromIdx = (page - 1) * size;
        int toIdx   = Math.min(fromIdx + size, filtered.size());

        List<Document> pageList = fromIdx >= filtered.size()
                ? Collections.emptyList()
                : filtered.subList(fromIdx, toIdx);

        return SearchResponse.builder()
                .documents(pageList)
                .total(filtered.size())
                .page(page)
                .pageSize(size)
                .totalPages((int)Math.ceil((double)filtered.size() / size))
                .build();
    }
}

