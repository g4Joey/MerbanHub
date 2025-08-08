package com.merbancapital.backend.dto;

import com.merbancapital.backend.model.Document;
import lombok.*;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SearchResponse {
    private List<Document> documents;
    private long total;
    private int page;
    private int pageSize;
    private int totalPages;
    // All fields from SearchFilters, no default values (will be set in service)
    private String clientName;
    private String accountNumber;
    private String department;
    private String fundDateStart;
    private String fundDateEnd;
    private List<String> fileExtensions;
    private String dateModifiedStart;
    private String dateModifiedEnd;
    private Long fileSizeMin;
    private Long fileSizeMax;
    private Integer ocrConfidenceMin;
    private String indexStatus;
    private String fullTextSearch;
    private String sortBy;
    private String sortOrder;
}
