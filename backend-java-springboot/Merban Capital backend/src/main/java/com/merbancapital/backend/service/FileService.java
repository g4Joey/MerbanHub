package com.merbancapital.backend.service;

import org.springframework.core.io.*;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.nio.file.*;
import java.util.stream.*;
import java.util.Map;
import java.util.HashMap;

@Service
public class FileService {
    private static final Logger log = LoggerFactory.getLogger(FileService.class);
    
    private final Path incomingRoot;
    private final Path fullyIndexedRoot;
    private final Path partiallyIndexedRoot;
    private final Path failedRoot;
    
    private final RestTemplate restTemplate;
    private final String ocrServiceUrl;

    public FileService(@Value("${ocr.base.path}") String ocrBasePath,
                      @Value("${ocr.service.url:http://localhost:8000}") String ocrServiceUrl) throws IOException {
        Path base = Paths.get(ocrBasePath);
        this.incomingRoot = base.resolve("incoming-scan");
        this.fullyIndexedRoot = base.resolve("fully_indexed");
        this.partiallyIndexedRoot = base.resolve("partially_indexed");
        this.failedRoot = base.resolve("failed");
        
        this.restTemplate = new RestTemplate();
        this.ocrServiceUrl = ocrServiceUrl;

        // Ensure directories exist on startup
        if (!Files.exists(incomingRoot)) Files.createDirectories(incomingRoot);
        if (!Files.exists(fullyIndexedRoot)) Files.createDirectories(fullyIndexedRoot);
        if (!Files.exists(partiallyIndexedRoot)) Files.createDirectories(partiallyIndexedRoot);
        if (!Files.exists(failedRoot)) Files.createDirectories(failedRoot);

        // Log the resolved paths
        log.info("OCR base path resolved to: {}", base.toAbsolutePath());
        log.info("Incoming scan folder: {}", incomingRoot.toAbsolutePath());
        log.info("Fully indexed folder: {}", fullyIndexedRoot.toAbsolutePath());
        log.info("Partially indexed folder: {}", partiallyIndexedRoot.toAbsolutePath());
        log.info("Failed folder: {}", failedRoot.toAbsolutePath());
        log.info("OCR Service URL: {}", ocrServiceUrl);
    }

    // Save an uploaded file and trigger OCR processing
    public String store(MultipartFile file) throws IOException {
        String original = file.getOriginalFilename();
        if (original == null || original.trim().isEmpty()) {
            original = "upload-" + System.currentTimeMillis();
        }
        String filename = StringUtils.cleanPath(original);
        
        // Store uploads to the incoming-scan folder
        Path target = incomingRoot.resolve(filename);
        
        // Handle duplicate filenames
        if (Files.exists(target)) {
            String baseName = filename.substring(0, filename.lastIndexOf('.'));
            String extension = filename.substring(filename.lastIndexOf('.'));
            int counter = 1;
            do {
                filename = baseName + "_" + counter + extension;
                target = incomingRoot.resolve(filename);
                counter++;
            } while (Files.exists(target));
        }
        
        // Ensure parent exists
        if (!Files.exists(target.getParent())) {
            Files.createDirectories(target.getParent());
        }
        
        log.info("Saving uploaded file '{}' to {}", filename, target.toAbsolutePath());
        Files.copy(file.getInputStream(), target, StandardCopyOption.REPLACE_EXISTING);
        log.info("Saved uploaded file to {}", target.toAbsolutePath());
        
        // Trigger OCR processing via microservice
        triggerOcrProcessing();
        
        return target.toAbsolutePath().toString();
    }
    
