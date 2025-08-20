package com.merbancapital.backend.model;

import jakarta.persistence.*;

@Entity
@Table(name = "departments")
public class Department {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "department_id")
    private Integer departmentId;  // Changed from Long to Integer

    @Column(name = "name", nullable = false, unique = true, length = 100)
    private String name;

    public Department() {
    }

    public Department(String name) {
        this.name = name;
    }

    public Integer getDepartmentId() {  // Changed return type
        return departmentId;
    }

    public void setDepartmentId(Integer departmentId) {  // Changed parameter type
        this.departmentId = departmentId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    // Remove getId() method as it's redundant now that departmentId is already Integer
}