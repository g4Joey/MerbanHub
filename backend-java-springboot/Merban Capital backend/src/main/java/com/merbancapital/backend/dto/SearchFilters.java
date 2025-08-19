package com.merbancapital.backend.dto;

import jakarta.validation.constraints.*;
import lombok.*;

import java.time.LocalDate;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SearchFilters {
    @Size(max = 100, message = "Client name must not exceed 100 characters")
    private String clientName;

    @Pattern(regexp = "^[0-9]{1,20}$", message = "Account number must contain only digits")
    private String accountNumber;

    @Size(max = 50, message = "Department must not exceed 50 characters")
    private String department;

    @PastOrPresent(message = "Fund date start cannot be in the future")
    private LocalDate fundDateStart;

    @PastOrPresent(message = "Fund date end cannot be in the future")
    private LocalDate fundDateEnd;

    private List<String> fileExtensions;

    @PastOrPresent(message = "Modified date start cannot be in the future")
    private LocalDate dateModifiedStart;

    @PastOrPresent(message = "Modified date end cannot be in the future")
    private LocalDate dateModifiedEnd;

    @PositiveOrZero(message = "Minimum file size cannot be negative")
    private Long fileSizeMin;

    @Positive(message = "Maximum file size must be positive")
    private Long fileSizeMax;

    @Min(value = 0, message = "OCR confidence minimum must be between 0 and 100")
    @Max(value = 100, message = "OCR confidence minimum must be between 0 and 100")
    private Integer ocrConfidenceMin;

    @Pattern(regexp = "^(PENDING|COMPLETED|FAILED)$", message = "Invalid index status")
    private String indexStatus;

    @Size(max = 1000, message = "Full text search must not exceed 1000 characters")
    private String fullTextSearch;

    @Min(value = 0, message = "Page number cannot be negative")
    private Integer page;

    @Min(value = 1, message = "Page size must be at least 1")
    @Max(value = 100, message = "Page size must not exceed 100")
    private Integer pageSize;

    @Pattern(regexp = "^[a-zA-Z0-9_]+$", message = "Sort by must contain only alphanumeric characters and underscores")
    private String sortBy;

    @Pattern(regexp = "^(asc|desc)$", message = "Sort order must be 'asc' or 'desc'")
    private String sortOrder;
    
    public Integer getOcrConfidenceMin() {
        return ocrConfidenceMin;
    }

    public void setOcrConfidenceMin(Integer ocrConfidenceMin) {
        this.ocrConfidenceMin = ocrConfidenceMin;
    }
}
