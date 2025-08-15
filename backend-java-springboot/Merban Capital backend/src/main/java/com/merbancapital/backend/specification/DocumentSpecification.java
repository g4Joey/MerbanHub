package com.merbancapital.backend.specification;

import com.merbancapital.backend.dto.SearchFilters;
import com.merbancapital.backend.model.Document;
import jakarta.persistence.criteria.*;
import org.springframework.data.jpa.domain.Specification;

import java.util.ArrayList;
import java.util.List;

public class DocumentSpecification {

    public static Specification<Document> build(SearchFilters filters) {
        return (Root<Document> root, CriteriaQuery<?> query, CriteriaBuilder cb) -> {
            List<Predicate> predicates = new ArrayList<>();

            if (filters.getClientName() != null && !filters.getClientName().isBlank()) {
                predicates.add(cb.like(cb.lower(root.get("client").get("fullName")), "%" + filters.getClientName().toLowerCase() + "%"));
            }

            if (filters.getAccountNumber() != null && !filters.getAccountNumber().isBlank()) {
                predicates.add(cb.like(cb.lower(root.get("client").get("accountNumber")), "%" + filters.getAccountNumber().toLowerCase() + "%"));
            }

            if (filters.getDepartment() != null && !filters.getDepartment().isBlank()) {
                predicates.add(cb.like(cb.lower(root.get("department").get("name")), "%" + filters.getDepartment().toLowerCase() + "%"));
            }

            if (filters.getFundDateStart() != null) {
                predicates.add(cb.greaterThanOrEqualTo(root.get("fundDate"), filters.getFundDateStart()));
            }

            if (filters.getFundDateEnd() != null) {
                predicates.add(cb.lessThanOrEqualTo(root.get("fundDate"), filters.getFundDateEnd()));
            }

            if (filters.getFileSizeMin() != null) {
                predicates.add(cb.greaterThanOrEqualTo(root.get("fileSize"), filters.getFileSizeMin()));
            }

            if (filters.getFileSizeMax() != null) {
                predicates.add(cb.lessThanOrEqualTo(root.get("fileSize"), filters.getFileSizeMax()));
            }

            if (filters.getDateModifiedStart() != null) {
                predicates.add(cb.greaterThanOrEqualTo(root.get("dateModified"), filters.getDateModifiedStart().atStartOfDay()));
            }

            if (filters.getDateModifiedEnd() != null) {
                predicates.add(cb.lessThanOrEqualTo(root.get("dateModified"), filters.getDateModifiedEnd().atTime(23, 59, 59)));
            }

            if (filters.getIndexStatus() != null && !filters.getIndexStatus().isBlank()) {
                predicates.add(cb.equal(root.get("indexStatus"), filters.getIndexStatus()));
            }

            if (filters.getOcrConfidenceMin() != null) {
                predicates.add(cb.greaterThanOrEqualTo(root.get("ocrConfidence"), filters.getOcrConfidenceMin()));
            }

            if (filters.getFileExtensions() != null && !filters.getFileExtensions().isEmpty()) {
                predicates.add(root.get("fileExtension").in(filters.getFileExtensions()));
            }

            if (filters.getFullTextSearch() != null && !filters.getFullTextSearch().isBlank()) {
                predicates.add(cb.like(cb.lower(root.get("snippet")), "%" + filters.getFullTextSearch().toLowerCase() + "%"));
            }

// Java
// Inside the build(SearchFilters filters) method, where you collect predicates:
String account = filters.getAccountNumber();
if (account != null && !account.isBlank()) {
    // If accountNumber is on Client: join and compare
    var clientJoin = root.join("client", jakarta.persistence.criteria.JoinType.LEFT);
    predicates.add(cb.equal(clientJoin.get("accountNumber"), account.trim()));

    // If accountNumber is on Document instead, use this line instead of the join:
    // predicates.add(cb.equal(root.get("accountNumber"), account.trim()));
}

            return cb.and(predicates.toArray(new Predicate[0]));
        };
    }
}