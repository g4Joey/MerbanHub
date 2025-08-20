package com.merbancapital.backend.model;

import jakarta.persistence.*;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "clients")
public class Client {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "client_id")
    private Integer clientId;  // Changed to Integer to match database schema

    @Column(name = "full_name", nullable = false)
    private String fullName;

    @Column(name = "account_number", nullable = false, unique = true, length = 8)
    private String accountNumber;

    @OneToMany(mappedBy = "client", cascade = CascadeType.ALL)
    private List<Document> documents = new ArrayList<>();

    // Constructors
    public Client() {
    }

    public Client(String fullName, String accountNumber) {
        this.fullName = fullName;
        this.accountNumber = accountNumber;
    }

    // Getters and Setters
    public Integer getClientId() {
        return clientId;
    }

    public void setClientId(Integer clientId) {
        this.clientId = clientId;
    }

    public String getFullName() {
        return fullName;
    }

    public void setFullName(String fullName) {
        this.fullName = fullName;
    }

    public String getAccountNumber() {
        return accountNumber;
    }

    public void setAccountNumber(String accountNumber) {
        this.accountNumber = accountNumber;
    }

    public List<Document> getDocuments() {
        return documents;
    }

    public void setDocuments(List<Document> documents) {
        this.documents = documents;
    }
}