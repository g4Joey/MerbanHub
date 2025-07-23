package com.murbancapital.backend.dto;

import com.murbancapital.backend.model.Document;
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
}

