package com.merbancapital.backend.model;

import jakarta.persistence.*;

@Entity
@Table(name = "roles")
public class Role {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    // e.g. "ROLE_ADMIN", "ROLE_USER"
    @Column(length = 50, unique = true, nullable = false)
    private String name;

    public Role(String authority) {
        this.name = authority;
    }

    public Role() {
        // Default constructor for JPA
    }

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
}
