package com.merbancapital.backend.service;

import com.merbancapital.backend.dto.SearchFilters;
import com.merbancapital.backend.dto.SearchResponse;
import com.merbancapital.backend.model.Document;
import com.merbancapital.backend.repository.DocumentRepository;
import org.springframework.core.io.Resource;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.List;

@Service
public class DocumentService {

    @Autowired
    private DocumentRepository documentRepository;

    @Autowired
    private FileService fileService;

    /** 1) Search/filter documents in the DB */
    public SearchResponse search(SearchFilters filters) {
        // TODO: translate SearchFilters into a JPA query (or Criteria API)
        // For now, fetch all and filter in memory:
        List<Document> all = documentRepository.findAll();
        // ... apply filters.clientName, accountNumber, etc. ...
        // build and return a SearchResponse
        return SearchResponse.builder()
                .documents(all)
                .total(all.size())
                .page(1)
                .pageSize(all.size())
                .totalPages(1)
                .build();
    }

    /** 2) Load a single document’s metadata */
    public Document getById(Long id) {
        return documentRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Document not found: " + id));
    }

    /** 3) Load the file contents as a Resource */
    public Resource loadAsResource(Long id) throws IOException {
        Document doc = getById(id);
        // filePath holds the absolute path on disk
        String filename = Paths.get(doc.getFilePath()).getFileName().toString();
        return fileService.loadAsResource(filename);
    }

    /** 4a) List all department names */
    public List<String> getAllDepartments() {
        // TODO: wire in a DepartmentRepository and return .findAll().stream().map(Department::getName)
        throw new UnsupportedOperationException("Implement via DepartmentRepository");
    }

    /** 4b) Search clients by a prefix */
    public List<String> findClients(String query, int limit) {
        // TODO: wire in a ClientRepository and call something like findByFullNameContainingIgnoreCase
        throw new UnsupportedOperationException("Implement via ClientRepository");
    }

    /** 4c) Count documents per file extension */
    public List<ExtensionCount> getExtensionCounts() {
        // TODO: use a custom @Query in DocumentRepository to group by fileExtension
        throw new UnsupportedOperationException("Implement via DocumentRepository custom query");
    }

    /** Simple DTO for extension counts */
    public static class ExtensionCount {
        private final String extension;
        private final long count;
        public ExtensionCount(String extension, long count) {
            this.extension = extension;
            this.count = count;
        }
        public String getExtension() { return extension; }
        public long getCount() { return count; }
    }
}
