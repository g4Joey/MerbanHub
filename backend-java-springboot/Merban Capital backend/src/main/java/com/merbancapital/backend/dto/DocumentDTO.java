package com.merbancapital.backend.dto;

import jakarta.validation.constraints.*;
import java.time.Instant;

public class DocumentDTO {

    // All-args constructor (for your mapping code):
    public DocumentDTO(Long id,
                       String fileName,
                       String clientName,
                       String accountNumber,
                       String department,
                       String fundDate,
                       String fileExtension,
                       Instant dateModified,
                       Long fileSize,
                       Integer ocrConfidence,
                       String indexStatus,
                       String snippet,
                       String filePath) {
        // Required fields validation
        if (fileName == null || fileName.trim().isEmpty()) {
            throw new IllegalArgumentException("File name is required");
        }
        if (clientName == null || clientName.trim().isEmpty()) {
            throw new IllegalArgumentException("Client name is required");
        }
        if (department == null || department.trim().isEmpty()) {
            throw new IllegalArgumentException("Department is required");
        }
        if (filePath == null || filePath.trim().isEmpty()) {
            throw new IllegalArgumentException("File path is required");
        }

        this.id = id;
        this.fileName = fileName.trim();
        this.clientName = clientName.trim();
        this.accountNumber = accountNumber;
        this.department = department.trim();
        this.fundDate = fundDate;
        this.fileExtension = fileExtension;
        this.dateModified = dateModified;
        this.fileSize = fileSize;
        this.ocrConfidence = ocrConfidence;
        this.indexStatus = indexStatus;
        this.snippet = snippet;
        this.filePath = filePath.trim();
    }

    private Long id;

    @NotBlank(message = "File name is required")
    @Size(max = 255, message = "File name must not exceed 255 characters")
    private String fileName;

    @NotBlank(message = "Client name is required")
    @Size(max = 100, message = "Client name must not exceed 100 characters")
    private String clientName;

    @Pattern(regexp = "^[0-9]{1,20}$", message = "Account number must contain only digits")
    private String accountNumber;

    @NotBlank(message = "Department is required")
    private String department;

    @Pattern(regexp = "^\\d{4}-\\d{2}-\\d{2}$", message = "Fund date must be in format YYYY-MM-DD")
    private String fundDate;

    @Pattern(regexp = "^\\.[a-zA-Z0-9]{1,10}$", message = "File extension must start with a dot and contain only alphanumeric characters")
    private String fileExtension;

    @PastOrPresent(message = "Modified date cannot be in the future")
    private Instant dateModified;

    @Positive(message = "File size must be positive")
    private Long fileSize;

    @Min(value = 0, message = "OCR confidence must be between 0 and 100")
    @Max(value = 100, message = "OCR confidence must be between 0 and 100")
    private Integer ocrConfidence;

    @NotNull(message = "Index status is required")
    @Pattern(regexp = "^(PENDING|COMPLETED|FAILED)$", message = "Invalid index status")
    private String indexStatus;

    private String snippet;

    @NotBlank(message = "File path is required")
    @Size(max = 1024, message = "File path must not exceed 1024 characters")
    private String filePath;

    // Getters for all fields (IDE-generate these)
    public Long getId() { return id; }
    public String getFileName() { return fileName; }
    public String getClientName() { return clientName; }
    public String getAccountNumber() { return accountNumber; }
    public String getDepartment() { return department; }
    public String getFundDate() { return fundDate; }
    public String getFileExtension() { return fileExtension; }
    public Instant getDateModified() { return dateModified; }
    public Long getFileSize() { return fileSize; }
    public Integer getOcrConfidence() { return ocrConfidence; }
    public String getIndexStatus() { return indexStatus; }
    public String getSnippet() { return snippet; }
    public String getFilePath() { return filePath; }

    // No setters required if you treat it as immutable
}

    // Constructor and getters remain the same




