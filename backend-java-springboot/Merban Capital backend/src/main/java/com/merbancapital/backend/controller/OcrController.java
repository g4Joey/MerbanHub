package com.merbancapital.backend.controller;

import com.merbancapital.backend.dto.OcrMetadata;
import com.merbancapital.backend.service.FileService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;
import java.util.HashMap;

@RestController
@RequestMapping("/api/ocr")
@CrossOrigin(origins = "*")
public class OcrController {

    private final Logger log = LoggerFactory.getLogger(OcrController.class);
    
    @Autowired
    private FileService fileService;

    @PostMapping("/notify")
    public OcrMetadata receiveMetadata(@RequestBody OcrMetadata meta) {
        log.info("Received OCR metadata: {}", meta);
        // TODO: later, save to DB or index
        return meta;
    }
    
    @PostMapping("/upload")
    public ResponseEntity<Map<String, Object>> uploadForOcr(@RequestParam("file") MultipartFile file) {
        try {
            log.info("Received file upload for OCR processing: {}", file.getOriginalFilename());
            
            // Upload directly to OCR microservice
            Map<String, Object> result = fileService.uploadToOcrService(file);
            
            if (result.containsKey("error")) {
                return ResponseEntity.badRequest().body(result);
            }
            
            return ResponseEntity.ok(result);
            
        } catch (Exception e) {
            log.error("Error processing file upload for OCR: {}", e.getMessage(), e);
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("error", e.getMessage());
            return ResponseEntity.internalServerError().body(errorResult);
        }
    }
    
    @PostMapping("/trigger")
    public ResponseEntity<Map<String, Object>> triggerOcrProcessing() {
        try {
            log.info("Manual OCR processing trigger requested");
            
            Map<String, Object> result = new HashMap<>();
            result.put("message", "OCR processing triggered");
            result.put("status", "success");
            
            return ResponseEntity.ok(result);
            
        } catch (Exception e) {
            log.error("Error triggering OCR processing: {}", e.getMessage(), e);
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("error", e.getMessage());
            return ResponseEntity.internalServerError().body(errorResult);
        }
    }
    
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getOcrStats() {
        try {
            Map<String, Object> stats = fileService.getOcrStats();
            return ResponseEntity.ok(stats);
        } catch (Exception e) {
            log.error("Error getting OCR stats: {}", e.getMessage(), e);
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("error", e.getMessage());
            return ResponseEntity.internalServerError().body(errorResult);
        }
    }
    
    @GetMapping("/search")
    public ResponseEntity<Map<String, Object>> searchOcrFiles(@RequestParam("q") String query) {
        try {
            Map<String, Object> results = fileService.searchOcrFiles(query);
            return ResponseEntity.ok(results);
        } catch (Exception e) {
            log.error("Error searching OCR files: {}", e.getMessage(), e);
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("error", e.getMessage());
            return ResponseEntity.internalServerError().body(errorResult);
        }
    }
}
