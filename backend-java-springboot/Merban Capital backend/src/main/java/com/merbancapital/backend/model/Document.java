package com.merbancapital.backend.model;

import lombok.*;

import java.time.LocalDate;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Document {
    private String id;
    private String fileName;
    private String clientName;
    private String accountNumber;
    private String department;
    private LocalDate fundDate;
    private String fileExtension;
    private LocalDate dateModified;
    private long fileSize;
    private int ocrConfidence;
    private String indexStatus;
    private String snippet;
    private String filePath;
}

