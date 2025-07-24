package com.murbancapital.backend.service;

import com.murbancapital.backend.dto.SearchFilters;
import com.murbancapital.backend.dto.SearchResponse;
import com.murbancapital.backend.dto.Document; // Use the new DTO
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Value;

import jakarta.annotation.PostConstruct;
import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.Stream;

@Service
public class DocumentSearchService {
        private List<Document> documents = Collections.synchronizedList(new ArrayList<>());

        @Value("${ocr.base.path}")
        private String ocrBasePath;

        private static final String FULLY_INDEXED_DIR = "fully_indexed";
        private static final String PARTIALLY_INDEXED_DIR = "partially_indexed";
        private static final String FAILED_DIR = "failed";

        @PostConstruct
        public void init() {
                System.out.println("[DocumentSearchService] Initializing with OCR base path: " + ocrBasePath);
                scanOcrFolders();
        }

        public void scanOcrFolders() {
                List<Document> newDocuments = new ArrayList<>();
                List<Path> directoriesToScan = List.of(
                                Paths.get(ocrBasePath, FULLY_INDEXED_DIR),
                                Paths.get(ocrBasePath, PARTIALLY_INDEXED_DIR),
                                Paths.get(ocrBasePath, FAILED_DIR));
                for (Path dirPath : directoriesToScan) {
                        if (Files.exists(dirPath) && Files.isDirectory(dirPath)) {
                                try (Stream<Path> paths = Files.list(dirPath)) {
                                        paths.filter(Files::isRegularFile)
                                                        .forEach(filePath -> {
                                                                try {
                                                                        BasicFileAttributes attr = Files.readAttributes(
                                                                                        filePath,
                                                                                        BasicFileAttributes.class);
                                                                        String fileName = filePath.getFileName()
                                                                                        .toString();
                                                                        long fileSize = attr.size();
                                                                        long lastModified = attr.lastModifiedTime()
                                                                                        .toMillis();
                                                                        String absolutePath = filePath.toAbsolutePath()
                                                                                        .toString();
                                                                        Document doc = new Document(fileName, fileSize,
                                                                                        lastModified, absolutePath);
                                                                        newDocuments.add(doc);
                                                                } catch (IOException e) {
                                                                        System.err.println(
                                                                                        "[ERROR] Could not read attributes for file: "
                                                                                                        + filePath
                                                                                                        + " - "
                                                                                                        + e.getMessage());
                                                                }
                                                        });
                                } catch (IOException e) {
                                        System.err.println("[ERROR] Could not list files in directory: " + dirPath
                                                        + " - " + e.getMessage());
                                }
                        } else {
                                System.out.println("[WARNING] OCR directory not found or not a directory: " + dirPath);
                        }
                }
                synchronized (documents) {
                        documents.clear();
                        documents.addAll(newDocuments);
                        System.out.println("[DocumentSearchService] Rescanned. Total documents loaded: "
                                        + documents.size());
                }
        }

        public SearchResponse search(SearchFilters f) {
                List<Document> filtered = new ArrayList<>(documents);
                // You can add simple filters here if needed, e.g. by name
                if (f.getClientName() != null && !f.getClientName().isBlank()) {
                        String q = f.getClientName().toLowerCase();
                        filtered = filtered.stream()
                                        .filter(d -> d.getName() != null && d.getName().toLowerCase().contains(q))
                                        .collect(Collectors.toList());
                }
                // Pagination (optional)
                int page = f.getPage() == null ? 1 : f.getPage();
                int size = f.getPageSize() == null ? 20 : f.getPageSize();
                int fromIdx = (page - 1) * size;
                int toIdx = Math.min(fromIdx + size, filtered.size());
                List<Document> pageList = fromIdx >= filtered.size() ? Collections.emptyList()
                                : filtered.subList(fromIdx, toIdx);
                return SearchResponse.builder()
                                .documents(pageList)
                                .total(filtered.size())
                                .page(page)
                                .pageSize(size)
                                .totalPages((int) Math.ceil((double) filtered.size() / size))
                                .clientName(f.getClientName() == null ? "" : f.getClientName())
                                .accountNumber(f.getAccountNumber() == null ? "" : f.getAccountNumber())
                                .department(f.getDepartment() == null ? "" : f.getDepartment())
                                .fundDateStart(f.getFundDateStart() == null ? "" : f.getFundDateStart().toString())
                                .fundDateEnd(f.getFundDateEnd() == null ? "" : f.getFundDateEnd().toString())
                                .fileExtensions(f.getFileExtensions() == null ? List.of() : f.getFileExtensions())
                                .dateModifiedStart(f.getDateModifiedStart() == null ? ""
                                                : f.getDateModifiedStart().toString())
                                .dateModifiedEnd(
                                                f.getDateModifiedEnd() == null ? "" : f.getDateModifiedEnd().toString())
                                .fileSizeMin(f.getFileSizeMin() == null ? 0L : f.getFileSizeMin())
                                .fileSizeMax(f.getFileSizeMax() == null ? 0L : f.getFileSizeMax())
                                .ocrConfidenceMin(f.getOcrConfidenceMin() == null ? 0 : f.getOcrConfidenceMin())
                                .indexStatus(f.getIndexStatus() == null ? "" : f.getIndexStatus())
                                .fullTextSearch(f.getFullTextSearch() == null ? "" : f.getFullTextSearch())
                                .sortBy(f.getSortBy() == null ? "" : f.getSortBy())
                                .sortOrder(f.getSortOrder() == null ? "" : f.getSortOrder())
                                .build();
        }
}