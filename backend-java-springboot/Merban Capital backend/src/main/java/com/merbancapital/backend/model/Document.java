package com.merbancapital.backend.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.persistence.*;
import lombok.Getter;

import java.time.Instant;
import java.time.LocalDate;

@Entity
@Table(name = "documents")
public class Document {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "document_id")
    private Integer documentId;

    @ManyToOne
    @JoinColumn(name = "client_id")
    private Client client;

    @Column(name = "client_id", insertable = false, updatable = false)
    private Integer clientId;  // Change to Integer

    @Getter
    @Column(name = "department_id")
    private Integer departmentId;

    @Column(name = "file_name", nullable = false)
    private String fileName;

    @Column(name = "file_path", nullable = false, columnDefinition = "TEXT")
    private String filePath;

    @Column(name = "date_modified", nullable = false)
    private Instant dateModified;

    @Column(name = "fund_date")
    private LocalDate fundDate;

    @Column(name = "file_extension", nullable = false)
    private String fileExtension;

    @Column(name = "file_size")
    private Long fileSize;

    @Column(name = "ocr_confidence")
    private Integer ocrConfidence;

    @Enumerated(EnumType.STRING)
    @Column(name = "index_status", nullable = false)
    private IndexStatus indexStatus;

    @Column(name = "snippet", columnDefinition = "TEXT")
    private String snippet;

    public enum IndexStatus {
        Indexed, Pending, Error
    }

    public Document() {
    }

    // Getters & setters

    public Integer getDocumentId() {
        return documentId;
    }
    public void setDocumentId(Integer documentId) {
        this.documentId = documentId;
    }

    public Integer getClientId() {
        return clientId;
    }

    public void setClientId(Integer clientId) {
        this.clientId = clientId;
    }

    public void setDepartmentId(Integer departmentId) {
        this.departmentId = departmentId;
    }

    public String getFileName() {
        return fileName;
    }
    public void setFileName(String fileName) {
        this.fileName = fileName;
    }

    @JsonProperty("name")
    public String getNameForJson() {
        return fileName;
    }

    public String getFilePath() {
        return filePath;
    }
    public void setFilePath(String filePath) {
        this.filePath = filePath;
    }

    @JsonProperty("path")
    public String getPathForJson() {
        return filePath;
    }

    public Instant getDateModified() {
        return dateModified;
    }
    public void setDateModified(Instant dateModified) {
        this.dateModified = dateModified;
    }

    public LocalDate getFundDate() {
        return fundDate;
    }
    public void setFundDate(LocalDate fundDate) {
        this.fundDate = fundDate;
    }

    public String getFileExtension() {
        return fileExtension;
    }
    public void setFileExtension(String fileExtension) {
        this.fileExtension = fileExtension;
    }

    public Long getFileSize() {
        return fileSize;
    }
    public void setFileSize(Long fileSize) {
        this.fileSize = fileSize;
    }

    public Integer getOcrConfidence() {
        return ocrConfidence;
    }
    public void setOcrConfidence(Integer ocrConfidence) {
        this.ocrConfidence = ocrConfidence;
    }

    public IndexStatus getIndexStatus() {
        return indexStatus;
    }
    public void setIndexStatus(IndexStatus indexStatus) {
        this.indexStatus = indexStatus;
    }

    public String getSnippet() {
        return snippet;
    }
    public void setSnippet(String snippet) {
        this.snippet = snippet;
    }
}