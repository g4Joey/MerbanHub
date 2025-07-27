package com.merbancapital.backend.dto;

import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OcrMetadata {
    private String originalFileName;
    private String newFileName;
    private String clientName;
    private String accountNumber;
    private String status;    // FULLY_INDEXED, PARTIAL_INDEXED, FAILED
}
