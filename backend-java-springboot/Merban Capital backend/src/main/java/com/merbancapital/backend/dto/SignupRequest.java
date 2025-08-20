package com.merbancapital.backend.dto;

import jakarta.validation.constraints.*;
import java.util.Set;

public class SignupRequest {
    @NotBlank @Size(min = 3, max = 20)
    private String username;

    @NotBlank @Email
    private String email;

    @NotBlank @Size(min = 6, max = 40)
    private String password;

    @NotNull
    private Integer departmentId;  // Changed from Long to Integer

    @NotEmpty
    private Set<String> roles;

    // getters & setters
    public String getUsername() { return username; }
    public void setUsername(String u) { this.username = u; }
    public String getEmail() { return email; }
    public void setEmail(String e) { this.email = e; }
    public String getPassword() { return password; }
    public void setPassword(String p) { this.password = p; }
    public Integer getDepartmentId() { return departmentId; }  // Changed return type
    public void setDepartmentId(Integer d) { this.departmentId = d; }  // Changed parameter type
    public Set<String> getRoles() { return roles; }
    public void setRoles(Set<String> r) { this.roles = r; }
}