package com.merbancapital.backend.dto;

import lombok.*;

import java.time.LocalDate;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SearchFilters {
    private String clientName;
    private String accountNumber;
    private String department;
    private LocalDate fundDateStart;
    private LocalDate fundDateEnd;
    private List<String> fileExtensions;
    private LocalDate dateModifiedStart;
    private LocalDate dateModifiedEnd;
    private Long fileSizeMin;     // in KB
    private Long fileSizeMax;     // in KB
    private Integer ocrConfidenceMin;
    private String indexStatus;
    private String fullTextSearch;
    private Integer page;
    private Integer pageSize;
    private String sortBy;
    private String sortOrder;
    
    public Integer getOcrConfidenceMin() {
        return ocrConfidenceMin;
    }

    public void setOcrConfidenceMin(Integer ocrConfidenceMin) {
        this.ocrConfidenceMin = ocrConfidenceMin;
    }
}
