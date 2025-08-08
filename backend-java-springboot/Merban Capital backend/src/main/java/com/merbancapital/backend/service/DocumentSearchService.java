package com.merbancapital.backend.service;

import com.merbancapital.backend.dto.SearchFilters;
import com.merbancapital.backend.dto.SearchResponse;
import com.merbancapital.backend.model.Document;
import com.merbancapital.backend.repository.DocumentRepository;
import com.merbancapital.backend.specification.DocumentSpecification;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.*;
import org.springframework.stereotype.Service;

@Service
public class DocumentSearchService {

        private final DocumentRepository documentRepository;

        @Autowired
        public DocumentSearchService(DocumentRepository documentRepository) {
                this.documentRepository = documentRepository;
        }

        public SearchResponse search(SearchFilters filters) {
                // Set pagination
                int page = filters.getPage() == null ? 0 : filters.getPage() - 1;
                int pageSize = filters.getPageSize() == null ? 20 : filters.getPageSize();
                Pageable pageable = PageRequest.of(page, pageSize);

                // Apply sorting if provided
                if (filters.getSortBy() != null && !filters.getSortBy().isBlank()) {
                        Sort.Direction direction = filters.getSortOrder() != null && filters.getSortOrder().equalsIgnoreCase("desc")
                                ? Sort.Direction.DESC : Sort.Direction.ASC;
                        pageable = PageRequest.of(page, pageSize, Sort.by(direction, filters.getSortBy()));
                }

                // Search using specification
                Page<Document> resultPage = documentRepository.findAll(
                        DocumentSpecification.build(filters), pageable
                );

                // Return search response
                return SearchResponse.builder()
                        .documents(resultPage.getContent())
                        .total((int) resultPage.getTotalElements())
                        .page(page + 1)
                        .pageSize(pageSize)
                        .totalPages(resultPage.getTotalPages())
                        .clientName(filters.getClientName() == null ? "" : filters.getClientName())
                        .accountNumber(filters.getAccountNumber() == null ? "" : filters.getAccountNumber())
                        .department(filters.getDepartment() == null ? "" : filters.getDepartment())
                        .fundDateStart(filters.getFundDateStart() == null ? "" : filters.getFundDateStart().toString())
                        .fundDateEnd(filters.getFundDateEnd() == null ? "" : filters.getFundDateEnd().toString())
                        .fileExtensions(filters.getFileExtensions() == null ? null : filters.getFileExtensions())
                        .dateModifiedStart(filters.getDateModifiedStart() == null ? "" : filters.getDateModifiedStart().toString())
                        .dateModifiedEnd(filters.getDateModifiedEnd() == null ? "" : filters.getDateModifiedEnd().toString())
                        .fileSizeMin(filters.getFileSizeMin() == null ? 0L : filters.getFileSizeMin())
                        .fileSizeMax(filters.getFileSizeMax() == null ? 0L : filters.getFileSizeMax())
                        .ocrConfidenceMin(filters.getOcrConfidenceMin() == null ? 0 : filters.getOcrConfidenceMin())
                        .indexStatus(filters.getIndexStatus() == null ? "" : filters.getIndexStatus())
                        .fullTextSearch(filters.getFullTextSearch() == null ? "" : filters.getFullTextSearch())
                        .sortBy(filters.getSortBy() == null ? "" : filters.getSortBy())
                        .sortOrder(filters.getSortOrder() == null ? "" : filters.getSortOrder())
                        .build();
        }
}