    // Upload file directly to OCR microservice
    public Map<String, Object> uploadToOcrService(MultipartFile file) {
        try {
            // Prepare multipart request
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);
            
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("file", new MultipartInputStreamFileResource(file.getInputStream(), file.getOriginalFilename()));
            
            HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
            
            // Send to OCR microservice
            String uploadUrl = ocrServiceUrl + "/upload";
            log.info("Uploading file '{}' to OCR service at {}", file.getOriginalFilename(), uploadUrl);
            
            ResponseEntity<Map> response = restTemplate.postForEntity(uploadUrl, requestEntity, Map.class);
            
            if (response.getStatusCode().is2xxSuccessful()) {
                log.info("Successfully uploaded file to OCR service: {}", response.getBody());
                return response.getBody();
            } else {
                log.error("Failed to upload to OCR service. Status: {}", response.getStatusCode());
                Map<String, Object> errorResult = new HashMap<>();
                errorResult.put("error", "Upload to OCR service failed");
                errorResult.put("status", response.getStatusCode());
                return errorResult;
            }
            
        } catch (Exception e) {
            log.error("Error uploading file to OCR service: {}", e.getMessage(), e);
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("error", e.getMessage());
            return errorResult;
        }
    }
    
    // Trigger OCR processing
    private void triggerOcrProcessing() {
        try {
            String triggerUrl = ocrServiceUrl + "/trigger-ocr";
            log.info("Triggering OCR processing at {}", triggerUrl);
            
            ResponseEntity<Map> response = restTemplate.postForEntity(triggerUrl, null, Map.class);
            
            if (response.getStatusCode().is2xxSuccessful()) {
                log.info("OCR processing triggered successfully: {}", response.getBody());
            } else {
                log.warn("OCR trigger returned non-success status: {}", response.getStatusCode());
            }
        } catch (Exception e) {
            log.error("Failed to trigger OCR processing: {}", e.getMessage());
            // Don't throw exception as file upload was successful
        }
    }
    
    // Get OCR service status
    public Map<String, Object> getOcrStats() {
        try {
            String statsUrl = ocrServiceUrl + "/stats";
            ResponseEntity<Map> response = restTemplate.getForEntity(statsUrl, Map.class);
            
            if (response.getStatusCode().is2xxSuccessful()) {
                return response.getBody();
            } else {
                Map<String, Object> errorResult = new HashMap<>();
                errorResult.put("error", "Failed to get OCR stats");
                return errorResult;
            }
        } catch (Exception e) {
            log.error("Error getting OCR stats: {}", e.getMessage());
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("error", e.getMessage());
            return errorResult;
        }
    }
    
    // Search processed files via OCR service
    public Map<String, Object> searchOcrFiles(String query) {
        try {
            String searchUrl = ocrServiceUrl + "/search?q=" + query;
            ResponseEntity<Map> response = restTemplate.getForEntity(searchUrl, Map.class);
            
            if (response.getStatusCode().is2xxSuccessful()) {
                return response.getBody();
            } else {
                Map<String, Object> errorResult = new HashMap<>();
                errorResult.put("error", "Search failed");
                return errorResult;
            }
        } catch (Exception e) {
            log.error("Error searching OCR files: {}", e.getMessage());
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("error", e.getMessage());
            return errorResult;
        }
    }

    // List all files
    public Stream<Path> listIndexedFiles() throws IOException {
        Stream<Path> fully = Files.list(fullyIndexedRoot).filter(Files::isRegularFile);
        Stream<Path> partial = Files.list(partiallyIndexedRoot).filter(Files::isRegularFile);
        return Stream.concat(fully, partial);
    }

    // Load a single file as Resource
    public Resource loadAsResource(String filename) throws IOException {
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

    public boolean isFileInIndexed(String filePath) throws IOException {
        if (filePath == null || filePath.isBlank()) return false;

        Path candidate = Paths.get(filePath);
        if (candidate.isAbsolute()) {
            Path norm = candidate.normalize();
            if (norm.startsWith(fullyIndexedRoot) || norm.startsWith(partiallyIndexedRoot)) return true;
            candidate = candidate.getFileName();
            if (candidate == null) return false;
        }

        Path byNameFully = fullyIndexedRoot.resolve(candidate.getFileName());
        Path byNamePartial = partiallyIndexedRoot.resolve(candidate.getFileName());
        return Files.exists(byNameFully) || Files.exists(byNamePartial);
    }
    
    // Helper class for multipart file resource
    private static class MultipartInputStreamFileResource extends InputStreamResource {
        private final String filename;

        public MultipartInputStreamFileResource(InputStream inputStream, String filename) {
            super(inputStream);
            this.filename = filename;
        }

        @Override
        public String getFilename() {
            return this.filename;
        }

        @Override
        public long contentLength() throws IOException {
            return -1; // Unknown length
        }
    }
}
