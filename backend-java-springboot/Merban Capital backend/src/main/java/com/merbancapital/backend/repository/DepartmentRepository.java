package com.merbancapital.backend.repository;

import com.merbancapital.backend.model.Department;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface DepartmentRepository extends JpaRepository<Department, Long> {
    // You can add findByNameIgnoreCase(...) here if you need
}
