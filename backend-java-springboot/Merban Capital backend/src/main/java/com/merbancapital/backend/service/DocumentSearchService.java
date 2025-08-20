package com.merbancapital.backend.service;

import com.merbancapital.backend.dto.SearchFilters;
import com.merbancapital.backend.dto.SearchResponse;
import com.merbancapital.backend.model.Document;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Value;

import jakarta.annotation.PostConstruct;
import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.time.Instant;
import java.util.*;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.Stream;

@Service
public class DocumentSearchService {

        private List<Document> documents = Collections.synchronizedList(new ArrayList<>());

        @Value("${ocr.base.path:uploads}")
        private String ocrBasePath;




        private static final String FULLY_INDEXED_DIR = "fully_indexed";
        private static final String PARTIALLY_INDEXED_DIR = "partially_indexed";

        @PostConstruct
        public void init() {
                System.out.println("[DocumentSearchService] Initializing with OCR base path: " + ocrBasePath);
                scanOcrFolders();
        }

        public void scanOcrFolders() {
                List<Document> newDocuments = new ArrayList<>();
                List<Path> directoriesToScan = List.of(
                                Paths.get(ocrBasePath, FULLY_INDEXED_DIR),
                                Paths.get(ocrBasePath, PARTIALLY_INDEXED_DIR));
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
                                                                        Document doc = new Document();
                                                                        doc.setFileName(fileName);
                                                                        doc.setFileSize(fileSize);
                                                                        doc.setDateModified(Instant.ofEpochMilli(lastModified));
                                                                        doc.setFilePath(absolutePath);
                                                                        // fileExtension extraction
                                                                        int idx = fileName.lastIndexOf('.');
                                                                        if (idx >= 0) doc.setFileExtension(fileName.substring(idx));
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
                // Simple name-based filter (template matched clientName against filename)
                if (f.getClientName() != null && !f.getClientName().isBlank()) {
                        String q = f.getClientName().toLowerCase();
                        filtered = filtered.stream()
                                        .filter(d -> d.getFileName() != null && d.getFileName().toLowerCase().contains(q))
                                        .collect(Collectors.toList());
                }

                // If an account number is provided, perform numeric-only matching.
                // Extract digits from the provided filter; if there are no digits, skip account-number filtering.
                if (f.getAccountNumber() != null && !f.getAccountNumber().isBlank()) {
                        String digitsOnly = f.getAccountNumber().replaceAll("\\D+", "");
                        if (!digitsOnly.isEmpty()) {
                                final String acc = digitsOnly; // do not lowercase digits
                                filtered = filtered.stream()
                                                .filter(d -> {
                                                        if (d.getFileName() == null) return false;
                                                        // Extract digits from filename and check contains
                                                        String fileDigits = d.getFileName().replaceAll("\\D+", "");
                                                        return fileDigits.contains(acc);
                                                })
                                                .collect(Collectors.toList());
                        } // else: query had no digits -> ignore accountNumber filter
                }

                // Pagination
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

        /**
         * Find an indexed file by exact filename (case-insensitive) inside
         * fully_indexed or partially_indexed. Returns an Optional<Path> when found.
         */
        public Optional<Path> findFileInIndexedFolders(String filename) {
                if (filename == null || filename.isBlank()) return Optional.empty();
                String safeName = Paths.get(filename).getFileName().toString();

                Path p1 = Paths.get(ocrBasePath, FULLY_INDEXED_DIR, safeName);
                if (Files.exists(p1) && Files.isRegularFile(p1)) return Optional.of(p1);

                Path p2 = Paths.get(ocrBasePath, PARTIALLY_INDEXED_DIR, safeName);
                if (Files.exists(p2) && Files.isRegularFile(p2)) return Optional.of(p2);

                // Try case-insensitive search in the two directories
                List<Path> dirs = List.of(
                                Paths.get(ocrBasePath, FULLY_INDEXED_DIR),
                                Paths.get(ocrBasePath, PARTIALLY_INDEXED_DIR));
                for (Path dir : dirs) {
                        if (Files.exists(dir) && Files.isDirectory(dir)) {
                                try (Stream<Path> s = Files.list(dir)) {
                                        Optional<Path> found = s.filter(Files::isRegularFile)
                                                        .filter(pp -> pp.getFileName().toString().equalsIgnoreCase(safeName))
                                                        .findFirst();
                                        if (found.isPresent()) return found;
                                } catch (IOException e) {
                                        // ignore and continue
                                }
                        }
                }

                return Optional.empty();
        }
}
