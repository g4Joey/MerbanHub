package com.merbancapital.backend.controller;

import com.merbancapital.backend.service.FileService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.List;
import java.util.stream.Collectors;
import java.nio.file.Path;


@RestController
@RequestMapping("/api/files")
@CrossOrigin(origins = "*")
public class FileController {

    @Autowired
    private FileService fileService;

    String uploadDir = System.getProperty("user.dir") + File.separator + "incoming-scan";
    File folder;
    {
        folder = new File(uploadDir);
        if (!folder.exists()) {
            folder.mkdirs(); // Creates the directory along with any needed parent directories
        }  // Ensure the upload directory exists
        folder = new File(uploadDir);
    }

    // 1) Upload endpoint (called by your OCR script)
    @PostMapping("/upload")
    public ResponseEntity<String> uploadFile(@RequestParam("file") MultipartFile file) throws IOException {

        try {
            // STEP 1: Define upload path
            String uploadDir = System.getProperty("user.dir") + File.separator + "incoming-scan";

            // STEP 2: Ensure directory exists
            File folder = new File(uploadDir);
            if (!folder.exists()) {
                folder.mkdirs(); // Create the directory if it doesn't exist
            }

            // Save the file to that directory
            Path filePath = Paths.get(uploadDir, file.getOriginalFilename());
            Files.copy(file.getInputStream(), filePath, StandardCopyOption.REPLACE_EXISTING);
            // STEP 3: Log the upload
            System.out.println("[BACKEND] Received file from OCR: " + file.getOriginalFilename()); // DEBUG LINE
            return ResponseEntity.ok("File uploaded to: " + filePath.toString());

        } catch (IOException e) {
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Upload failed.");
        }



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

