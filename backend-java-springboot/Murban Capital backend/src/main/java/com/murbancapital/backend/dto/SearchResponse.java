package com.murbancapital.backend.dto;

import lombok.*;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SearchResponse {
    private List<Document> documents; // Use dto.Document
    private long total;
    private int page;
    private int pageSize;
    private int totalPages;
}
