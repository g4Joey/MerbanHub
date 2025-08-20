package com.merbancapital.backend.controller;

import com.merbancapital.backend.service.FileService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;


@RestController
@RequestMapping("/api/files")
@CrossOrigin(origins = "*")
public class FileController {

    @Autowired
    private FileService fileService;

    @Value("${ocr.base.path}")
    private String ocrBasePath;

    // 1) Upload endpoint (called by your OCR script)
     @PostMapping("/upload")
    public ResponseEntity<String> uploadFile(@RequestParam("file") MultipartFile file) throws IOException {
        // Delegate storage to FileService so uploads and listing use the same directory
        String stored;
        try {
            stored = fileService.store(file);
        } catch (IOException e) {
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Upload failed.");
        }
        // stored now contains the absolute path where the file was saved
        logUploaded(file.getOriginalFilename(), stored);
        return ResponseEntity.ok("File uploaded to: " + stored);
    }

    // small helper to centralize debug logging for uploads
    private void logUploaded(String originalName, String savedPath) {
        System.out.println("[BACKEND] Received file for OCR: " + originalName + " -> " + savedPath);
    }


    // 2) List endpoint (called by frontend)
    @GetMapping("/list")
    public ResponseEntity<List<String>> listFiles() throws IOException {
        List<String> files = fileService.listIndexedFiles()
                .map(Path::getFileName)
                .map(Object::toString)
                .collect(Collectors.toList());
        return ResponseEntity.ok(files);
    }

    // 3) Download endpoint (frontend fetches file by name)
    @GetMapping("/{filename:.+}")
    public ResponseEntity<Resource> serveFile(@PathVariable String filename) throws IOException {
        Resource file = fileService.loadAsResource(filename);
        return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_OCTET_STREAM)
                .header(HttpHeaders.CONTENT_DISPOSITION,
                        "attachment; filename=\"" + file.getFilename() + "\"")
                .body(file);
    }
}

