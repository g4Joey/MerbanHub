package com.merbancapital.backend.service;

import org.springframework.core.io.*;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.beans.factory.annotation.Value;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.nio.file.*;
import java.util.stream.*;

@Service
public class FileService {
    private static final Logger log = LoggerFactory.getLogger(FileService.class);
    // We keep three important folders under the OCR base path:
    //  - incoming-scan  (where uploads are stored and OCR watcher reads from)
    //  - fully_indexed  (OCR succeeded -> permanent storage for searchable files)
    //  - partially_indexed (OCR partially succeeded -> searchable by frontend)
    //  - failed (OCR failed -> not searched by frontend)
    private final Path incomingRoot; // ocrBasePath/incoming-scan
    private final Path fullyIndexedRoot; // ocrBasePath/fully_indexed
    private final Path partiallyIndexedRoot; // ocrBasePath/partially_indexed
    private final Path failedRoot; // ocrBasePath/failed

    public FileService(@Value("${ocr.base.path}") String ocrBasePath) throws IOException {
        Path base = Paths.get(ocrBasePath);
        this.incomingRoot = base.resolve("incoming-scan");
        this.fullyIndexedRoot = base.resolve("fully_indexed");
        this.partiallyIndexedRoot = base.resolve("partially_indexed");
        this.failedRoot = base.resolve("failed");

    // Ensure directories exist on startup
        if (!Files.exists(incomingRoot)) Files.createDirectories(incomingRoot);
        if (!Files.exists(fullyIndexedRoot)) Files.createDirectories(fullyIndexedRoot);
        if (!Files.exists(partiallyIndexedRoot)) Files.createDirectories(partiallyIndexedRoot);
        if (!Files.exists(failedRoot)) Files.createDirectories(failedRoot);

    // Log the resolved paths so they are visible in Spring Boot logs for debugging
    log.info("OCR base path resolved to: {}", base.toAbsolutePath());
    log.info("Incoming scan folder: {}", incomingRoot.toAbsolutePath());
    log.info("Fully indexed folder: {}", fullyIndexedRoot.toAbsolutePath());
    log.info("Partially indexed folder: {}", partiallyIndexedRoot.toAbsolutePath());
    log.info("Failed folder: {}", failedRoot.toAbsolutePath());
    }

    // Save an uploaded file
    public String store(MultipartFile file) throws IOException {
        String original = file.getOriginalFilename();
        if (original == null || original.trim().isEmpty()) {
            original = "upload-" + System.currentTimeMillis();
        }
        String filename = StringUtils.cleanPath(original);
        // Store uploads to the incoming-scan folder (OCR watcher will pick them up)
        Path target = incomingRoot.resolve(filename);
        // Ensure parent exists (defensive)
        if (!Files.exists(target.getParent())) {
            Files.createDirectories(target.getParent());
        }
        log.info("Saving uploaded file '{}' to {}", filename, target.toAbsolutePath());
        Files.copy(file.getInputStream(), target, StandardCopyOption.REPLACE_EXISTING);
        log.info("Saved uploaded file to {}", target.toAbsolutePath());
        // Return the absolute path where the file was saved to make debugging easier
        return target.toAbsolutePath().toString();
    }

    // List all files
    /**
     * Return a combined stream of files located in the folders that are
     * considered searchable by the frontend: fully_indexed and partially_indexed.
     * Files in `failed` are intentionally excluded.
     */
    public Stream<Path> listIndexedFiles() throws IOException {
        Stream<Path> fully = Files.list(fullyIndexedRoot).filter(Files::isRegularFile);
        Stream<Path> partial = Files.list(partiallyIndexedRoot).filter(Files::isRegularFile);
        return Stream.concat(fully, partial);
    }

    // Load a single file as Resource
    public Resource loadAsResource(String filename) throws IOException {
        // Try to locate the file in the indexed folders first (frontend search targets these),
        // then fall back to incoming-scan. This makes downloads resilient regardless of where the file lives.
        Path[] candidates = new Path[] {
                fullyIndexedRoot.resolve(filename),
                partiallyIndexedRoot.resolve(filename),
                incomingRoot.resolve(filename)
        };

        for (Path p : candidates) {
            Resource resource = new UrlResource(p.toUri());
            if (resource.exists() && resource.isReadable()) return resource;
        }
        throw new FileNotFoundException("Could not read file: " + filename);
    }

    /**
     * Check whether a stored file path (absolute path or filename) exists in one of the
     * searchable/indexed folders: fully_indexed or partially_indexed.
     * This is used by DocumentService to restrict search results to files the frontend
     * should see.
     */
    public boolean isFileInIndexed(String filePath) throws IOException {
        if (filePath == null || filePath.isBlank()) return false;

        Path candidate = Paths.get(filePath);
        // If given an absolute path, check whether it resides under one of the indexed roots
        if (candidate.isAbsolute()) {
            Path norm = candidate.normalize();
            if (norm.startsWith(fullyIndexedRoot) || norm.startsWith(partiallyIndexedRoot)) return true;
            // If absolute but not under the indexed roots, still check whether the exact file exists in indexed folders by name
            candidate = candidate.getFileName();
            if (candidate == null) return false;
        }

        // Treat candidate as filename and check existence in indexed folders
        Path byNameFully = fullyIndexedRoot.resolve(candidate.getFileName());
        Path byNamePartial = partiallyIndexedRoot.resolve(candidate.getFileName());
        return Files.exists(byNameFully) || Files.exists(byNamePartial);
    }
}
