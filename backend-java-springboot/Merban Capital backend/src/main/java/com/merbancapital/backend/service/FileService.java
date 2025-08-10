package com.merbancapital.backend.service;

import org.springframework.core.io.*;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.nio.file.*;
import java.util.stream.*;

@Service
public class FileService {
    private final Path root = Paths.get("uploads"); // folder where OCR script drops/reads files

    public FileService() throws IOException {
        if (!Files.exists(root)) Files.createDirectories(root);
    }

    // Save an uploaded file
    public String store(MultipartFile file) throws IOException {
        String filename = StringUtils.cleanPath(file.getOriginalFilename());
        Path target = root.resolve(filename);
        Files.copy(file.getInputStream(), target, StandardCopyOption.REPLACE_EXISTING);
        return filename;
    }

    // List all files
    public Stream<Path> listFiles() throws IOException {
        return Files.list(root);
    }

    // Load a single file as Resource
    public Resource loadAsResource(String filename) throws IOException {
        Path file = root.resolve(filename);
        Resource resource = new UrlResource(file.toUri());
        if (resource.exists() || resource.isReadable()) return resource;
        else throw new FileNotFoundException("Could not read file: " + filename);
    }
}
