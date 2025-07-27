package com.murbancapital.backend.controller;

import com.murbancapital.backend.service.FileService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;
import java.nio.file.Path;


@RestController
@RequestMapping("/api/files")
@CrossOrigin(origins = "*")
public class FileController {

    @Autowired
    private FileService fileService;

    // 1) Upload endpoint (called by your OCR script)
    @PostMapping("/upload")
    public ResponseEntity<String> uploadFile(@RequestParam("file") MultipartFile file) throws IOException {
        String filename = fileService.store(file);
        System.out.println("[BACKEND] Received file from OCR: " + filename); // DEBUG LINE
        return ResponseEntity.ok("Uploaded: " + filename);
    }

    // 2) List endpoint (called by frontend)
    @GetMapping("/list")
    public ResponseEntity<List<String>> listFiles() throws IOException {
        List<String> files = fileService.listFiles()
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

